import random
from app import config

def base_spin(bet: int, double_chance: bool = False):
    g = []
    sc = 0
    scatter_odds = 0.10 if double_chance else 0.05
    for _ in range(30):
        if random.random() < scatter_odds:
            g.append(config.SCATTER)
            sc += 1
        else:
            g.append(random.choice(config.BASE_SYMS))
    
    co = {}
    for s in g:
        if s != config.SCATTER:
            co[s] = co.get(s, 0) + 1
            
    m = 0.0
    for _, cnt in co.items():
        if cnt >= 12: m += 5.0
        elif cnt >= 8: m += 1.5
        
    return {
        "grid": g,
        "winnings": int(bet * m),
        "scatter_count": sc,
        "triggered_bonus": sc >= 4
    }

def _get_bomb_multiplier():
    t = sum(w for w, _ in config.BOMB_WEIGHTS)
    r = random.uniform(0, t)
    c = 0
    for w, m in config.BOMB_WEIGHTS:
        c += w
        if r <= c: return m
    return 2

def bonus_spin(bet: int):
    g = []
    bombs = []
    sc = 0
    for i in range(30):
        r = random.random()
        if r < 0.03:
            g.append(config.SCATTER)
            sc += 1
        elif r < 0.13:
            g.append(config.BOMB)
            bombs.append(i)
        else:
            g.append(random.choice(config.BONUS_SYMS))
            
    co = {}
    for s in g:
        if s not in (config.SCATTER, config.BOMB):
            co[s] = co.get(s, 0) + 1
            
    m = 0.0
    ws = {}
    for sym, cnt in co.items():
        if cnt >= 12: m += 10.0; ws[sym] = cnt
        elif cnt >= 10: m += 5.0; ws[sym] = cnt
        elif cnt >= 8: m += 3.0; ws[sym] = cnt
        elif cnt >= 6: m += 2.0; ws[sym] = cnt
        
    bw = int(bet * m)
    bl = []
    tbm = 1
    for p in bombs:
        bm = _get_bomb_multiplier()
        bl.append({"pos": p, "mult": bm})
        tbm *= bm
        
    fw = bw * tbm if bw > 0 else 0
    rt = sc >= 3
    
    return {
        "grid": g,
        "winnings": int(fw),
        "bombs": bl,
        "total_bomb_mult": tbm,
        "base_win": bw,
        "scatter_count": sc,
        "retrigger": rt,
        "extra_spins": 5 if rt else 0,
        "winning_symbols": ws
    }

def full_bonus(bet: int):
    ts = 10
    d = 0
    res = []
    tw = 0
    while d < ts:
        r = bonus_spin(bet)
        d += 1
        tw += r["winnings"]
        r.update({"spin_number": d, "total_spins": ts, "running_total": tw})
        res.append(r)
        if r["retrigger"]:
            ts = min(ts + r["extra_spins"], 30)
    return {"spins": res, "total_win": tw, "total_spins_played": d}

def spin_wheel():
    t = sum(w for w, _, _ in config.WHEEL_PRIZES)
    r = random.uniform(0, t)
    c = 0
    for w, pt, v in config.WHEEL_PRIZES:
        c += w
        if r <= c: return {"type": pt, "value": v}
    return {"type": "coins", "value": 5}
