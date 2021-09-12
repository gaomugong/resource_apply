
import docker
import threading
from utils import singletonDecorator,get_free_port,get_host_ip
from docker.errors import ImageNotFound,NotFound 

@singletonDecorator
class DockerManager(object):
    _lock = threading.Lock() # 防止端口被占用

    def __init__(self):
        self.client = docker.from_env(timeout=15)

    def reset_client(self):
        pass

    def search_image(self,image_name):
        """查找镜像"""
        try:
            return self.client.images.get(image_name)
        except ImageNotFound as e:
            return False

    def search_instance(self,container_id,is_running=False):
        """查找容器"""
        try:
            container = self.client.containers.get(container_id)
            return container 
        except NotFound as e:
            return False

    def pull(self,image_name):
        """pull镜像"""
        try:
            return self.client.images.pull(image_name)
        except Exception as e:
            raise e
            return False

    def run(self,container_name,image_tag,config={}):
        """运行容器"""
        params = {}

        # 端口映射
        inside_port = config.get("inside_port")
        port = None
        if inside_port:
            port = get_free_port()
            ports = {"{}/tcp".format(inside_port): port}
            params["ports"] = ports

        # 环境变量 
        environment = config.get("environment")
        if environment:
            params["environment"] = environment

        container = self.client.containers.run(image=image_tag,name=container_name,
                                      detach=True,**params)
        return {
            "container_id":container.id,
            "addr":get_host_ip(),
            "port":port,
            "config":config
        }

    def stop(self,container):
        """停止容器"""
        try:
            container = self.search_instance(container)
            container.stop()
        except Exception as e:
            return

    def remove(self,container):
        """删除容器"""
        try:
            container = self.search_instance(container)
            container.remove()
        except Exception as e:
            return

    def remove_image(self,image_name):
        """删除镜像"""
        self.client.images.remove(image_name)

    def create(self,image_name,tag,container_name,config={}):
        # 查找是否存在镜像
        tag = tag if tag else "latest"
        image_tag = "{}:{}".format(image_name,tag)
        if not self.search_image(image_tag):
            if not self.pull(image_tag):
                return False
        # 开启并运行容器
        self.__class__._lock.acquire()
        try:
            res = self.run(container_name,image_tag,config)
            self.__class__._lock.release()
            return res
        except Exception as e:
            self.__class__._lock.release()
            raise e


if __name__ == "__main__":
    d = DockerManager()
    container = d.create("mysql","5.7","mysql2",config={"inside_port":3306,"environment":{"MYSQL_ROOT_PASSWORD":"111"}})
    d.stop(container.id)
    d.remove(container.id)
    # print(d.pull("nginx"))
    # d.remove_image("nginx")