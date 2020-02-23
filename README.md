![](https://travis-ci.com/katjad/bookxchange.svg?branch=master)

# bookxchange

## Set up dev environment


### Using Docker

You will need [Docker](https://docs.docker.com/install/) and [Docker Compose](https://docs.docker.com/compose/install/) installed


Build containers and run services in detached mode:

```
docker-compose up -d
```

Run Django commands to migrate data and create superuser:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

Create the directory used for media uploads in development:
```
docker-compose exec web mkdir -p media/covers
```
The local development server should be running at this point, and the app accessible in the browser at localhost:800. If it needs to be started again, you can use this command:
```
docker-compose exec web python manage.py runserver 0:8000
```


### Manually

This is for Ubuntu 18.04, it will vary slightly for other OSs.

Make sure pip, venv (python3 version) and postgres are installed

```
$ sudo apt install python3-venv python3-pip postgresql
```

Create a virtual environment.
```
$ mkdir venvs && cd venvs
$ python3 -m venv bookx
$ source ~/venvs/bookx/bin/activate
$ (bookx) cd ~
```

Clone project and install requirements.

```
$ (bookx) git clone https://github.com/Geekfish/bookxchange.git
$ (bookx) cd bookxchange
$ (bookx) pip3 install -r requirements.txt
```

Create a postgres user and database, set db environment variables.
```
$ sudo su - postgres
$ createuser dj
$ createdb dj -O dj
$ psql
postgres=#q ALTER USER dj WITH PASSWORD 'new_password';

$ mv .env-file .env
```
Make sure you have the correct variables set in the .env file.

Run ```python manage.py runserver 0:8000``` to make sure that everything is set up correctly. You should be able to access the app at http://localhost:8000 .

To complete the setup, apply the database migrations and create a superuser.
```
$ python manage.py migrate
$ python manage.py createsuperuser
```
When you start the server again, you should now be able to log in and enter a book at http://localhost:8000/book/new .
