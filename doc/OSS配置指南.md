# 阿里云OSS对象存储配置指南

本文档提供在WellLog应用中配置阿里云OSS对象存储的详细步骤。

## 1. 准备工作

在配置前，您需要先从阿里云获取以下信息：

- AccessKeyId：访问密钥ID
- AccessKeySecret：访问密钥密钥
- BucketName：存储桶名称
- Endpoint：区域端点（如 `oss-cn-beijing.aliyuncs.com`）

如果您还没有阿里云账号或这些信息，请按以下步骤操作：

1. 注册一个阿里云账号：https://account.aliyun.com/register/register.htm
2. 创建一个AccessKey：https://ram.console.aliyun.com/manage/ak
3. 创建一个OSS存储桶：https://oss.console.aliyun.com/bucket

注意：建议创建RAM用户，并只授予该用户OSS相关权限，以提高安全性。

## 2. 配置项目

1. 首先确保`.env`文件中包含以下配置（用您的实际值替换）：

```
ALIYUN_ACCESS_KEY_ID=your_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret
ALIYUN_BUCKET_NAME=your_bucket_name
ALIYUN_ENDPOINT=your_endpoint.aliyuncs.com
```

2. 安装必要的Python依赖：

```bash
pip install aliyun-python-sdk-core aliyun-python-sdk-kms oss2 python-dotenv
```

## 3. 验证配置

在配置完成后，您应该验证OSS连接是否正常工作。可以运行以下命令：

```bash
python scripts/test_oss.py
```

如果一切正常，您将看到测试成功的消息，表明可以连接到OSS并进行基本操作。

## 4. 图片迁移

如果您之前已经有存储在数据库中的图片，可以使用以下命令将它们迁移到OSS：

```bash
python manage.py migrate_images
```

要迁移特定帖子的图片：

```bash
python manage.py migrate_images --post-id=123
```

要强制重新迁移所有图片：

```bash
python manage.py migrate_images --force
```

## 5. 故障排除

如果您遇到OSS相关问题，请检查：

1. 确认您的`.env`文件包含正确的OSS配置
2. 验证AccessKey有足够的权限访问该Bucket
3. 检查Bucket是否配置了合适的权限
4. 网络连接问题（防火墙、代理等）
5. 检查域名解析是否正常

如果应用启动时显示`WARNING: 阿里云OSS配置未完成，使用本地文件系统存储`，则表示OSS环境变量配置不完整，
应用回退使用本地文件系统存储图片。

## 6. 安全最佳实践

- 不要在代码库中硬编码OSS凭证，始终使用环境变量
- 使用权限最小的RAM用户
- 定期轮换AccessKey
- 配置OSS防盗链功能
- 启用OSS访问日志

## 7. 常见问题

**Q: 为什么上传图片后不能立即显示？**  
A: 这可能是由于CDN缓存或者权限问题。检查Bucket的访问权限和防盗链设置。

**Q: 能否设置图片过期时间？**  
A: 是的，您可以在`settings.py`中调整`ALIYUN_URL_EXPIRES_IN`设置，单位为秒。

**Q: 是否可以设置自定义域名？**  
A: 可以，在阿里云控制台为您的Bucket绑定自定义域名后，需要对应修改OSS配置。 