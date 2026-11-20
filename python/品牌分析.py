import pandas as pd
root=r"D:\real"
oct19=pd.read_csv(f"{root}/2019-Oct.csv")
dec19=pd.read_csv(f"{root}/2019-Dec.csv")
nov19=pd.read_csv(f"{root}/2019-Nov.csv")
feb20=pd.read_csv(f"{root}/2020-Feb.csv")
jan20=pd.read_csv(f"{root}/2020-Jan.csv")
all=pd.concat([oct19,dec19,nov19,feb20,jan20], ignore_index=True)
def check(df):
    df['event_time']=pd.to_datetime(df['event_time'])
    #统计行数和缺失值
    a=df
    none={
        '总行数':a,
        '缺失行':df.isna().sum()
    }
    #处理缺失值
    df=df.dropna(subset=['user_session'])
    df['brand']=df['brand'].fillna('unknown')
    df['category_code']=df['category_code'].fillna('unknown')
    #检查重复行
    dup=df.duplicated().sum()
    #去重前后对比
    dropdup=df.drop_duplicates()
    compare={
        '原始数据行数':a,
        '清洗后行数':len(dropdup)
    }
    #检查事件类型分布
    stat={
        '行数':dropdup['event_type'].value_counts(),
        '百分比':dropdup['event_type'].value_counts(normalize=True)
    }
    #检查时间范围
    time={
        '第一次浏览':dropdup['event_time'].min(),
        '最后一次浏览':dropdup['event_time'].max()
    }
    #检查价格是否存在异常
    price_check=dropdup['price'].describe()
    return none,dropdup,stat,time,price_check,compare

def check_price(df):
    a=int((df['price']<=0).sum())
    b=df[df['price']<0]['event_type'].value_counts()
    c=df[df['price']==0]['event_type'].value_counts()
    return a,b,c         

