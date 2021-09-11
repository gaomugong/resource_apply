
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, JSON,ForeignKey
from sqlalchemy.orm import relationship
from utils import generate_id

engine = create_engine('sqlite:////home/wb.pengjiayu/resource_apply/sql/data.db')
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()



def init_db():
    Base.metadata.create_all(bind=engine)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(128), unique=True, nullable=False)
    token = Column(String(256), unique=True, nullable=False)
    resource = relationship("Resource")

    def __init__(self, username=None):
        self.username = username
        self.token = generate_id()

    def __repr__(self):
        return '<User %r>' % self.username


class Resource(Base):
    __tablename__ = 'resource'
    id = Column(Integer, primary_key=True)
    resource = Column(String(128), nullable=False)
    container_id = Column(String(128), nullable=False)
    config = Column(JSON, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))

    def __init__(self, resource,config,user_id):
        self.resource = resource
        self.config = config
        self.user_id = user_id

    def __repr__(self):
        return '<Resource %r>' % self.resource


if __name__ == "__main__":
    init_db()