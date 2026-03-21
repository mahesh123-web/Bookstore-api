from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

#----------CONFIG-------------------
SECRET_KEY = "88e693d434edea50db3c680ef106ee6fff97c3cc04b7a6dab31b4659383c5182"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

#---------- Password Hashing------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def hash_password(password:str)->str:
    return pwd_context.hash(password[:72])

def verify_password(plain:str, hashed: str)->bool:
    return pwd_context.verify(plain[:72],hashed)

#-----------Fake User DB-----------------

fake_user_db={
    "ram":{
        "username":"ram",
        "hashed_password":hash_password("ram789"),
        "role":"admin"
    },
    "sham":{
        "username":"sham",
        "hashed_password":hash_password("sham102"),
        "role":"reader"
    }
}

#-------------Models-------------------

class Token (BaseModel):
    access_token : str
    token_type : str
    
class TokenData(BaseModel):
    username : Optional[str] = None
    
#----------Token Creation----------------

def create_access_token(data:dict)->str:
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(minutes = TOKEN_EXPIRE_MINUTES)
    payload.update({"exp":expire})
    return jwt.encode(payload, SECRET_KEY,algorithm=ALGORITHM)

#-------------Token Verification--------------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_error = HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid or Expired Token",
            headers = {"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_error
    except JWTError : 
        raise credentials_error
    
    user = fake_user_db.get(username)
    if user is None:
        raise credentials_error
    return user

#----------ROLE CHECK-----------------

def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Admin access required"
        )
    return current_user