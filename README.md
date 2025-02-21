# How to run

```
$ git clone https://github.com/axdyer/WellLog.git
$ cd WellLog
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
$ python manage.py createsuperuser
$ python manage.py runserver
# Load the site at http://127.0.0.1:8000 or http://127.0.0.1:8000/admin for the admin
```
