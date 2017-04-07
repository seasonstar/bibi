## Bibi

Bibi原本是一款海外留学生活助手APP，含电商，社交等热门模块，经历过商业运营的考验，是较为成熟的解决方案。

本项目是电商服务后端，基于 Flask, MongoDB, Redis, Celery, RabbitMQ, 支持 Python 3.5.

Bibi 提供电商全栈解决方案，配合以下项目使用:

> [bibi-frontend](https://github.com/seasonstar/bibi-frontend) 微信前端项目

> [bibi-ionic](https://github.com/seasonstar/bibi-ionic) 手机端Hybrid APP源码

----------------

**Features**：

- [x] 用户中心
    - [x] 支持邮件，微信，微博，QQ，Facebook及其手机客户端等登录，详看[social-oauth](https://github.com/seasonstar/social-oauth)支持
    - [x] 用户基本信息，收货地址，联系方式，喜欢收藏
- [x] 社交系统
    - [x] 发布帖子，点赞，评论，不良信息举报
    - [x] 用户之间可相互关注
    - [x] 新消息通知
- [x] 内容系统
    - [x] 商品专题
    - [x] Banner广告
- [x] 商品系统
    - [x] 品牌，类别，标签，供货商，价格系统
    - [x] 商品基于不同颜色，尺寸等不同价格的子选择
- [x] 购物车系统
    - [x] 支持匿名放入购物车
    - [x] 商品快照，上下架更新
- [x] 订单系统
    - [x] 订单快照，保存商品历史信息
    - [x] 根据商品总价和类别拆分成不同包裹
    - [x] 国内外物流信息跟踪，自动更新
    - [x] 第三方物流商对接包裹处理
- [x] 支付系统
    - [x] 支持微信，Paypal等支付方式
    - [x] 用户钱包支持 优惠券，金币等减免方式
- [x] 后台管理系统

- [x] AWS文件上传
- [x] Bing翻译API对接
- [x] Openexchange外币兑换汇率API对接
- [x] kuaidi100快递跟踪API对接
- [x] 4PX物流商对接


#### Screenshot

内容管理界面
![](http://7xn6eu.com1.z0.glb.clouddn.com/Backend.png)
物流管理界面
![](http://7xn6eu.com1.z0.glb.clouddn.com/Logistics-Backend.jpg)
商品管理界面
![](http://7xn6eu.com1.z0.glb.clouddn.com/Item%20Backend.png)

#### 搭建环境

本教程基于Ubuntu/Debian，已安装python3 环境的请跳过

```bash
# 安装python3环境
sudo apt-get update
sudo apt-get install python3-pip python3-dev
sudo apt-get install build-essential libssl-dev libffi-dev python-dev

#安装virtualenv
sudo pip3 install virtualenv virtualenvwrapper
echo "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" >> ~/.bashrc
echo "export WORKON_HOME=~/Env" >> ~/.bashrc
echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
source ~/.bashrc

# 现在你的home目录下有Env的文件夹，你的python虚拟环境都会创建在这里

mkvirtualenv bibi # bibi可随便改成你的项目名
workon bibi # 现在已进入项目的独立环境

# 安装 mongodb 略  (请安装mongodb 2.6版本)
# 安装 redis 略
# 安装 rabbitMQ 略

mongod &              # 启动mongodb
redis-server &        # 启动redis
rabbitmq-server &     # 启动RabbitMQ
```

安装依赖
```bash
pip3 install -r requirements.txt
```

初始化数据库
```python
python3 manage.py shell
# into Python3 shell
>>> from application.models import User
>>> user = User.create(email="xxxx@xxx.com", password="xxx", name="xxxx")
# email, password, name改成你自己的
>>> user.roles.append("ADMIN")
>>> user.save()
```

运行

```
# 启动 celery
celery -A application.cel worker -l info &

python3 manage.py runserver
```
本地可以打开 http://127.0.0.1:5000/admin/



#### 部署方式
```bash
# 安装 supervisor
sudo apt-get install supervisor
# 安装 gunicorn
pip3 install gunicorn
```
创建supervisor配置

`sudo vim /etc/supervisor/conf.d/bibi.conf`
```
[program:bibi]
command=/root/Env/bibi/bin/gunicorn
    -w 3
    -b 0.0.0.0:8080
    --log-level debug
    "application.app:create_app()"

directory=/opt/py-maybi/                                       ; 你的项目代码目录
autostart=false                                                ; 是否自动启动
autorestart=false                                              ; 是否自动重启
stdout_logfile=/opt/logs/gunicorn.log                          ; log 日志
redirect_stderr=true
```
PS: 上面 -w 为 开启workers数，公式：（系统内核数*2 + 1)

创建nginx配置

`sudo vim /etc/nginx/sites-enabled/bibi.conf`

```nginx
server {
    listen 80;
    server_name bigbang.maybi.cn; # 这是HOST机器的外部域名，用地址也行

    location / {
        proxy_pass http://127.0.0.1:8080; # 这里是指向 gunicorn host 的服务地址
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

  }
```

接着启动 supervisor, nginx
```bash
sudo supervisorctl reload
sudo supervisorctl start bibi

sudo service nginx restart
```

大功告成。


有问题，欢迎提Issue。


----------------

#### License

Apache-2.0
