
from database import User
from database import db_session

if __name__=="__main__":
    u = User('admin2')
    db_session.add(u)
    db_session.commit()
    print({
        "username":u.username,
        "token":u.token
    })