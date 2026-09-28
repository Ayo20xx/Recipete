from uuid import UUID

import bcrypt
import jwt

from app.core.config import settings


def hash_password(password):
    byte_pw=password.encode("utf-8")
    return bcrypt.hashpw(byte_pw,bcrypt.gensalt()).decode("utf-8")

def verify_password(password,password_hash):
    byte_pw=password.encode("utf-8")
    
    return bcrypt.checkpw(byte_pw,password_hash.encode("utf-8"))

def encode_jwt(id:UUID):
    return jwt.encode({"sub":id},settings.secret,algorithm="HS256")
    

def decode_jwt(jwt):
    return jwt.decode(jwt,settings.secret,algorithm="HS256")