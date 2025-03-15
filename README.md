# Wellog -- A Web Site to Record Your Health Data.
## About
Welcome to our website: [WellLog.top](url)  
This Web provide a platform for people to record their health and sports data and get professional AI adivce to help you promote your training. You also can share your moment and tips about sports. Hope you enjoy here.
## Who I am 
Yu Ye  
Junqiang Ji  
Ruihan Xu  
We are Group-08 of ITECH course in University of Glasgow. This a project of this course.
## How to run

```
$ git clone https://github.com/axdyer/WellLog.git
$ cd WellLog
```
Add your secret key to `.env`. Here is a template for your reference.
```.env
SECRET_KEY=

# PostgreSQL Setting
DATABASE_NAME=
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_HOST=
DATABASE_PORT=

# DeepSeek API
AI_API_KEY=

# Aliyun OSS Setting
ALIYUN_ACCESS_KEY_ID=
ALIYUN_ACCESS_KEY_SECRET=
ALIYUN_BUCKET_NAME=
ALIYUN_ENDPOINT=
```

You can use conda to create a fresh virtual environment on either Windows or macOS.

```
$ conda create -n WellLog
$ conda activate WellLog
$ pip install -r requirements.txt
```

Then all packages needed will be installed.

```
$ python manage.py migrate
$ python manage.py runserver
```
Load the site at http://127.0.0.1:8000
