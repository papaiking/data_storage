import abc
import os
import datetime
import aiofiles
from sqlalchemy.future import select
from app.database import async_session, Metadata, BlobData
from app.config import settings, get_logger
import boto3
from botocore.exceptions import ClientError

logger = get_logger(__name__)

class BaseStorage(abc.ABC):
    """
    Abstract class for all medium storage
    Use template pattern to implement store and retrieve methods
    """
    @abc.abstractmethod
    async def medium_store(self, object_id: str, data: bytes) -> str:
        """
        Store object data into medium
        Return filepath
        """
        raise NotImplementedError

    async def store(self, object_id: str, data: bytes) -> Metadata:
        try:
            # Store binay data/object into medium
            file_path = await self.medium_store(object_id, data)

            # Store metadata
            size = len(data)
            meta = Metadata(
                object_id=object_id,
                size=size,
                storage_type=settings.ACTIVE_STORAGE,
                file_path=file_path
            )
            async with async_session() as session:
                session.add(meta)
                await session.commit()
                await session.refresh(meta)
            return meta
        except ClientError as e:
            logger.error(f"Error storing object {object_id} to medium storage: {e}", exc_info=True)
            raise

    @abc.abstractmethod
    async def medium_retrieve(self, object_id: str, **kwargs) -> bytes:
        """
        Retrieve binary data from medium storage and return to function
        """
        raise NotImplementedError

    async def retrieve(self, object_id: str) -> tuple[bytes, Metadata]:
        try:
            # Retrieve metadata
            async with async_session() as session:
                result = await session.execute(select(Metadata).where(Metadata.object_id == object_id))
                meta = result.scalar_one_or_none()

            if not meta:
                raise FileNotFoundError("Object metadata not found")

            # Retrieve binary data from medium storage
            data = await self.medium_retrieve(object_id, file_path=meta.file_path)
            return data, meta
        except ClientError as e:
            logger.error(f"Error in retrieving object {object_id} from medium storage: {e}", exc_info=True)
            raise

class LocalStorage(BaseStorage):
    def __init__(self, root_path: str):
        self.root_path = root_path
        os.makedirs(self.root_path, exist_ok=True)

    def _get_file_path(self, object_id: str) -> str:
        now = datetime.datetime.utcnow()
        dir_path = os.path.join(self.root_path, now.strftime("%Y/%m/%d"))
        os.makedirs(dir_path, exist_ok=True)
        return os.path.join(dir_path, object_id)

    async def medium_store(self, object_id: str, data: bytes) -> str:
        file_path = self._get_file_path(object_id)
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(data)
        except Exception as e:
            logger.error(f"Error in store object {object_id} in local: {e}", exc_info=True)
            raise

        return file_path

    async def medium_retrieve(self, object_id: str, **kwargs) -> bytes:
        """
        Retrieve object file data from local file. Read from file specified in file path.
        Return data to function
        """
        try:
            async with aiofiles.open(kwargs.get('file_path'), 'rb') as f:
                data = await f.read()
        except Exception as e:
            logger.error(f"Failed to read object file: {e}", exc_info=True)
            raise FileNotFoundError("Failed to read object file")

        return data

class DatabaseStorage(BaseStorage):
    async def medium_store(self, object_id: str, data: bytes) -> str:
        try:            
            async with async_session() as session:
                # Store blob data into databases
                blob_data = BlobData(
                    object_id=object_id,
                    data=data
                )
                session.add(blob_data)
                await session.commit()
            return
        except ClientError as e:
            logger.error(f"Error storing object {object_id} to Database storage: {e}", exc_info=True)
            raise

    async def medium_retrieve(self, object_id: str, **kwargs) -> bytes:
        try:
            async with async_session() as session:
                # Retrieve blob data
                blob_result = await session.execute(select(BlobData).where(BlobData.object_id == object_id))
                blob_data = blob_result.scalar_one_or_none()

                if not blob_data:
                    raise FileNotFoundError("Object data not found")

            return blob_data.data
        except Exception as e:
            logger.error(f"Error retrieving object {object_id} from database: {e}", exc_info=True)
            raise

class S3Storage(BaseStorage):
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION_NAME
        )
        self.bucket_name = settings.S3_BUCKET_NAME
        
        # Ensure the bucket exists
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            logger.info(f"Bucket {self.bucket_name} does not exist. Creating it.")
            self.s3_client.create_bucket(Bucket=self.bucket_name)

    async def medium_store(self, object_id: str, data: bytes) -> str:
        try:
            # S3 object key can be the object_id directly, or you can build a path
            s3_key = object_id
            self.s3_client.put_object(Bucket=self.bucket_name, Key=s3_key, Body=data)
            
            return f"s3://{self.bucket_name}/{s3_key}" # Storing S3 path in file_path
        except ClientError as e:
            logger.error(f"Error storing object {object_id} to S3: {e}", exc_info=True)
            raise

    async def medium_retrieve(self, object_id: str, **kwargs) -> bytes:
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=object_id)
            data = response['Body'].read()
            return data
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f"Object {object_id} not found in S3 bucket {self.bucket_name}")
            else:
                logger.error(f"Error retrieving object {object_id} from S3: {e}", exc_info=True)
                raise

def get_storage_backend() -> BaseStorage:
    if settings.ACTIVE_STORAGE == 'local':
        return LocalStorage(settings.LOCAL_STORAGE_PATH)
    elif settings.ACTIVE_STORAGE == 'database':
        return DatabaseStorage()
    elif settings.ACTIVE_STORAGE == 's3':
        return S3Storage()
    else:
        raise ValueError(f"Unknown storage backend, not supported: {settings.ACTIVE_STORAGE}")

