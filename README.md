# Airport-Service-API

Service for buying tickets and monitoring flights

## Installing process
Change mocks to your native data inside .env.sample. Do not forget to change file name to ".env".
#### Run with IDE(configure local db instead of remote)
```
    git clone https://github.com/alim2709/airport-api-service.git
    cd airport-api-service
    python -m venv venv
    venv\Scripts\activate (on Windows)
    source venv/bin/activate (on macOS)
    pip install -r requirements.txt
    set SECRET_KEY = YOUR_SECRET_KEY
    set POSTGRES_HOST=POSTGRES_HOST
    set POSTGRES_DB=POSTGRES_DB
    set POSTGRES_USER=POSTGRES_USER
    set POSTGRES_PASSWORD=POSTGRES_PASSWORD
    set POSTGRES_PORT=POSTGRES_PORT
    python manage.py migrate
    python manage.py runserver
```
    
###    Use the following command to load prepared data from fixture:
```
    python manage.py loaddata fixture-test-data.json
```
###    After loading data from fixture you can use following superuser (or create another one by yourself):
```
    - Login: `test@test1.com`
    - Password: `qwertyqwerty`
```

## Run with docker
Docker should be installed
#### Open terminal
```
    docker-compose build
    docker-compose up
```

## Getting access

* create user via /api/user/register
* get access token via api/user/token(do not forget to add "Bearer " before token)


## Features
* JWT authenticated
* Admin panel /admin/
* Managing orders with flights and tickets
* Creating airports, airplanes, airplane-types, air companies, flights, crews, routes, cities, countries, 
* Filtering flights by route, departure date, arrival date
* Filtering routes by source and destination
* The ability to add images to airports
