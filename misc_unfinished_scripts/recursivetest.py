scope_set = set()
def grab_key_value(x):
    if isinstance(x, list):
        for y in x:
            grab_key_value(y)
    elif isinstance(x, dict):
        for k,v in x.items():
            if isinstance(v, list):
                 grab_key_value(v)
            elif isinstance(v, dict):
                 grab_key_value(v)
            else:
               if not x['dn'] in scope_set:
                    scope_set.add(x['dn'])
                    print(x['dn'],[x['scope'],x['seg'])
               else:
                   continue
