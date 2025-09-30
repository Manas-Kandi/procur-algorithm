"""Document storage integrations (S3, Google Drive, SharePoint)."""

import logging
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

logger = logging.getLogger(__name__)


class StorageService(ABC):
    """Base class for storage services."""
    
    @abstractmethod
    def upload_file(
        self,
        file_path: str,
        destination_path: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """Upload file."""
        pass
    
    @abstractmethod
    def download_file(self, file_id: str, destination_path: str):
        """Download file."""
        pass
    
    @abstractmethod
    def delete_file(self, file_id: str):
        """Delete file."""
        pass
    
    @abstractmethod
    def list_files(self, folder_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List files."""
        pass


class S3Storage(StorageService):
    """AWS S3 storage service."""
    
    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        bucket_name: str,
        region_name: str = "us-east-1",
    ):
        """Initialize S3 storage."""
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )
        self.bucket_name = bucket_name
    
    def upload_file(
        self,
        file_path: str,
        destination_path: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """Upload file to S3."""
        try:
            extra_args = {}
            if metadata:
                extra_args["Metadata"] = metadata
            
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                destination_path,
                ExtraArgs=extra_args,
            )
            
            url = f"s3://{self.bucket_name}/{destination_path}"
            logger.info(f"Uploaded file to S3: {url}")
            return url
        except ClientError as e:
            logger.error(f"Failed to upload to S3: {e}")
            raise
    
    def download_file(self, file_id: str, destination_path: str):
        """Download file from S3."""
        try:
            self.s3_client.download_file(
                self.bucket_name,
                file_id,
                destination_path,
            )
            logger.info(f"Downloaded file from S3: {file_id}")
        except ClientError as e:
            logger.error(f"Failed to download from S3: {e}")
            raise
    
    def delete_file(self, file_id: str):
        """Delete file from S3."""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_id,
            )
            logger.info(f"Deleted file from S3: {file_id}")
        except ClientError as e:
            logger.error(f"Failed to delete from S3: {e}")
            raise
    
    def list_files(self, folder_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List files in S3."""
        try:
            params = {"Bucket": self.bucket_name}
            if folder_id:
                params["Prefix"] = folder_id
            
            response = self.s3_client.list_objects_v2(**params)
            
            files = []
            for obj in response.get("Contents", []):
                files.append({
                    "id": obj["Key"],
                    "name": obj["Key"].split("/")[-1],
                    "size": obj["Size"],
                    "modified": obj["LastModified"],
                })
            
            return files
        except ClientError as e:
            logger.error(f"Failed to list S3 files: {e}")
            raise
    
    def generate_presigned_url(
        self,
        file_id: str,
        expiration: int = 3600,
    ) -> str:
        """Generate presigned URL for file access."""
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": file_id},
                ExpiresIn=expiration,
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise


class GoogleDriveStorage(StorageService):
    """Google Drive storage service."""
    
    def __init__(self, credentials: Credentials):
        """Initialize Google Drive storage."""
        self.service = build("drive", "v3", credentials=credentials)
    
    def upload_file(
        self,
        file_path: str,
        destination_path: str,
        metadata: Optional[Dict[str, str]] = None,
        folder_id: Optional[str] = None,
    ) -> str:
        """Upload file to Google Drive."""
        try:
            file_metadata = {"name": destination_path}
            if folder_id:
                file_metadata["parents"] = [folder_id]
            if metadata:
                file_metadata["properties"] = metadata
            
            with open(file_path, "rb") as f:
                media = MediaIoBaseUpload(
                    BytesIO(f.read()),
                    mimetype="application/octet-stream",
                    resumable=True,
                )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id, webViewLink",
            ).execute()
            
            file_id = file.get("id")
            logger.info(f"Uploaded file to Google Drive: {file_id}")
            return file_id
        except Exception as e:
            logger.error(f"Failed to upload to Google Drive: {e}")
            raise
    
    def download_file(self, file_id: str, destination_path: str):
        """Download file from Google Drive."""
        try:
            request = self.service.files().get_media(fileId=file_id)
            
            with open(destination_path, "wb") as f:
                downloader = request.execute()
                f.write(downloader)
            
            logger.info(f"Downloaded file from Google Drive: {file_id}")
        except Exception as e:
            logger.error(f"Failed to download from Google Drive: {e}")
            raise
    
    def delete_file(self, file_id: str):
        """Delete file from Google Drive."""
        try:
            self.service.files().delete(fileId=file_id).execute()
            logger.info(f"Deleted file from Google Drive: {file_id}")
        except Exception as e:
            logger.error(f"Failed to delete from Google Drive: {e}")
            raise
    
    def list_files(self, folder_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List files in Google Drive."""
        try:
            query = "trashed=false"
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                fields="files(id, name, size, modifiedTime, mimeType)",
            ).execute()
            
            files = []
            for file in results.get("files", []):
                files.append({
                    "id": file["id"],
                    "name": file["name"],
                    "size": file.get("size"),
                    "modified": file["modifiedTime"],
                    "mime_type": file["mimeType"],
                })
            
            return files
        except Exception as e:
            logger.error(f"Failed to list Google Drive files: {e}")
            raise
    
    def share_file(
        self,
        file_id: str,
        email: str,
        role: str = "reader",
    ):
        """Share file with user."""
        try:
            permission = {
                "type": "user",
                "role": role,
                "emailAddress": email,
            }
            
            self.service.permissions().create(
                fileId=file_id,
                body=permission,
                sendNotificationEmail=True,
            ).execute()
            
            logger.info(f"Shared file {file_id} with {email}")
        except Exception as e:
            logger.error(f"Failed to share file: {e}")
            raise
