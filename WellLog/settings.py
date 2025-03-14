from pathlib import Path
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-^&pv6!rhwvdk(jg6!tr$3#4h!_@i#9mx!@)8n70$oxa^ec%!ju')

DEBUG = True

ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1", "welllog.top"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    'widget_tweaks',
    # Third-party
    "allauth",
    "allauth.account",
    'allauth.socialaccount',
    "crispy_forms",
    "crispy_bootstrap5",
    "storages",
    "mathfilters",
    # "debug_toolbar",
    # Local
    "pages",
    'accounts',
    'health',
    'community',
    'analysis',
    
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "debug_toolbar.middleware.DebugToolbarMiddleware",  # Django Debug Toolbar
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'WellLog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        "DIRS": [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'WellLog.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'wellog',
        'USER': 'myuser',
        'PASSWORD': 'mypassword',
        'HOST': 'welllog.top',
        'PORT': '8888',
        'TEST': {
            'NAME': 'test',
            'SERIALIZE': False,
            'CREATE_DB': False,
            'MIRROR': None,
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOCALE_PATHS = [BASE_DIR / 'locale']
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = "bootstrap5"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "root@localhost"
INTERNAL_IPS = ["127.0.0.1"]
AUTH_USER_MODEL = "accounts.CustomUser"
SITE_ID = 1
LOGIN_REDIRECT_URL = "home"
ACCOUNT_LOGOUT_REDIRECT_URL = "home"
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True

# Media files (Images, Videos, etc.)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Object Storage Settings - 保持简单配置
# 使用本地文件系统存储作为默认值
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# 存储自定义配置
ALIYUN_OSS = {
    'ACCESS_KEY_ID': os.environ.get('ALIYUN_ACCESS_KEY_ID', ''),
    'ACCESS_KEY_SECRET': os.environ.get('ALIYUN_ACCESS_KEY_SECRET', ''),
    'BUCKET_NAME': os.environ.get('ALIYUN_BUCKET_NAME', ''),
    'ENDPOINT': os.environ.get('ALIYUN_ENDPOINT', ''),
    'URL_EXPIRES_IN': 60 * 60 * 24 * 365,  # 链接有效期(秒)
}

# 腾讯云COS设置（已禁用）
# DEFAULT_FILE_STORAGE = 'storages.backends.tencent.TencentStorage'
# TENCENT_SECRET_ID = os.environ.get('TENCENT_SECRET_ID', '')
# TENCENT_SECRET_KEY = os.environ.get('TENCENT_SECRET_KEY', '')
# TENCENT_BUCKET_NAME = os.environ.get('TENCENT_BUCKET_NAME', '')
# TENCENT_REGION = os.environ.get('TENCENT_REGION', '')  # 例如：ap-beijing

# AWS S3设置（取消注释并配置您的AWS S3信息）
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
# AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
# AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')
