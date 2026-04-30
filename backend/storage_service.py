import os
import logging
from config import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.provider = os.environ.get("STORAGE_PROVIDER", "local").lower()
        self.s3_bucket = os.environ.get("AWS_S3_BUCKET_NAME", "aetherstore-assets")
        self.cloudfront_domain = os.environ.get("CLOUDFRONT_DOMAIN", "")

        if self.provider == "s3":
            import boto3
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=os.environ.get("AWS_REGION", "us-east-1")
            )

    def get_presigned_url(self, file_path: str, expiration_seconds: int = 3600) -> str:
        """
        Generate a pre-signed URL for downloading an asset.
        If using S3/CloudFront, it returns a secure edge-optimized URL.
        If local, it simply returns the relative path for the FastAPI static files.
        """
        if self.provider == "s3":
            try:
                if self.cloudfront_domain:
                    # In a real scenario, you'd use CloudFront signed URLs here
                    # For simplicity, we just return the direct CloudFront URL if public
                    return f"https://{self.cloudfront_domain}/{file_path}"
                else:
                    response = self.s3_client.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': self.s3_bucket, 'Key': file_path},
                        ExpiresIn=expiration_seconds
                    )
                    return response
            except Exception as e:
                logger.error(f"Error generating presigned URL: {e}")
                return file_path
        else:
            # Fallback to local static file serving
            # Assuming file_path looks like 'uploads/3d_models/file.glb'
            # and FastAPI mounts static at /static/uploads/...
            if not file_path.startswith('/'):
                file_path = '/' + file_path
            return file_path

storage_service = StorageService()
