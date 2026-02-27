from app import config

def get_vip_level(wagered: int):
    lv = config.VIP_LEVELS[0]
    for l in config.VIP_LEVELS:
        if wagered >= l['min']:
            lv = l
    return lv
