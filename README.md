# resource_apply

### 简介
这是一个简易的服务，为用户申请 MySQL 与 Redis 两类资源，采用resuful api的形式提供给用户使用，提供部分个性化配置。    
基础服务使用flask框架，数据库使用sqlite3，使用token验证进行资源访问验证和查询，资源实例通过docker容器运行，请确保环境能正常进行docker pull并能正常使用docker。
### 基本框架图
![image](https://github.com/yukimur/resource_apply/blob/main/images/%E5%9F%BA%E6%9C%AC%E6%9E%B6%E6%9E%84%E5%9B%BE.png)
### 基本使用及案例
1. 请确保本地环境安装了python3，sqlite3和docker；
2. 本地执行命令拉取资源镜像
    ```
    docker pull mysql:5.7
    docker pull redis 
    ```
3. 创建并进入虚拟环境
    ```
    python3 -m venv venv
    source venv/bin/activate
    ```
4. 依赖安装
    ```
    pip install -r requirements.txt
    ```
5. 创建数据库文件夹，该项目使用sqlite3，也可自行选择其他数据库，参考flask sqlalchemy配置
    ```
    mkdir path
    ```
    修改database.py数据库地址，注意要写绝对路径
    ```
    DATABASEPAATH = path
    ```
    初始化数据库并生成表格
    ```
    python database.py
    ```
6. 运行服务
    ```
    python api.py
    ```
    如果希望进行生产环境部署，请参考https://dormousehole.readthedocs.io/en/latest/deploying/index.html

7. 可以通过 /api/spec.html 查看项目提供的接口和信息，但由于使用token验证，暂不支持直接在该页面进行接口访问，可以选择通过postman进行接口访问，需要添加请求头信息：
    ```
    Authorization:Bearer {个人token}
    ```
    可以通过运行create_admin.py获取初始用户信息，如：
    ```
    python create_admin.py

    {'username': 'admin2', 'token': '8d8ac5ca136a11ec96b8525400e41c08'}
    ```

### 接口说明
POST /user 创建用户接口    
- params:
    - username: 用户名称
- rtype:
    - username: 用户名称
    - token: 用户token

GET /resource_list 查看用户资源列表    
- rtype:
    - data: 资源实例列表信息，如  
    ```
        {
            "data": [
                {
                    "id": 2,
                    "container_id": "90fe3bb6e9c4ee8588a5184419483b22119f0d096e74af8bf6c57a00441450e4",
                    "resource": "redis",
                    "config": {
                        "--maxmemory": "100m"
                    }
                }
        }
    ```
POST /resource_list  创建用户资源，可选是mysql和redis   
- post data:
    - resource_name: 资源实例名称，可选mysql和redis，必选参数
    - config: 配置信息
    ```
    支持部分个性化配置\n
    Mysql:
        MYSQL_DATABASE：数据库名称
        --character-set-server：默认编码
        --collation-server：排序规则
        更多参数参考https://hub.docker.com/_/mysql
    Redis:
        --maxmemory：最大内存
        更多参数参考https://hub.docker.com/_/redis?tab=description&page=1&ordering=last_updated
    ```
    如：
    ```
    POST /resource_list
    {
        "resource_name":"mysql",
        "config":{
            "MYSQL_DATABASE":"haha",
            "--character-set-server":"utf8" # 设置默认字符集
        }
    }
    ```
- rtype:
    返回资源实例信息，请注意mysql和redis返回信息不尽相同，如实例返回
    ```
    # mysql返回
    {
        "id": 14,
        "container_id": "b3bd95f3e0b6dabb9bb102dec14611c6106923aaa5c24750d266b08b7ef63673",
        "resource": "mysql",
        "config": {
            "container_id": "b3bd95f3e0b6dabb9bb102dec14611c6106923aaa5c24750d266b08b7ef63673",
            "addr": "192.168.41.20",    # 资源连接地址
            "port": 52281,              #  资源连接端口
            "config": {
                "--character-set-server": "utf8",  # 数据库字符集
                "inside_port": 3306,
                "environment": {
                    "MYSQL_ROOT_PASSWORD": "283a5bce136d11ec85d8525400e41c08",  # mysql连接密码
                    "MYSQL_DATABASE": "haha"                                    # mysql数据库名称
                }
            },
            "MYSQL_USER": "root"   # mysql远程连接用户，默认使用root
        }
    }
    # redis返回
    {
        "id": 13,
        "container_id": "59f90923640a887ef4d9014f7e1933a2fa5567389c9445d9cfe926756a7fb094",
        "resource": "redis",
        "config": {
            "container_id": "59f90923640a887ef4d9014f7e1933a2fa5567389c9445d9cfe926756a7fb094",
            "addr": "192.168.41.20",    # 资源连接地址
            "port": 45278,      #  资源连接端口
            "config": {
                "inside_port": 6379,
                "--requirepass": "99e2209c136611ecbfee525400e41c08" # redis 连接密码
            }
        }
    }
    ```

GET /resource/{id}  查看指定id资源配置   
- params:
    - id: resource id 即资源实例id
- rtype:
    返回实例配置信息，如
    ```
    {
        "id": 12,
        "container_id": "e19198131fa5212751612550695498ef29ba266563a31b9325966317663ed224",
        "resource": "mysql",    # 资源类型
        "config": {             # 配置信息
            "container_id": "e19198131fa5212751612550695498ef29ba266563a31b9325966317663ed224",
            "addr": "192.168.41.20",    # 地址
            "port": 42228,              # 端口
            "config": {
                "--character-set-server": "utf81",
                "inside_port": 3306,
                "environment": {
                    "MYSQL_ROOT_PASSWORD": "803dc52e136611ec9595525400e41c08",  # 数据库密码
                    "MYSQL_DATABASE": "haha"    # 数据库名称
                }
            },
            "MYSQL_USER": "root"    # 数据库账号
        },
        "is_running": true
    }
    ```
DELETE /resource/{id}   删除个人资源实例
- params:
    - id: resource id 即资源实例id
