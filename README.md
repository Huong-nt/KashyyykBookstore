
# BookStore Api

======

--------------------------------------------

## Deploy to EC2

```txt
1. Build docker image:
    docker-compose build
2. Eport image:
    docker images
    docker save 0984760xxx/bookstore.api:alpha-2020.03.13 > alpha-2020.03.13.tar
3. Load image:
    docker load --input alpha-2020.03.13.tar
4. Run image:
    docker-compose up -d
5. Remove old image:
    docker rmi 0984760xxx/bookstore.api:alpha-2019.12.13
```

## Runing local

### Setup

```sh
sudo apt-get install python3.6-dev libmysqlclient-dev
pipenv install
```

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

### Run app

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
