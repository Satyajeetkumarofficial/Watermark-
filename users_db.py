users = {}
stats = {
    "users": set(),
    "processed": 0
}

def get_user(uid):
    stats["users"].add(uid)

    if uid not in users:
        users[uid] = {
            "rename": None,
            "thumb": None,
            "scale": DEFAULT_SCALE if "DEFAULT_SCALE" in globals() else 20,
            "position": "bottom-center",
            "awaiting": None,
            "last_video_msg": None
        }
    return users[uid]
