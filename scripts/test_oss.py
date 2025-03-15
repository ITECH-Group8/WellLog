#!/usr/bin/env python
# 测试阿里云OSS连接

import os
import sys
import oss2
from pathlib import Path
from dotenv import load_dotenv

script_dir = Path(__file__).parent
project_root = script_dir.parent
os.chdir(project_root)

load_dotenv()

def test_oss_connection():
    """测试阿里云OSS连接"""
    # 获取配置信息
    access_key_id = os.environ.get('ALIYUN_ACCESS_KEY_ID')
    access_key_secret = os.environ.get('ALIYUN_ACCESS_KEY_SECRET')
    bucket_name = os.environ.get('ALIYUN_BUCKET_NAME')
    endpoint = os.environ.get('ALIYUN_ENDPOINT')
    
    if not all([access_key_id, access_key_secret, bucket_name, endpoint]):
        print("错误: 环境变量不完整。请确保您已经设置了以下环境变量:")
        print("  ALIYUN_ACCESS_KEY_ID")
        print("  ALIYUN_ACCESS_KEY_SECRET")
        print("  ALIYUN_BUCKET_NAME")
        print("  ALIYUN_ENDPOINT")
        return False
    
    try:
        # 打印配置信息
        print(f"Access Key ID: {access_key_id[:8]}********")
        print(f"Access Key Secret: {access_key_secret[:8]}********")
        print(f"Bucket Name: {bucket_name}")
        print(f"Endpoint: {endpoint}")
        
        # 创建Auth和Bucket对象
        auth = oss2.Auth(access_key_id, access_key_secret)
        bucket = oss2.Bucket(auth, endpoint, bucket_name)
        
        # 测试上传
        test_key = 'test/connection_test.txt'
        bucket.put_object(test_key, 'Hello, OSS! 这是一个连接测试。')
        
        # 测试下载
        result = bucket.get_object(test_key)
        content = result.read().decode('utf-8')
        print(f"\n读取测试文件内容: {content}")
        
        # 测试列出对象
        print("\n存储桶中的对象:")
        for obj in oss2.ObjectIterator(bucket, prefix='test/', max_keys=10):
            print(f"  - {obj.key}")
        
        # 清理
        print("\n删除测试文件...")
        bucket.delete_object(test_key)
        
        print("\n🎉 连接测试成功! 您的阿里云OSS配置正常。")
        return True
    except oss2.exceptions.ServerError as e:
        print(f"\n服务器错误: {e}")
        if '403' in str(e):
            print("权限错误: 请检查您的AccessKey是否具有正确的权限。")
        return False
    except oss2.exceptions.ClientError as e:
        print(f"\n客户端错误: {e}")
        return False
    except Exception as e:
        print(f"\n未知错误: {e}")
        return False

if __name__ == "__main__":
    print("=== 阿里云OSS连接测试 ===")
    success = test_oss_connection()
    sys.exit(0 if success else 1) 