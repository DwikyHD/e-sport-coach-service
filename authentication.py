from dotenv import dotenv_values
import jwt
from fastapi import (FastAPI, Depends, HTTPException, status)
from models import (User, Game, Coach, user_pydantic, user_pydanticIn, coach_pydantic,coach_pydanticIn, game_pydantic, game_pydanticIn)
from passlib.context import CryptContext

config_credentials = dict(dotenv_values(".env"))

pass_context = CryptContext(schemes=('bcrypt'), deprecated='auto')

def get_hash(password):
    return pass_context.hash(password)

async def verify_password(plain_password, hashed_password):
    return pass_context.verify(plain_password, hashed_password)

async def authenticate_user(username: str, password: str):
    user = await User.get(username = username)
    if user  and verify_password(password, user.password):
        return user
    return False

async def token_generator(username: str, password: str):
    user = await authenticate_user(username, password)
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {
        "id" : user.id,
        "username" : user.username
    }

    token = jwt.encode(token_data, config_credentials["SECRET"])
    return token

async def verify_token(token: str):
    try:
        payload = jwt.decode(token, config_credentials['SECRET'], algorithms = ['HS256'])
        user = await User.get(id = payload.get('id'))
    except:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user