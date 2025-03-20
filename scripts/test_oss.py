#!/usr/bin/env python
# Test Alibaba Cloud OSS connection

import os
import sys
import oss2
from pathlib import Path
from dotenv_vault import load_dotenv

script_dir = Path(__file__).parent
project_root = script_dir.parent
os.chdir(project_root)

load_dotenv()

def test_oss_connection():
    """Test Alibaba Cloud OSS connection"""
    # Get configuration information
    access_key_id = os.environ.get('ALIYUN_ACCESS_KEY_ID')
    access_key_secret = os.environ.get('ALIYUN_ACCESS_KEY_SECRET')
    bucket_name = os.environ.get('ALIYUN_BUCKET_NAME')
    endpoint = os.environ.get('ALIYUN_ENDPOINT')
    
    if not all([access_key_id, access_key_secret, bucket_name, endpoint]):
        print("Error: Incomplete environment variables. Please ensure you have set the following environment variables:")
        print("  ALIYUN_ACCESS_KEY_ID")
        print("  ALIYUN_ACCESS_KEY_SECRET")
        print("  ALIYUN_BUCKET_NAME")
        print("  ALIYUN_ENDPOINT")
        return False
    
    try:
        # Print configuration information
        print(f"Access Key ID: {access_key_id[:8]}********")
        print(f"Access Key Secret: {access_key_secret[:8]}********")
        print(f"Bucket Name: {bucket_name}")
        print(f"Endpoint: {endpoint}")
        
        # Create Auth and Bucket objects
        auth = oss2.Auth(access_key_id, access_key_secret)
        bucket = oss2.Bucket(auth, endpoint, bucket_name)
        
        # Test upload
        test_key = 'test/connection_test.txt'
        bucket.put_object(test_key, 'Hello, OSS! This is a connection test.')
        
        # Test download
        result = bucket.get_object(test_key)
        content = result.read().decode('utf-8')
        print(f"\nRead test file content: {content}")
        
        # Test listing objects
        print("\nObjects in the bucket:")
        for obj in oss2.ObjectIterator(bucket, prefix='test/', max_keys=10):
            print(f"  - {obj.key}")
        
        # Clean up
        print("\nDeleting test file...")
        bucket.delete_object(test_key)
        
        print("\n🎉 Connection test successful! Your Alibaba Cloud OSS configuration is working properly.")
        return True
    except oss2.exceptions.ServerError as e:
        print(f"\nServer error: {e}")
        if '403' in str(e):
            print("Permission error: Please check if your AccessKey has the correct permissions.")
        return False
    except oss2.exceptions.ClientError as e:
        print(f"\nClient error: {e}")
        return False
    except Exception as e:
        print(f"\nUnknown error: {e}")
        return False

if __name__ == "__main__":
    print("=== Alibaba Cloud OSS Connection Test ===")
    success = test_oss_connection()
    sys.exit(0 if success else 1) 