# LabAdmin
Manage user rights to access the lab and the machines

# how to setup locally

## install django

`pip install Django==1.9.8`

## install mysql
- create a db called labadmin
- configure the settings.py adding your db username and psw

## install the dependencies

```
pip install djangorestframework
pip install mysql-python
```

## apply modification in the model to the db

`python manage.py migrate `

##create a superuser account
this will be needed to access the admin interface

` python manage.py createsuperuser `

## sync the db and generate the required tables

`python manage.py migrate --run-syncdb`

## Run the server

`python manage.py runserver`

## admin view
you can access the admin view at
[127.0.0.1:8000/admin](127.0.0.1:8000/admin) and use the credential you created via superuser to login
