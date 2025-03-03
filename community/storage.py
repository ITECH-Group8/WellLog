import os
import oss2
from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from urllib.parse import urljoin
import itertools

@deconstructible
class AliyunOSSStorage:
    """
    阿里云OSS存储类，用于处理图片上传
    注意：此类不是一个完整的Django Storage后端，仅提供图片上传和URL获取功能
    """
    
    def __init__(self, base_dir=''):
        self.base_dir = base_dir
        self.access_key_id = settings.ALIYUN_OSS.get('ACCESS_KEY_ID', '')
        self.access_key_secret = settings.ALIYUN_OSS.get('ACCESS_KEY_SECRET', '')
        self.bucket_name = settings.ALIYUN_OSS.get('BUCKET_NAME', '')
        self.endpoint = settings.ALIYUN_OSS.get('ENDPOINT', '')
        
        # 配置验证
        if not self.access_key_id:
            print("警告: OSS AccessKeyID未设置")
        if not self.access_key_secret:
            print("警告: OSS AccessKeySecret未设置")
        if not self.bucket_name:
            print("警告: OSS BucketName未设置")
        if not self.endpoint:
            print("警告: OSS Endpoint未设置")
            
        # 配置是否有效
        self.valid = all([self.access_key_id, self.access_key_secret, 
                           self.bucket_name, self.endpoint])
        
        if self.valid:
            print(f"OSS存储配置有效，连接到存储桶 {self.bucket_name}")
            try:
                # 创建OSS连接
                self.auth = oss2.Auth(self.access_key_id, self.access_key_secret)
                self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)
                
                # 测试连接
                self.test_connection()
            except Exception as e:
                print(f"OSS连接初始化失败: {e}")
                self.valid = False
        else:
            print("OSS存储配置无效，将使用本地文件系统")
    
    def test_connection(self):
        """测试OSS连接"""
        try:
            # 列出存储桶中的前5个对象，确认连接是否正常
            list_objects = list(itertools.islice(oss2.ObjectIterator(self.bucket), 5))
            print(f"OSS连接测试成功，存储桶中包含{len(list_objects)}个对象")
            return True
        except Exception as e:
            print(f"OSS连接测试失败: {e}")
            return False
    
    def upload_image(self, file_obj, file_path):
        """上传图片到OSS"""
        if not self.valid:
            print("OSS配置无效，无法上传图片")
            return None
        
        # 构建完整路径
        if self.base_dir:
            full_path = os.path.join(self.base_dir, file_path)
        else:
            full_path = file_path
            
        # 上传文件
        try:
            print(f"正在上传到OSS: {full_path}")
            # 将文件指针重置到开头
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
                
            # 上传文件
            result = self.bucket.put_object(full_path, file_obj)
            if result.status == 200:
                url = self.get_url(full_path)
                print(f"上传成功: {url}")
                return url
            else:
                print(f"上传失败，状态码: {result.status}")
        except Exception as e:
            print(f"上传到阿里云OSS失败: {e}")
        
        return None
    
    def get_url(self, file_path):
        """获取文件URL"""
        if not self.valid:
            return None
            
        # 构建OSS URL
        url = f"https://{self.bucket_name}.{self.endpoint}/{file_path}"
        return url 