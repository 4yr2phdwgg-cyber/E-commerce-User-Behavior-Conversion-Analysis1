import pandas as pd
import os
root1=r"D:\real\清洗后数据"
def clean(df):
    #处理缺失值
    all=df.dropna(subset=['user_session'])
    all['brand']=all['brand'].fillna('unknown')
    all['category_code']=all['category_code'].fillna('unknown')
    #去重（负价格和0价格存在较少，购买中的负价格和零价格，可能是退款和冲正以及赠品，不删除，其它三种行动中的不为正数的价格，不影响，保留）
    all_d=all.drop_duplicates().copy()
    a=all_d['event_type'].value_counts()
    b=all_d['event_type'].value_counts(normalize=True)
    res=pd.DataFrame({    
    '事件数量': a,    
    '事件占比': b
    })
    #每天事件数和访客量
    
    daily_user=all_d.groupby('date')['user_id'].nunique()
    daily_event=all_d.groupby(['date','event_type']).size().unstack(fill_value=0)
    daily=daily_event.merge(daily_user,on='date',how='inner')
    daily['events_per_user']=(daily[['cart','purchase','remove_from_cart','view']].sum(axis=1)/daily['user_id'])
    #粗滤漏斗
    session_event=all_d.groupby('user_session')['event_type'].value_counts().unstack(fill_value=0).gt(0)
    view_session=session_event['view'].sum()
    cart_session=session_event['cart'].sum() 
    purchase_session=session_event['purchase'].sum()
    vc=round(cart_session/view_session,4)
    cp=round(purchase_session/cart_session,4)
    vp=round(purchase_session/view_session,4)
    easy_funnel={
        '环节':('浏览——加购','加购——购买','浏览——购买'),
        '转换率':(vc,cp,vp),
        '流失率':(1-vc,1-cp,1-vp)
    }
    #严格漏斗
    session_time=all_d.groupby(['user_session','event_type'])['event_time'].min().unstack()
    s1=session_time.dropna(subset=['view'])
    s2=s1[s1['cart']>s1['view']]
    s3=s2[s2['purchase']>s2['cart']]

    strict_funnel_counts=pd.Series({
       'view':len(s1),
       'cart':len(s2),
       'purchase':len(s3)
    })
    #相邻环节转化率
    view_to_cart=round(strict_funnel_counts['cart']/strict_funnel_counts['view'],4)
    cart_to_purchase=round(strict_funnel_counts['purchase']/strict_funnel_counts['cart'],4)
    #整体转化率
    view_to_purchase=round(strict_funnel_counts['purchase']/strict_funnel_counts['view'],4)
    strict_funnel={
        '环节':('浏览——加购','加购——购买','浏览——购买'),
        '转换率':(view_to_cart,cart_to_purchase,view_to_purchase),
        '流失率':(1-view_to_cart,1-cart_to_purchase,1-view_to_purchase)
    }
    return res,all_d,daily,easy_funnel,strict_funnel

root=r"D:\real"
oct19=pd.read_csv(f"{root}/2019-Oct.csv")
dec19=pd.read_csv(f"{root}/2019-Dec.csv")
nov19=pd.read_csv(f"{root}/2019-Nov.csv")
feb20=pd.read_csv(f"{root}/2020-Feb.csv")
jan20=pd.read_csv(f"{root}/2020-Jan.csv")
all=pd.concat([oct19,dec19,nov19,feb20,jan20], ignore_index=True)
all['event_time']=pd.to_datetime(all['event_time'])
all['date']=all['event_time'].dt.date
#整体表现
a1,b1,c1,d1,e1=clean(all)
whole={
    '用户数':b1['user_id'].nunique(),
    '会话数':b1['user_session'].nunique(),
    '事件数':len(b1)
}
a1.to_csv(os.path.join(root1,'a.csv'))
pd.DataFrame([whole]).to_csv(os.path.join(root1,'whole.csv'),index=False,encoding='utf-8')
pd.DataFrame(d1).to_csv(os.path.join(root1,'d.csv'),index=False,encoding='utf-8')
pd.DataFrame(e1).to_csv(os.path.join(root1,'e.csv'),index=False,encoding='utf-8')
#月份趋势
def every(df):
    df['event_time']=pd.to_datetime(df['event_time'])
    df['date']=df['event_time'].dt.date
    a,b,c,d,e=clean(df)
    return a,b,c,d,pd.DataFrame(e)

oct19_a,oct19_b,oct19_c,oct19_d,oct19_e=every(oct19)
nov19_a,nov19_b,nov19_c,nov19_d,nov19_e=every(nov19)
dec19_a,dec19_b,dec19_c,dec19_d,dec19_e=every(dec19)
jan20_a,jan20_b,jan20_c,jan20_d,jan20_e=every(jan20)
feb20_a,feb20_b,feb20_c,feb20_d,feb20_e=every(feb20)

def pay(df):
    a=df[df['event_type']=='purchase']
    b=a['price'].sum()
    return round(b,2)
def repeat(df):
    a=df[df['event_type']=='purchase']
    c=(a['user_id'].value_counts()>=2).sum()
    return c
def wh(df):
    whole={
          '用户数':df['user_id'].nunique(),
          '会话数':df['user_session'].nunique(),
          '事件数':len(df)
        }
    return whole
mouth_any={
    '月份':('2019_10','2019_11','2019_12','2020_01','2020_02'),
    '购买金额':(pay(oct19),pay(nov19),pay(dec19),pay(jan20),pay(feb20)),
    '活跃用户数':(wh(oct19_b)['用户数'],wh(nov19_b)['用户数'],wh(dec19_b)['用户数'],wh(jan20_b)['用户数'],wh(feb20_b)['用户数']),
    '会话数':(wh(oct19_b)['会话数'],wh(nov19_b)['会话数'],wh(dec19_b)['会话数'],wh(jan20_b)['会话数'],wh(feb20_b)['会话数']),
    '用户活跃度':(wh(oct19_b)['事件数']/wh(oct19_b)['用户数'],wh(nov19_b)['事件数']/wh(nov19_b)['用户数'],wh(dec19_b)['事件数']/wh(dec19_b)['用户数'],wh(jan20_b)['事件数']/wh(jan20_b)['用户数'],wh(feb20_b)['事件数']/wh(feb20_b)['用户数']),
    '复购数':(repeat(oct19),repeat(nov19),repeat(dec19),repeat(jan20),repeat(feb20))
}
mouth_funnel={
    '月份':('2019_10','2019_11','2019_12','2020_01','2020_02'),
    '浏览——加购':(oct19_e[oct19_e['环节']=='浏览——加购']['转换率'].iloc[0],nov19_e[nov19_e['环节']=='浏览——加购']['转换率'].iloc[0],dec19_e[dec19_e['环节']=='浏览——加购']['转换率'].iloc[0],jan20_e[jan20_e['环节']=='浏览——加购']['转换率'].iloc[0],feb20_e[feb20_e['环节']=='浏览——加购']['转换率'].iloc[0]),
    '加购——购买':(oct19_e[oct19_e['环节']=='加购——购买']['转换率'].iloc[0],nov19_e[nov19_e['环节']=='加购——购买']['转换率'].iloc[0],dec19_e[dec19_e['环节']=='加购——购买']['转换率'].iloc[0],jan20_e[jan20_e['环节']=='加购——购买']['转换率'].iloc[0],feb20_e[feb20_e['环节']=='加购——购买']['转换率'].iloc[0]),
    '浏览——购买':(oct19_e[oct19_e['环节']=='浏览——购买']['转换率'].iloc[0],nov19_e[nov19_e['环节']=='浏览——购买']['转换率'].iloc[0],dec19_e[dec19_e['环节']=='浏览——购买']['转换率'].iloc[0],jan20_e[jan20_e['环节']=='浏览——购买']['转换率'].iloc[0],feb20_e[feb20_e['环节']=='浏览——购买']['转换率'].iloc[0])
}

pd.DataFrame(mouth_any).to_csv(os.path.join(root1,'mouth_any.csv'),index=False,encoding='utf-8')
pd.DataFrame(mouth_funnel).to_csv(os.path.join(root1,'mouth_funnel.csv'),index=False,encoding='utf-8')



