# Nginx

## 安装部署

## 安装指定模块

### 第三方模块nginx_substitutions_filter安装，演示

参考官网(<https://github.com/yaoweibin/ngx_http_substitutions_filter_module>)

nginx_substitutions_filter

    这个模块不会随着nginx源码一块发布，需要自己安装

  Description

    nginx_substitutions_filter是一个过滤模块，可以使用正则表达式或者固定的字符串替换
    响应体（不支持nginx中的变量），这模块不同于nginx的原生的Substitution模块。它扫描
    输出缓冲区，并逐行扫描。这个模块只处理纯文本，不能对响应体进行解压。可以不设置压
    缩，头部增加header：Accept-Encoding

  示例：

    proxy_set_header Accept-Encoding "";

  配置示例：

    location / {
        subs_filter_types text/html text/css text/xml;
        subs_filter st(\d*).example.com $1.example.com ir;
        subs_filter a.example.com s.example.com;
    }

  提供的指令

    *   subs_filter_types
    *   subs_filter

  subs_filter_types

    syntax:  *subs_filter_types mime-type [mime-types]*
    default: *subs_filter_types text/html*
    context: *http, server, location*


​    

### if指令的条件表达式

1. 检查变量为空或者值为0，直接使用
2. 将变量与字符做匹配，使用=或者！=
3. 将变量与正则表达式做匹配
   + 大小写敏感，~或者！~
   + 大小写不敏感，~\*或者！~\*
4. 检查文件是否存在，使用-f或者!-f
5. 检查目录是否存在，使用-d或者!-d
6. 检查文件，目录，软链接是否存在，使用-e或者!-e
7. 检查是否为可执行文件，使用-x或者!-x

```bash
# 示例
if ($http_user_agent ~ MSIE) { 
rewrite ^(.*)$ /msie/$1 break; 
} 
if ($http_cookie ~* "id=([^;]+)(?:;|$)") { 
set $id $1; 
} 
if ($request_method = POST) { 
return 405; 
} 
if ($slow) { 
limit_rate 10k; 
} 
if ($invalid_referer) { 
return 403; 
}
```

