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
    Aliyun OSS Storage class for image upload handling
    Note: This class is not a complete Django Storage backend, it only provides image upload and URL retrieval functionality
    """
    
    def __init__(self, base_dir=''):
        self.base_dir = base_dir
        self.access_key_id = settings.ALIYUN_OSS.get('ACCESS_KEY_ID', '')
        self.access_key_secret = settings.ALIYUN_OSS.get('ACCESS_KEY_SECRET', '')
        self.bucket_name = settings.ALIYUN_OSS.get('BUCKET_NAME', '')
        self.endpoint = settings.ALIYUN_OSS.get('ENDPOINT', '')
        
        # Configuration validation
        if not self.access_key_id:
            print("Warning: OSS AccessKeyID not set")
        if not self.access_key_secret:
            print("Warning: OSS AccessKeySecret not set")
        if not self.bucket_name:
            print("Warning: OSS BucketName not set")
        if not self.endpoint:
            print("Warning: OSS Endpoint not set")
            
        # Check if configuration is valid
        self.valid = all([self.access_key_id, self.access_key_secret, 
                           self.bucket_name, self.endpoint])
        
        if self.valid:
            print(f"OSS storage configuration valid, connecting to bucket {self.bucket_name}")
            try:
                # Create OSS connection
                self.auth = oss2.Auth(self.access_key_id, self.access_key_secret)
                self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)
                
                # Test connection
                self.test_connection()
            except Exception as e:
                print(f"OSS connection initialization failed: {e}")
                self.valid = False
        else:
            print("OSS storage configuration invalid, will use local file system")
    
    def test_connection(self):
        """Test OSS connection"""
        try:
            # List first 5 objects in the bucket to confirm connection is working
            list_objects = list(itertools.islice(oss2.ObjectIterator(self.bucket), 5))
            print(f"OSS connection test successful, bucket contains {len(list_objects)} objects")
            return True
        except Exception as e:
            print(f"OSS connection test failed: {e}")
            return False
    
    def upload_image(self, file_obj, file_path):
        """Upload image to OSS"""
        if not self.valid:
            print("OSS configuration invalid, unable to upload image")
            return None
        
        # Build complete path
        if self.base_dir:
            full_path = os.path.join(self.base_dir, file_path)
        else:
            full_path = file_path
            
        # Upload file
        try:
            print(f"Uploading to OSS: {full_path}")
            # Reset file pointer to beginning
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
                
            # Upload file
            result = self.bucket.put_object(full_path, file_obj)
            if result.status == 200:
                url = self.get_url(full_path)
                print(f"Upload successful: {url}")
                return url
            else:
                print(f"Upload failed, status code: {result.status}")
        except Exception as e:
            print(f"Failed to upload to Aliyun OSS: {e}")
        
        return None
    
    def get_url(self, file_path):
        """Get file URL"""
        if not self.valid:
            return None
            
        # Build OSS URL
        url = f"https://{self.bucket_name}.{self.endpoint}/{file_path}"
        return url 