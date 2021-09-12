
import threading
import socket 
import uuid

def singletonDecorator(cls,*args,**kwargs):
    """单例装饰器
    """
    instance = {}
    _lock = threading.Lock()
    
    def wrapperSingleton(*args,**kwargs):
        _lock.acquire()  # 防止初始化时并发生成实例
        try:
            if cls not in instance:
                instance[cls] = cls(*args,**kwargs)
        except Exception as e:
            _lock.release()
            raise e
        _lock.release()
        return instance[cls]
    
    return wrapperSingleton


def get_free_port():  
    """获取没被绑定的端口"""
    sock = socket.socket()
    sock.bind(('', 0))
    ip, port = sock.getsockname()
    sock.close()
    return port

def generate_id():
    """生成唯一id函数"""
    uid = uuid.uuid1()
    return uid.hex

def get_host_ip():
    """获取本地id地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
 
    return ip

if __name__ == "__main__":
    print(get_host_ip())