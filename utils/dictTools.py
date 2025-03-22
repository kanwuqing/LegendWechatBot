def get_key(d: dict, value, idx = 0):
    res = []
    for k, v in d.items():
        if v == value:
            res.append(k)
    if len(res) == 0:
        return None
    try:
        return res[idx]
    except IndexError:
        return res[0]

def get_keys(d: dict, value):
    res = []
    for k, v in d.items():
        if v == value:
            res.append(k)
    if len(res) == 0:
        return None
    return res