import os
import boto3
from PIL import Image
from io import BytesIO

# S3 クライアントの作成
s3 = boto3.client('s3')

# 生成するサムネイルのサイズ（幅, 高さ）
THUMBNAIL_SIZE = (128, 128)

def lambda_handler(event, context):
    # イベントから S3 バケット名とオブジェクトキーを取得
    for record in event.get('Records', []):
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # 既にサムネイルフォルダにある画像は処理しない
        if key.startswith("thumbnails/"):
            continue

        try:
            # S3 から画像データを取得
            response = s3.get_object(Bucket=bucket, Key=key)
            img_data = response['Body'].read()

            # Pillow を使って画像を開く
            image = Image.open(BytesIO(img_data))
            
            # サムネイル画像を生成
            image.thumbnail(THUMBNAIL_SIZE)
            
            # バッファに生成した画像を保存
            buffer = BytesIO()
            image_format = image.format if image.format else "JPEG"
            image.save(buffer, image_format)
            buffer.seek(0)
            
            # サムネイルの保存先のキーを作成（例: thumbnails/ファイル名）
            thumb_key = f"thumbnails/{os.path.basename(key)}"
            
            # S3 にサムネイルをアップロード
            s3.put_object(
                Bucket=bucket,
                Key=thumb_key,
                Body=buffer,
                ContentType=response['ContentType']
            )
            print(f"Thumbnail saved to {thumb_key}")
        except Exception as e:
            print(f"Error processing {key} from bucket {bucket}: {e}")
    
    return {"statusCode": 200, "body": "Thumbnails processed."}
