from models import leave_model as LM
def list_for(user):
    if user.get('role')=='admin': return LM.list_for_user(None)
    return LM.list_for_user(user.get('username'))
def create(user,payload): payload['username']=user['username']; payload['status']='Pending'; return LM.create(payload)
def update(user,leave_id,updates):
    leaves = LM.list_for_user(None)
    for l in leaves:
        if l.get('id')==leave_id:
            if user.get('role')=='admin' or l.get('username')==user.get('username'):
                return LM.update(leave_id, updates)
    return None
def delete(user,leave_id):
    leaves = LM.list_for_user(None)
    for l in leaves:
        if l.get('id')==leave_id:
            if user.get('role')=='admin' or l.get('username')==user.get('username'):
                return LM.delete(leave_id)
    return None
