import bcrypt


def hash_password(password):
    byte_pw=password.encode("utf-8")
    return bcrypt.hashpw(byte_pw,bcrypt.gensalt()).decode("utf-8")

def verify_password(password,password_hash):
    byte_pw=password.encode("utf-8")
    
    return bcrypt.checkpw(byte_pw,password_hash.encode("utf-8"))

def encode_jwt():
    pass

def decode_jwt():
    pass
