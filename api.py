

from flask import Flask,request,abort
from flask_restful import Api,Resource as RS
from flask_restful_swagger import swagger
from resource import MysqlResource,RedisResource
from database import User,Resource,db_session
from flask_httpauth import HTTPTokenAuth
from dockerManager import DockerManager

app = Flask(__name__)
api = Api(app)
api = swagger.docs(Api(app), apiVersion='0.1')
auth = HTTPTokenAuth(scheme='Bearer')

@auth.verify_token
def verify_token(token):
    """接口用户统一验证"""
    user = User.query.filter_by(token=token).first()
    return user

class ResourceList(RS):
    
    @swagger.operation(
        notes="get user resource list",
        nickname="get"
    )
    @auth.login_required
    def get(self):
        user = auth.current_user()
        data = [{
            "id":resource.id,
            "container_id":resource.container_id,
            "resource":resource.resource,
            "config":resource.config,
        } for resource in user.resource]
        return {"data": data}

    @swagger.operation(
        notes="create a resource item",
        nickname="post",
        parameters=[
            {
              "name": "resource_name",
              "description": "choose mysql or redis",
              "required": True,
              "allowMultiple": False,
              "dataType": "string",
              "paramType": "string"
            },
            {
              "name": "config",
              "description": """
                支持部分个性化配置\n
                Mysql:
                    MYSQL_DATABASE：数据库名称
                    --character-set-server
                    --collation-server
                    更多参数参考https://hub.docker.com/_/mysql
                Redis:
                    更多参数参考https://hub.docker.com/_/redis?tab=description&page=1&ordering=last_updated
              """,
              "required": False,
              "allowMultiple": False,
              "dataType": "body",
              "paramType": "body"
            }
          ],
    )
    @auth.login_required
    def post(self):
        data = request.json
        resource_name = data.get("resource_name")
        if not resource_name:
            abort(400,"resource_name must required!")
        config = data.get("config",{})

        if resource_name == "mysql":
            resource = MysqlResource()
        elif resource_name == "redis":
            resource = RedisResource()
        else:
            abort(400,"must choose mysql or redis!")
        
        try:
            resource_info = resource.create()
        except Exception as e:
            resource.clear()
            abort(500,e)
        res = {}
        user = auth.current_user()
        resource = Resource(resource=resource_name,config=config,user_id=user.id)
        db_session.add(resource)
        db_session.commit()
        res["id"] = resource.id
        res["resource"] = resource.resource
        res["config"] = resource.config
        return res

class ResourceItem(RS):

    @swagger.operation(
        nickname="get"
    )
    @auth.login_required
    def get(self,id):
        """获取指定id资源信息"""
        user = auth.current_user()
        resource = Resource.query.filter_by(user_id=user.id,id=id).first()
        if not resource:
            abort(404,"the item was not found")
        dockerManager = DockerManager()
        container = dockerManager.search_instance(resource.container_id)
        res = {
            "id":resource.id,
            "container_id":resource.container_id,
            "resource":resource.resource,
            "config":resource.config,
            "is_running":True if container else False
        }
        return res

    @swagger.operation(
        nickname="delete"
    )
    @auth.login_required
    def delete(self,id):
        """删除指定id资源信息"""
        user = auth.current_user()
        resource = Resource.query.filter_by(user_id=user.id,id=id).first()
        if not resource:
            abort(404,"the item was not found")
        # 清空容器
        dockerManager = DockerManager()
        try:
            dockerManager.stop(resource.container_id)
            dockerManager.remove(resource.container_id)
        except:
            pass
        db_session.delete(resource)
        db_session.commit()
        return None,201

class UserItem(RS):

    @swagger.operation(
        nickname="post",
        parameters=[
            {
              "name": "username",
              "description": "username",
              "required": True,
              "allowMultiple": False,
              "dataType": "string",
              "paramType": "string"
            }
          ],
    )
    @auth.login_required
    def post(self):
        """创建用户"""
        data = request.json
        username = data.get("username")
        if not username:
            abort(400,"username must required!")
        res = {}
        user = auth.current_user()
        user = User(username=username)
        db_session.add(user)
        db_session.commit()
        res["id"] = user.id
        res["username"] = user.username
        res["token"] = user.token
        return res

api.add_resource(UserItem, '/user')
api.add_resource(ResourceList, '/resource_list')
api.add_resource(ResourceItem, '/resource/<string:id>')

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)