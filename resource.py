
from dockerManager import DockerManager
from utils import generate_id

class Resource(object):
    def __init__(self,config={}):
        self.docker_manager = DockerManager()
        self.config = config
        self.image_name = None
        self.tag = None
        self.container_name = None

    def create(self):
        container = self.docker_manager.create(self.image_name,self.tag,self.container_name,self.config)
        return container

    def clear(self):
        try:
            self.docker_manager.stop(self.container_name)
            self.docker_manager.remove(self.container_name)
        except Exception as e:
            raise e

class MysqlResource(Resource):
    def __init__(self,*args,**kargs):
        super(MysqlResource,self).__init__(*args,**kargs)
        self.image_name = "mysql"
        self.tag = "5.7"
        self.container_name = generate_id()
        self.mysql_password = generate_id()

        self.config["inside_port"] = 3306
        self.config["environment"]= {
            "MYSQL_ROOT_PASSWORD":self.mysql_password,
            "MYSQL_DATABASE":self.config.pop("MYSQL_DATABASE")
        }

    def create(self):
        container_data = super().create()
        container_data["MYSQL_USER"] = "root"
        return container_data

class RedisResource(Resource):
    def __init__(self,*args,**kargs):
        super(RedisResource,self).__init__(*args,**kargs)
        self.image_name = "redis"
        self.tag = "latest"
        self.container_name = generate_id()
        self.mysql_password = generate_id()

        self.config["inside_port"] = 6379
        self.config["--requirepass"] = self.mysql_password

    def create(self):
        container_data = super().create()
        return container_data

if __name__ == "__main__":
    config = {
        "MYSQL_DATABASE":"haha"
    }
    resource = MysqlResource(config)
    # resource = RedisResource()
    print(resource.create())
    resource.clear()