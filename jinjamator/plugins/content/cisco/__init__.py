import re
def analyze_interface_name(shortname,result_prefix='',default_interface_prefix='Ethernet'):
    shortname=shortname.lower().strip()
    if not shortname:
        log.error(f'cisco.analyze_interface_name: no shortname supplied')
        return {}
    is_nxos=False
    is_ios=False
    _rgx=r'(?P<prefix>\D+)(?P<a>\d+)/?(?P<b>\d+)?/?(?P<c>\d*)(?:\.(?P<l3_sub_interface>))?'
    try:
        _res=re.match(_rgx,shortname).groupdict()
    except AttributeError as err:
        log.error(f'cisco.analyze_interface_name: shortname "{shortname}" does not match {_rgx}')
    except Exception as err:
        log.error(f'cisco.analyze_interface_name: shortname "{shortname}" triggers exception')
        raise err
    
    if not _res['prefix']:
        _res['prefix']=default_interface_prefix

    prefix=_res['prefix'].strip().lower()

    if re.match(r"^e[thernet]?\d.*", shortname):
        is_nxos=True
        prefix="Ethernet"
    elif re.match(r"^gi[gabitethernet]?\d.*", shortname):
        is_ios=True
        prefix="GigabitEthernet"
    elif re.match(r"^te[ngigabitethernet]?\d.*", shortname):
        is_ios=True
        prefix="TenGigabitEthernet"
    elif re.match(r"^tw[entyfifengigabitethernet]?\d.*", shortname):
        is_ios=True
        prefix="TwentyfifeGigabitEthernet"
    elif re.match(r"^fo[rtygigabitethernet]?\d.*", shortname):
        is_ios=True
        prefix="FortyfifeGigabitEthernet"
    elif re.match(r"^hu[ndredgigabitethernet]?\d.*", shortname):
        is_ios=True
        prefix="HundredGigabitEthernet"
    elif re.match(r"^fa[ndredgigabitethernet]?\d.*", shortname):
        is_ios=True
        prefix="FastEthernet"
    elif re.match(r"^vl[an]?\d.*", shortname):
        is_ios=True
        prefix="Vlan"
    elif re.match(r"^po[rt-channel]?\d.*", shortname):
        is_ios=True
        prefix="port-channel"
    

    retval={
         'prefix':prefix,
         'chassis': 1,
         'card': None,
         'port' : None,
         'lane' : None,
         'is_nxos':is_nxos,
         'is_ios':is_ios,
         'is_fex':False,
         'is_l3_subinterface':False,
         'is_breakout_interface':False,
         'name': ""
    }
    
    if not _res['b'] and  not _res['c']:
        retval['port']=int(_res['a'])
        retval['name']=f"{retval['prefix']}{retval['port']}"
    if _res['b'] and  not _res['c']:
        retval['card']=int(_res['a'])
        retval['port']=int(_res['b'])
        retval['name']=f"{retval['prefix']}{retval['card']}/{retval['port']}"
    if _res['b'] and _res['c']:
        tmp=int(_res['a'])
        
        if is_nxos:
            if tmp > 99:
                retval['is_fex']=True
                retval['chassis']=tmp
                retval['card']=int(_res['b'])
                retval['port']=int(_res['c'])
                retval['name']=f"{retval['prefix']}{retval['chassis']}/{retval['card']}/{retval['port']}"
            else:
                retval['is_breakout_interface']=True
                retval['card']=tmp
                retval['port']=int(_res['b'])
                retval['lane']=int(_res['a'])
                retval['name']=f"{retval['prefix']}{retval['card']}/{retval['port']}/{retval['lane']}"
        if is_ios:
                retval['chassis']=tmp
                retval['card']=int(_res['b'])
                retval['port']=int(_res['c'])            
                retval['name']=f"{retval['prefix']}{retval['chassis']}/{retval['card']}/{retval['port']}"
                

    if _res['l3_sub_interface']:
        _res['is_l3_subinterface']=True
        retval['name']=f"{retval['name']}.{_res['l3_sub_interface']}"
    
    if result_prefix:
        tmp={}
        for k,v in retval.items():
            tmp[f'{result_prefix}{k}']=v
        return tmp

    return(retval)


