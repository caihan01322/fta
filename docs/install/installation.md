# 故障自愈 下载安装

# 1 下载安装

## 1.1 源码下载
```
    git clone https://github.com/Tencent/bk_fta_solutions.git
```

## 1.2 前置依赖安装

> 操作系统: centos6.5以上版本

### 1.2.1 前端开发依赖软件

* MySQL >= 5.5.24

请参看官方资料 [MySQL](https://dev.mysql.com/doc/mysql-getting-started/en/#mysql-getting-started-installing)

推荐版本下载： [MySQL 5.5+](https://dev.mysql.com/downloads/mysql/5.5.html#downloads)

### 1.2.2 后台开发依赖软件

* redis >= 3.2.8

请参看官方资料 [redis](https://redis.io/download#installation)

推荐版本下载： [redis 3.2.8](http://download.redis.io/releases/redis-3.2.8.tar.gz)

* beanstalkd >= 1.10

请参看官方资料 [beanstalkd](https://beanstalkd.github.io/download.html)

推荐版本下载： [beanstalkd 1.10](https://github.com/kr/beanstalkd/archive/v1.10.tar.gz)


依赖库安装

```
yum install \
    --skip-broken \
    --assumeyes \
    --quiet \
    "python-tools" \
    "python-devel" \
    "bzip2-devel" \
    "expat-devel" \
    "gettext-devel" \
    "libzip-devel" \
    "libcurl-devel" \
    "libxml2-devel" \
    "libffi-devel" \
    "mysql-devel" \
    "openssl" \
    "openssl-devel" \
    "readline-devel" \
    "sqlite-devel" \
    "zlib-devel" \
    "patch"
    > /dev/null || exit 1
```

### 1.2.3 python安装

> 本项目支持以下python版本

* 2.7.12
* 2.7.13
* 2.7.9-stackless
* 2.7.12-stackless

### 1.2.4 python库
* pbr-1.10.0
* six-1.10.0
* stevedore-1.19.1

### 1.2.5 配置本地 hosts
* 执行“sudo vim /etc/hosts”，添加“127.0.0.1 {your_domain}”


## 1.3 Web安装部署：

### 1.3.1 进入Web层根目录
源码包含Web层和后台服务层两个部分，其中web_app是Web层根目录，在源码下载目录执行`cd web_app`

### 1.3.2 数据库初始化

* 在 mysql 中创建名为 bk_fta_solutions 的数据库
```sql
CREATE DATABASE `bk_fta_solutions` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
```

* 执行初始化sql 其中`your_user_name`需要替换为连接mysql的用户名
```
mysql -uyour_user_name -p  < sql/init_fta.sql
```

### 1.3.3 安装python依赖库
```
    pip install -r requirements.txt
```

### 1.3.4 修改本地配置
进入到工程目录下

* 修改 ./project/conf/settings_env.py

> 请注意：以下列举变量必须要结合本地社区版的实际情况进行配置，否则故障自愈的大部分功能将无法使用

```python
# ==============================================================================
# 应用基本信息配置 (请按照说明修改)
# ==============================================================================
# APP_ID不用修改
APP_ID = 'bk_fta_solutions'
# APP_TOKEN需要到官方网站的admin中获取 默认访问http://{BK_PAAS_HOST}/admin/app/app/ 找到名为"故障自愈"的记录，查看详情获取Token字段值
APP_TOKEN = ''
# 蓝鲸智云开发者中心的域名，例如：http://paas.bking.com:80
BK_PAAS_HOST = ""

# 蓝鲸智云作业平台的域名，例如：http://job.bking.com:80
BK_JOB_HOST = ""
# 蓝鲸智云配置平台的域名，例如：http://cmdb.bking.com:80
BK_CC_HOST = ""
# 缓存时间
CACHE_TIME = 5
```

* 修改 ./conf/local_settings.py，设置本地开发用的数据库信息和本地后台API连接变量信息

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 默认用mysql
        'NAME': APP_ID,       # 数据库名 (默认与APP_ID相同)
        'USER': 'root',       # 你的数据库user
        'PASSWORD': '',       # 你的数据库password
        'HOST': 'localhost',  # 数据库HOST
        'PORT': '3306',       # 默认3306
    },
}


LOCAL_BACKEND_HOST = 'http://127.0.0.1:13031'

FTA_API_PREFIX = '%s/event/' % LOCAL_BACKEND_HOST
FTA_CALL_BACK_URL = '%s/callback/' % LOCAL_BACKEND_HOST
FTA_STATUS_URL = '%s/status/process/' % LOCAL_BACKEND_HOST

```

* 修改 ./web_app/settings.py, 注释掉以下内容

**`请注意 此步骤仅针对本地开发 部署至服务器时清取消此修改`**

![](../docs/resource/img/注释后.png)


### 1.3.5 应用数据初始化

* 在 ./web_app 目录下执行以下命令初始化数据库

```
python manage.py migrate
python manage.py createcachetable django_cache
```

### 1.3.6 运行程序
```
python manage.py runserver {your_port}
```

### 1.3.7 访问页面
在hosts添加 127.0.0.1 local.**${BK\_PAAS\_DOMAIN}**
>  BK\_PAAS\_DOMAIN 为用户个人部署的蓝鲸智云的域名，否则无法进行登录验证

通过浏览器访问 http://{your_domain}:{your_port}/ 验证APP是否正常启动。

## 1.4 后台安装：

### 1.4.1 进入后台服务层根目录

server是后台服务根目录，在源码下载目录执行`cd server`

### 1.4.2 项目依赖库安装

运行 `pip install -r requirements.txt`

### 1.4.3 修改本地配置

* 修改 fta/templates/conf/settings_local.py

```bash
vim fta/templates/conf/settings_local.py
```

> **`请注意：以下变量为必填变量，必须结合本地蓝鲸智云社区版的实际情况进行配置，否则故障自愈的大部分功能将无法使用`**

```python

# 本地社区版蓝鲸智云页面访问地址 eg: http://paas.bk.com
PAAS_ADDR = ''

# 本地社区版蓝鲸智云内网地址 如果不确认 可以和PAAS_ADDR保持一致  eg: http://paas.bk.com
PAAS_INNER_ADDR = ''

# 本地社区版JOB页面访问地址 eg: http://job.bk.com
JOB_ADDR = ''

# APP_TOKEN需要到官方网站的admin中获取 默认访问http://{PAAS_ADDR}/admin/app/app/ 找到名为"故障自愈"的记录，查看详情获取Token字段值
APP_SECRET_KEY = ''

# 通知人列表 用于接收后台发送的通知信息 填空则默认后台不发送信息 仅记录日志
VERIFIER = [""]

# 本地python运行环境 eg: /usr/local/python2.7/bin/
PYTHON_HOME = ""

# FTA WEB SERVER PORT
WEBSERVER_PORT = 13021
APISERVER_PORT = 13031
JOBSERVER_PORT = 13041
WEBSERVER_URL = "http://127.0.0.1:%s" % WEBSERVER_PORT

# BEANSTALKD
BEANSTALKD_HOST = ['']          # beanstalkd ip地址
BEANSTALKD_PORT = 14711         # beanstalkd 端口

# MYSQL
MYSQL_NAME = 'bk_fta_solutions'
MYSQL_USER = ''                 # 数据库访问用户
MYSQL_PASSWORD = ''             # 访问密码
MYSQL_HOST = ''                 # 数据库地址
MYSQL_PORT = 3306               # 数据库端口

# REDIS
REDIS_HOST = ['']               # redis ip地址
REDIS_PASSWD = ''               # redis 访问密码
REDIS_PORT = 6379               # redis 访问端口

```


### 1.4.4 本地开发环境后台初始化
```
bin/init_local.sh
```

### 1.4.5 启动后台
```
bash bin/fta.sh start
```

### 1.4.6 所有可用控制命令
> start -- 启动
> 
> stop -- 停止进程， supervisor进程依然保留
> 
> restart -- 重启
> 
> reload -- 重载配置文件
> 
> status -- 查看进程状态
> 
> shutdown -- 关闭supervisor

可通过执行下述命令来获取可用命令列表

```
bash bin/fta.sh
```




