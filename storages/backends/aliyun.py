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
    阿里云OSS存储后端
    """
    def __init__(self, access_key_id=None, access_key_secret=None, 
                 bucket_name=None, endpoint=None, url_expire_seconds=None):
        self.access_key_id = access_key_id or settings.ALIYUN_ACCESS_KEY_ID
        self.access_key_secret = access_key_secret or settings.ALIYUN_ACCESS_KEY_SECRET
        self.bucket_name = bucket_name or settings.ALIYUN_BUCKET_NAME
        self.endpoint = endpoint or settings.ALIYUN_ENDPOINT
        self.url_expire_seconds = url_expire_seconds or getattr(
            settings, 'ALIYUN_URL_EXPIRES_IN', 60 * 60 * 24 * 365)  # 默认链接有效期1年
        
        # 验证配置是否完整
        if not (self.access_key_id and self.access_key_secret and 
                self.bucket_name and self.endpoint):
            raise ValueError(
                '阿里云OSS配置不完整，请检查ALIYUN_ACCESS_KEY_ID, ALIYUN_ACCESS_KEY_SECRET, '
                'ALIYUN_BUCKET_NAME, ALIYUN_ENDPOINT设置。'
            )
        
        # 初始化阿里云OSS
        self._auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        self._bucket = oss2.Bucket(self._auth, self.endpoint, self.bucket_name)
        self._is_setup = True
    
    def _open(self, name, mode='rb'):
        """
        从OSS下载文件并返回文件对象
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
        将文件保存到OSS
        """
        name = self._normalize_name(name)
        content.open()
        content_bytes = content.read()
        content.close()
        
        self._bucket.put_object(name, content_bytes)
        return name
    
    def delete(self, name):
        """
        从OSS删除文件
        """
        name = self._normalize_name(name)
        try:
            self._bucket.delete_object(name)
        except oss2.exceptions.NoSuchKey:
            pass
    
    def exists(self, name):
        """
        检查文件是否存在于OSS
        """
        name = self._normalize_name(name)
        try:
            return self._bucket.object_exists(name)
        except:
            return False
    
    def listdir(self, path):
        """
        列出指定路径下的所有文件和目录
        """
        path = self._normalize_name(path)
        if path and not path.endswith('/'):
            path += '/'
        
        directories, files = [], []
        for obj in oss2.ObjectIterator(self._bucket, prefix=path, delimiter='/'):
            if obj.is_prefix():  # 文件夹
                directories.append(obj.key.replace(path, '', 1).rstrip('/'))
            else:  # 文件
                files.append(obj.key.replace(path, '', 1))
        
        return directories, files
    
    def size(self, name):
        """
        返回文件大小
        """
        name = self._normalize_name(name)
        return self._bucket.get_object_meta(name).content_length
    
    def url(self, name):
        """
        返回文件的URL
        """
        name = self._normalize_name(name)
        # 生成带有过期时间的签名URL
        expiration_time = int(datetime.datetime.now().timestamp()) + self.url_expire_seconds
        return self._bucket.sign_url('GET', name, expiration_time)
    
    def get_modified_time(self, name):
        """
        返回文件的最后修改时间
        """
        name = self._normalize_name(name)
        return datetime.datetime.fromtimestamp(self._bucket.get_object_meta(name).last_modified)
    
    def get_created_time(self, name):
        """
        返回文件的创建时间（OSS不提供创建时间，返回修改时间）
        """
        return self.get_modified_time(name)
    
    def _normalize_name(self, name):
        """
        标准化文件名，确保它不以'/'开头
        """
        if name and name.startswith('/'):
            name = name[1:]
        return name 