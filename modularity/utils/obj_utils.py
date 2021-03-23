def incDic(dic, key, val):
    dic[key] = val

def appendDic(dic, key, val):
    if key in dic:
        dic[key].append(val)
    else:
        dic[key] = [val]

def incDicWithAdd(dic, key, val):
    origin_data = dic.get(key, set())
    # origin_data = set(origin_data)
    origin_data.add(val)
    dic[key] = origin_data

def incDicWithWeightAdd(dic, key, val=None):
    origin_data = dic.get(key, 0)
    if val is None:
        val = 1
    origin_data += val
    dic[key] = origin_data

def node2idx(dic, key):
    if not key in dic:
        origin_size = len(dic)
        dic[key] = origin_size
        return origin_size
    else:
        return dic[key]
        