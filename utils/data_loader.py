import os, json, pandas as pd
RAW_DIR='ride_data/raw'
def list_rides():
    rows=[]
    if not os.path.exists(RAW_DIR): return pd.DataFrame()
    for f in sorted(os.listdir(RAW_DIR),reverse=True):
        if not f.endswith('.json'): continue
        try: data=json.load(open(os.path.join(RAW_DIR,f)))
        except: continue
        m=data.get('_meta',{})
        if not m or not m.get('name') or m['name'].lower().startswith('unnamed'): continue
        rows.append({'Activity':m['name'],'File':f,
                     'Distance (mi)':round((m.get('distance_m',0))/1609.34,2),
                     'Avg Power (W)':m.get('average_watts',0),
                     'Avg HR (bpm)':m.get('average_heartrate',0)})
    return pd.DataFrame(rows)
def stream_values(df,key):
    vals=[]
    for _,r in df.iterrows():
        p=os.path.join(RAW_DIR,r['File'])
        try:
            d=json.load(open(p))
            if key in d: vals+=d[key]['data']
        except: continue
    return vals
