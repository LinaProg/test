from hashlib import sha256
from datetime import datetime

def get_password(password: str) -> str:
    bytes_password = password.encode()
    return sha256(bytes_password).hexdigest()


def create_token(username: str,password: str) -> str:
    login_time = datetime.now()
    return sha256(username.encode()+password.encode()+str(login_time).encode()).hexdigest()

