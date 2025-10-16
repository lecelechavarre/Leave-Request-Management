from utils import load_json, save_json
import os, uuid
LEAVES_FILE = os.path.join(os.path.dirname(__file__),'..','data','leaves.json')
def _ensure():
    os.makedirs(os.path.dirname(LEAVES_FILE),exist_ok=True)
    if not os.path.exists(LEAVES_FILE): save_json(LEAVES_FILE,[])
def list_all(): _ensure(); return load_json(LEAVES_FILE) or []
def list_for_user(username=None):
    items = list_all()
    if username: return [i for i in items if i.get('username')==username]
    return items
def create(record):
    _ensure(); items=list_all(); record['id']=str(uuid.uuid4())[:8]; items.append(record); save_json(LEAVES_FILE, items); return record
def update(record_id, updates):
    _ensure(); items=list_all()
    for i,it in enumerate(items):
        if it.get('id')==record_id:
            items[i].update(updates); save_json(LEAVES_FILE, items); return items[i]
    return None
def delete(record_id):
    _ensure(); items=list_all(); new=[it for it in items if it.get('id')!=record_id]; save_json(LEAVES_FILE,new); return True
