
import jwt
from datetime import datetime, timedelta


# TODOAUTH: this cannot stay in the code
# TODOAUTH: use CCAT_API_KEY?
SECRET_KEY = "sfdjgnsiobesiubib54ku3vku6v553kuv6uv354uvk5yuvtku5"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # TODOAUTH find reasonable expire


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def verify_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False