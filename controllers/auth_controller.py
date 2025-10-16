from models import user_model as UM
def login(u,p): return UM.get_user(u) if UM.verify(u,p) else None
def register(u,p,role='employee'): return UM.add_user(u,p,role)
