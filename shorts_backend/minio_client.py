from minio import Minio
from django.conf import settings
import os
import uuid

class MinioClient:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        
        # Create bucket if not exists
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
            print(f"✅ Bucket '{self.bucket_name}' created")
    
    def upload_video(self, video_file, filename):
        """
        Upload video to MiniO and return URL
        """
        # Generate unique filename
        ext = filename.split('.')[-1]
        unique_filename = f"videos/{uuid.uuid4()}.{ext}"
        
        # Get file size
        video_file.seek(0, os.SEEK_END)
        file_size = video_file.tell()
        video_file.seek(0)
        
        # Upload
        self.client.put_object(
            self.bucket_name,
            unique_filename,
            video_file,
            length=file_size,
            content_type='video/mp4'
        )
        
        # Generate URL
        url = f"http://{settings.MINIO_ENDPOINT}/{self.bucket_name}/{unique_filename}"
        return url
    
    def upload_thumbnail(self, thumbnail_file, filename):
        """
        Upload thumbnail to MiniO and return URL
        """
        ext = filename.split('.')[-1]
        unique_filename = f"thumbnails/{uuid.uuid4()}.{ext}"
        
        thumbnail_file.seek(0, os.SEEK_END)
        file_size = thumbnail_file.tell()
        thumbnail_file.seek(0)
        
        self.client.put_object(
            self.bucket_name,
            unique_filename,
            thumbnail_file,
            length=file_size,
            content_type='image/jpeg'
        )
        
        url = f"http://{settings.MINIO_ENDPOINT}/{self.bucket_name}/{unique_filename}"
        return url