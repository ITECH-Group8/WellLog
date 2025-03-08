import os
import datetime
import oss2
from urllib.parse import urljoin
from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

@deconstructible
class AliyunStorage(Storage):
    """
    Aliyun OSS Storage Backend
    """
    def __init__(self, access_key_id=None, access_key_secret=None, 
                 bucket_name=None, endpoint=None, url_expire_seconds=None):
        self.access_key_id = access_key_id or settings.ALIYUN_ACCESS_KEY_ID
        self.access_key_secret = access_key_secret or settings.ALIYUN_ACCESS_KEY_SECRET
        self.bucket_name = bucket_name or settings.ALIYUN_BUCKET_NAME
        self.endpoint = endpoint or settings.ALIYUN_ENDPOINT
        self.url_expire_seconds = url_expire_seconds or getattr(
            settings, 'ALIYUN_URL_EXPIRES_IN', 60 * 60 * 24 * 365)  # Default link validity: 1 year
        
        # Verify if configuration is complete
        if not (self.access_key_id and self.access_key_secret and 
                self.bucket_name and self.endpoint):
            raise ValueError(
                'Aliyun OSS configuration is incomplete, please check ALIYUN_ACCESS_KEY_ID, ALIYUN_ACCESS_KEY_SECRET, '
                'ALIYUN_BUCKET_NAME, ALIYUN_ENDPOINT settings.'
            )
        
        # Initialize Aliyun OSS
        self._auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        self._bucket = oss2.Bucket(self._auth, self.endpoint, self.bucket_name)
        self._is_setup = True
    
    def _open(self, name, mode='rb'):
        """
        Download file from OSS and return file object
        """
        from django.core.files.base import ContentFile
        name = self._normalize_name(name)
        
        try:
            content = self._bucket.get_object(name)
            return ContentFile(content.read())
        except oss2.exceptions.NoSuchKey:
            return None
    
    def _save(self, name, content):
        """
        Save file to OSS
        """
        name = self._normalize_name(name)
        content.open()
        content_bytes = content.read()
        content.close()
        
        self._bucket.put_object(name, content_bytes)
        return name
    
    def delete(self, name):
        """
        Delete file from OSS
        """
        name = self._normalize_name(name)
        try:
            self._bucket.delete_object(name)
        except oss2.exceptions.NoSuchKey:
            pass
    
    def exists(self, name):
        """
        Check if file exists in OSS
        """
        name = self._normalize_name(name)
        try:
            return self._bucket.object_exists(name)
        except:
            return False
    
    def listdir(self, path):
        """
        List all files and directories in the specified path
        """
        path = self._normalize_name(path)
        if path and not path.endswith('/'):
            path += '/'
        
        directories, files = [], []
        for obj in oss2.ObjectIterator(self._bucket, prefix=path, delimiter='/'):
            if obj.is_prefix():  # Directory
                directories.append(obj.key.replace(path, '', 1).rstrip('/'))
            else:  # File
                files.append(obj.key.replace(path, '', 1))
        
        return directories, files
    
    def size(self, name):
        """
        Return file size
        """
        name = self._normalize_name(name)
        return self._bucket.get_object_meta(name).content_length
    
    def url(self, name):
        """
        Return file URL
        """
        name = self._normalize_name(name)
        # Generate signed URL with expiration time
        expiration_time = int(datetime.datetime.now().timestamp()) + self.url_expire_seconds
        return self._bucket.sign_url('GET', name, expiration_time)
    
    def get_modified_time(self, name):
        """
        Return file's last modified time
        """
        name = self._normalize_name(name)
        return datetime.datetime.fromtimestamp(self._bucket.get_object_meta(name).last_modified)
    
    def get_created_time(self, name):
        """
        Return file's creation time (OSS does not provide creation time, returns modified time)
        """
        return self.get_modified_time(name)
    
    def _normalize_name(self, name):
        """
        Normalize filename, ensure it does not start with '/'
        """
        if name and name.startswith('/'):
            name = name[1:]
        return name 