## Bibi

**Bibi** is an e-commerce fullstack solution built with Flask. It includes e-commerce, social, and hot common modules. It stood the test of business operations, is a light but complete solution.

This project provides backend service, based on Flask, MongoDB, Redis, Celery, RabbitMQ, and supports Python 3.5.

Bibi offers fullstack solution for use with the following:

> [bibi-frontend](https://github.com/seasonstar/bibi-frontend) Mobile web frontend

> [bibi-ionic](https://github.com/seasonstar/bibi-ionic) Hybrid APP

* 可观看[中文文档](https://github.com/seasonstar/bibi/blob/master/README_zh.md)

----------------

**Features**：

- [x] User
    - [x] Supports Email, Wechat, Weibo, QQ, and Facebook Oauth，[social-oauth](https://github.com/seasonstar/social-oauth) for details
    - [x] User Information, Address, Contact, Favor collections and etc..
- [x] Social
    - [x] Post, like, comment, and bad information report.
    - [x] Following and followers.
    - [x] Notifications.
- [x] Content
    - [x] Products board
    - [x] Banners
- [x] Product
    - [x] Brands, categories, tags, vendors, price history.
    - [x] Commodities sub-selections based on different colors, sizes and materials.
- [x] Cart
    - [x] Session carts
    - [x] Snapshot for items
- [x] Order
    - [x] Snapshot for order, store items history
    - [x] Split into different packages depend on the total price and categories
    - [x] Logistics information tracking, automatic updates
    - [x] Third party logistics business parcel handling
- [x] Payment
    - [x] Supports Wechat，Paypal and etc..
    - [x] Supports coupons, coins for discount.
- [x] Management System

- [x] AWS file upload
- [x] Bing translate API
- [x] Openexchange rate API
- [x] Kuaidi100 logistics tracking API


#### Screenshot

Content Management
![](http://7xn6eu.com1.z0.glb.clouddn.com/Backend.png)
Logistics Management
![](http://7xn6eu.com1.z0.glb.clouddn.com/Logistics-Backend.jpg)
Product Management
![](http://7xn6eu.com1.z0.glb.clouddn.com/Item%20Backend.png)

#### Get Started

This based on Ubuntu/Debian，please skip if you had set up Python 3 environment.

```bash
# set up python3 environment
sudo apt-get update
sudo apt-get install python3-pip python3-dev
sudo apt-get install build-essential libssl-dev libffi-dev python-dev

# set up virtualenv
sudo pip3 install virtualenv virtualenvwrapper
echo "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" >> ~/.bashrc
echo "export WORKON_HOME=~/Env" >> ~/.bashrc
echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
source ~/.bashrc

# Now virtual env for python3 will be installed in ~/Env

mkvirtualenv bibi # rename bibi
workon bibi # activate bibi env

# set up mongodb # 2.6 version
# set up redis
# set up rabbitMQ

mongod &              # start mongodb
redis-server &        # start redis
rabbitmq-server &     # start RabbitMQ
```

Install dependencies
```bash
pip3 install -r requirements.txt
```

Initial database
```python
python3 manage.py shell
# into Python3 shell
>>> from application.models import User
>>> user = User.create(email="xxxx@xxx.com", password="xxx", name="xxxx")
# Rename the email, password, name
>>> user.roles.append("ADMIN")
>>> user.save()
```

Run server
```
# start celery
celery -A application.cel worker -l info &

python3 manage.py runserver
```
Now open http://127.0.0.1:5000/admin/ on local.



#### Deploy
```bash
# set up supervisor
sudo apt-get install supervisor
# set up gunicorn
pip3 install gunicorn
```
Create supervisor config

`sudo vim /etc/supervisor/conf.d/bibi.conf`
```
[program:bibi]
command=/root/Env/bibi/bin/gunicorn
    -w 3
    -b 0.0.0.0:8080
    --log-level debug
    "application.app:create_app()"

directory=/opt/py-maybi/                                       ; Project dir
autostart=false
autorestart=false
stdout_logfile=/opt/logs/gunicorn.log                          ; log dir
redirect_stderr=true
```
PS: -w  the workers number，formula：（CPUs*2 + 1)

Create nginx config

`sudo vim /etc/nginx/sites-enabled/bibi.conf`

```nginx
server {
    listen 80;
    server_name bigbang.maybi.cn;

    location / {
        proxy_pass http://127.0.0.1:8080; # Pointing to the gunicorn host
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

  }
```

Start supervisor, nginx
```bash
sudo supervisorctl reload
sudo supervisorctl start bibi

sudo service nginx restart
```

Bravo! It's done.

Please open issues if you have problems.

-----------------------------------
#### License

Apache-2.0
