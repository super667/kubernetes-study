# Django进阶实战

## 一、为已有系统数据库生成管理平台

1.创建项目

```bash
django-admin startproject empmanager
```

2.修改setting.py

```python
# vim settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'poll',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': '10.4.7.70',
        'PORT': '3306'
    }
}
```

3.创建一个应用

```bash
python3 manage.py startapp candidates
```

4.生成model类

```bash
python3 manage.py inspectdb > candidates/models.py
```

5.修改生成的models.py

```bash
修改models.py文件
```

6.启动django

```bash
python manager runserver 0.0.0.0:8000
```

## 二、定义自己的中间件

### 创建一个性能和日志中间件

```python
# 增加一个中间件函数
import time
import logging


logger = logging.getLogger(__name__)


def perfromance_logger_middle(get_response):
    def middleware(request):
        start_time = time.time()
        response = get_response(request)
        duration = time.time() - start_time
        response["X-page-Duration-ms"] = int(duration * 1000)
        logger.info("%s %s %s", duration, request.path, request.GET.dict())
        return response

    return middleware
```

将中间件添加到settings.py

```python
MIDDLEWARE = [
    'interview.performance.perfromance_logger_middle', # 新增
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```
