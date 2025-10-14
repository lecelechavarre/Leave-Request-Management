from models.leave_model import LeaveModel

class LeaveController:
    @staticmethod
    def list(user):
        if user.get('role') == 'admin':
            return LeaveModel.list_for_user(None)
        return LeaveModel.list_for_user(user['username'])

    @staticmethod
    def create(user, payload):
        payload['username'] = user['username']
        payload['status'] = 'Pending'
        return LeaveModel.create(payload)

    @staticmethod
    def update(user, leave_id, updates):
        leaves = LeaveModel.list_for_user(None)
        for l in leaves:
            if l['id'] == leave_id:
                if user['role'] == 'admin' or l['username'] == user['username']:
                    return LeaveModel.update(leave_id, updates)
        return None

    @staticmethod
    def delete(user, leave_id):
        leaves = LeaveModel.list_for_user(None)
        for l in leaves:
            if l['id'] == leave_id:
                if user['role'] == 'admin' or l['username'] == user['username']:
                    return LeaveModel.delete(leave_id)
        return None
