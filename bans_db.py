banned = set()

def is_banned(uid):
    return uid in banned

def ban(uid):
    banned.add(uid)

def unban(uid):
    banned.discard(uid)