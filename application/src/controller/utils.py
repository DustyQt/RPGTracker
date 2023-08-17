def sum_dict(dict, key, value):
    if key in dict:
        dict[key]+=value
    else: 
        dict[key] = value