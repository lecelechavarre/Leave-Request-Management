from utils import load_json, save_json
import os, uuid

LEAVES_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'leaves.json')

class LeaveModel:
    @classmethod
    def _ensure_file(cls):
        os.makedirs(os.path.dirname(LEAVES_FILE), exist_ok=True)
        if not os.path.exists(LEAVES_FILE):
            save_json(LEAVES_FILE, [])

    @classmethod
    def list_for_user(cls, username=None):
        cls._ensure_file()
        items = load_json(LEAVES_FILE)
        if username:
            return [i for i in items if i['username'] == username]
        return items

    @classmethod
    def create(cls, record):
        cls._ensure_file()
        items = load_json(LEAVES_FILE)
        record['id'] = str(uuid.uuid4())[:8]
        items.append(record)
        save_json(LEAVES_FILE, items)
        return record

    @classmethod
    def update(cls, record_id, updates):
        cls._ensure_file()
        items = load_json(LEAVES_FILE)
        for i, it in enumerate(items):
            if it['id'] == record_id:
                items[i].update(updates)
                save_json(LEAVES_FILE, items)
                return items[i]
        return None

    @classmethod
    def delete(cls, record_id):
        cls._ensure_file()
        items = load_json(LEAVES_FILE)
        new = [it for it in items if it['id'] != record_id]
        save_json(LEAVES_FILE, new)
        return True
