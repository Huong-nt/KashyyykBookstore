
# BookStore Api

--------------------------------------------

### Init db

```sh
source $(pipenv --venv)/bin/activate
(venv) $ flask shell
db.drop_all()
db.create_all()
```

### Migrate database

```sh
(venv) $ flask db migrate -m "something need to migrate"
(venv) $ flask db upgrade
```

## Unit test

### Set env variables

- Linux
```sh
export FLASK_APP=./bookstore/flasky.py
export FLASK_CONFIG=development
export PRESERVE_CONTEXT_ON_EXCEPTION=False
export DB_HOST=<dbhost>
export DB_USERNAME=<dbusername>
export DB_PASSWORD=<dbpassword>
export AWS_ACCESS_KEY_ID=<awsaccesskey>
export AWS_SECRET_ACCESS_KEY=<awssecretkey>
```
- Window
```sh
set FLASK_APP=./bookstore/flasky.py
set FLASK_CONFIG=development
set PRESERVE_CONTEXT_ON_EXCEPTION=False
set DB_HOST=<dbhost>
set DB_USERNAME=<dbpassword>
set DB_PASSWORD=<dbpassword>
set AWS_ACCESS_KEY_ID=<awsaccesskey>
set AWS_SECRET_ACCESS_KEY=<awssecretkey>
```

### Run unittest

```sh
flask test
```

Or test a specific module

```sh
flask test tests.test_basics.BasicsTestCase
```

## Deployment

### Docker

```txt
1. Build docker image:
    docker-compose build
2. Upload image to docker hub:
    docker push 0984760xxx/bookstore.api:alpha-2020.03.13
3. Run image:
    docker-compose up -d
```

### Local

#### Setup

```sh
sudo apt-get install python3.6-dev libmysqlclient-dev
pipenv install
```

#### Run app

```sh
chmod +x bash_bootstrap.sh
chmod +x bootstrap.sh
```

```sh
source $(pipenv --venv)/bin/activate
export FLASK_ENV=development
export FLASK_APP=./code/flasky.py
flask run -h 0.0.0.0 -p 5001
```

or using bootstrap:

```sh
./bash_bootstrap.sh
```

or using docker:

```sh
chmod +x boostrap.sh
docker-compose build
docker-compose up -d
```

## Config Nginx

```url
https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-18-04
```

### Config

```conf
# For load balance
upstream backend {
    server 172.31.25.126:5002;
    server 172.31.27.83:5002;
    # server 192.0.0.1 backup;
}

server {

    server_name bookstore.com www.bookstore.com;

    set_real_ip_from 0.0.0.0/0;
    real_ip_header X-Real-IP;
    real_ip_recursive on;

    location / {
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-Host $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   Host $http_host;
        proxy_pass         http://backend;
    }
}

```

### Let's Encrypt

```url
https://certbot.eff.org/lets-encrypt/ubuntubionic-nginx.html
```
