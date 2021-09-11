
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
        except:
            pass

class MysqlResource(Resource):
    def __init__(self,*args,**kargs):
        super(MysqlResource,self).__init__(*args,**kargs)
        self.image_name = "mysql"
        self.tag = "5.7"
        self.container_name = generate_id()
        self.mysql_password = generate_id()
        self.config = {
            "environment":self.config
        }
        self.config["inside_port"] = 3306
        self.config["environment"]["MYSQL_ROOT_PASSWORD"] = self.mysql_password

    def create(self):
        container_data = super().create()
        return {
            "container_id":container_data["container"].id,
            "port":container_data["params"].get("port")
        }

class RedisResource(Resource):
    def __init__(self,*args,**kargs):
        super(RedisResource,self).__init__(*args,**kargs)
        self.image_name = "redis"
        self.tag = "lastest"
        self.container_name = generate_id()
        self.mysql_password = generate_id()
        self.config = {
            "environment":self.config
        }
        self.config["inside_port"] = 3306
        self.config["environment"]["MYSQL_ROOT_PASSWORD"] = self.mysql_password

    def create(self):
        container = super().create()
        return container

if __name__ == "__main__":
    resource = MysqlResource()
    # resource = RedisResource()
    print(resource.create())
    resource.clear()