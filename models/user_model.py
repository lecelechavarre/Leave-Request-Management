from utils import load_json, save_json, hash_password, verify_password
import os
USERS_FILE = os.path.join(os.path.dirname(__file__),'..','data','users.json')
def _ensure():
    os.makedirs(os.path.dirname(USERS_FILE),exist_ok=True)
    if not os.path.exists(USERS_FILE) or os.path.getsize(USERS_FILE)==0:
        save_json(USERS_FILE,[{'username':'admin','password':hash_password('admin'),'role':'admin'},{'username':'employee','password':hash_password('employee'),'role':'employee'}])
def load_all():
    _ensure(); return load_json(USERS_FILE) or []
def get_user(username):
    for u in load_all():
        if u.get('username')==username: return u
    return None
def verify(username,password):
    u=get_user(username); return False if not u else verify_password(password,u.get('password',''))
def add_user(username,password,role='employee'):
    _ensure()
    if get_user(username): return False
    users = load_json(USERS_FILE) or []
    users.append({'username':username,'password':hash_password(password),'role':role})
    save_json(USERS_FILE, users); return True
