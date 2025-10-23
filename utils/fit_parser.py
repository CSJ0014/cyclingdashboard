from fitparse import FitFile
import pandas as pd, numpy as np, io, time
def parse_fit_to_json(file):
    f=FitFile(io.BytesIO(file.read()))
    t,p,h,s,d=[],[],[],[],[]
    start=None
    for r in f.get_messages('record'):
        v={d.name:d.value for d in r}
        if 'timestamp' in v:
            t.append(pd.to_datetime(v['timestamp']).tz_localize(None))
            if start is None: start=t[-1]
        p.append(float(v.get('power',np.nan)))
        h.append(float(v.get('heart_rate',np.nan)))
        s.append(float(v.get('speed',np.nan)))
        d.append(float(v.get('distance',np.nan)))
    if not t: raise ValueError('No timestamp data.')
    t0=pd.Series(t); time_s=(t0-t0.iloc[0]).dt.total_seconds().tolist()
    avg_pw=np.nanmean(p); avg_hr=np.nanmean(h); dist=np.nanmax(d)
    dur=time_s[-1] if time_s else 0
    meta={"id":str(int(time.time())),"name":file.name.replace('.fit',''),
          "distance_m":float(dist),"moving_time_s":float(dur),
          "average_watts":float(avg_pw),"average_heartrate":float(avg_hr),
          "start_date":pd.to_datetime(start).isoformat(),"type":"Ride"}
    return {"time":{"data":time_s},"watts":{"data":p},"heartrate":{"data":h},
            "velocity_smooth":{"data":s},"distance":{"data":d},"_meta":meta}
