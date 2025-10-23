import os,json,pandas as pd
RAW_DIR='ride_data/raw'
def _tss(meta,ftp=222):
    dur=(meta.get('moving_time_s',0))/3600; pw=meta.get('average_watts',0)
    if dur<=0 or pw<=0: return 0
    return dur*((pw/ftp)**2)*100
def build_tss_dataframe(rides,ftp=222):
    rec=[]
    for _,r in rides.iterrows():
        data=json.load(open(os.path.join(RAW_DIR,r['File'])))
        m=data.get('_meta',{})
        if not m.get('start_date'): continue
        rec.append({'date':pd.to_datetime(m['start_date']),'TSS':_tss(m,ftp)})
    df=pd.DataFrame(rec).sort_values('date')
    if df.empty: return df
    df=df.groupby(df['date'].dt.date,as_index=False)['TSS'].sum()
    df['date']=pd.to_datetime(df['date'])
    df['CTL']=df['TSS'].rolling(42,min_periods=1).mean()
    df['ATL']=df['TSS'].rolling(7,min_periods=1).mean()
    df['TSB']=df['CTL']-df['ATL']
    return df
