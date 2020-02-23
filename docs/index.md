# Notes / Troubleshooting

## Docker

### Running and shutting down the development sever

The development server is not started anymore when the containers are brought up, as it then runs in the background and is difficult to shut down or start. 

So after starting the containers with `docker-compose up -d`, run `docker-compose exec web python manage.py runserver 0:8000`

### When you get error messages on missing dependencies

When a new Python/Django dependency is installed, do a rebuild - this will only affect the web container (the other one is based on an image that doesn't change).

`docker-compose build`

### Accessing server and database

For accessing a docker container, there are two alternative ways, either using _docker_ or _docker-compose_, both using the exec command

`docker-compose exec web bash` will give you access to the container where the app is running; you could equally use `docker exec -it bookxchange_web_1 bash` where the container name depends on the name of the parent directory (look up the container name with `docker ps`)

To log into the database, use `docker-compose exec db psql -U dj` or `docker exec -it bookxchange_db_1 psql -U dj`

### Run migrations

`docker-compose exec web python manage.py migrate`

### Operations on postgres

Copy file from host into docker         
`docker cp book_x.sql bookxchange_db_1:/var/backups`          

Drop database, create it again and restore from database dump         
docker-compose exec db psql -U dj -d postgres -c "DROP DATABASE dj"         
docker-compose exec db psql -U dj -d postgres -c "CREATE DATABASE dj"      
docker-compose exec db psql -U dj -f /var/backups/book_x_2020_22.sql  

### Generally useful 

Stop all docker containers: `docker stop $(docker ps -a -q)`

Inspect container: `docker inspect -f '{{ json .Mounts }}' bookxchange_db_1 | python -m json.tool`   (example)

Look at logs: `docker-compose logs web` or `docker logs bookxchange_web_1`

## Postgres

`\x on` switches to a neater display of table entries

## Frontend

### Compiling css files

Install gulp globally: `yarn global add gulp-cli` or `npm install -g gulp-cli`
Install local dependencies: `yarn` or `npm install`
Start gulp watch with browsersync: `gulp` - app then running on localhost:3000, reload should be trigger on change of sass or html files