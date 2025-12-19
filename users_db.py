users = {}

def get_user(uid):
    if uid not in users:
        users[uid] = {
            "rename": None,
            "thumb": None,
            "scale": 20,
            "position": "bottom-center",
            "awaiting": None,
            "last": None
        }
    return users[uid]