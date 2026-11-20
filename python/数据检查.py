import pandas as pd
import os
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
    return res,all_d,daily,easy_funnel,strict_funnel,strict_funnel_counts

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
a1,b1,c1,d1,e1,f1=clean(all)
all_purchase=b1[b1['event_type']=='purchase']
any_brand=pd.DataFrame({
    'hang':('brand','categroy_code'),
    '未知数量':(len(all_purchase[all_purchase['brand']=='unknown']),len(all_purchase[all_purchase['category_code']=='unknown']))
})
any_brand['未知比例']=any_brand['未知数量']/len(all_purchase)
print(any_brand)
a=all_purchase.groupby('product_id').agg(
    销售额=('price','sum'),
    销售量=('product_id','count')
)
root1=r"D:\real\清洗后数据"
f1.to_csv(os.path.join(root1,'严格漏斗环节计数.csv'))
a.sort_values('销售额',ascending=False).head(10).to_csv(os.path.join(root1,'product销售额.csv'))
a.sort_values('销售量',ascending=False).head(10).to_csv(os.path.join(root1,'product销售量.csv'))
b=all_purchase[all_purchase['brand']!='unknown'].groupby('brand').agg(
    销售额=('price','sum'),
    销售量=('brand','count'),
    产品数=('product_id','nunique')
)
b.sort_values('销售额',ascending=False).head(10).to_csv(os.path.join(root1,'brand销售额.csv'))
b.sort_values('销售量',ascending=False).head(10).to_csv(os.path.join(root1,'brand销售量.csv'))

#复购分析
d=all_purchase.groupby('user_id').agg(
    消费金额=('price','sum'),
    消费次数=('user_id','count')
)
e=pd.DataFrame({'复购用户数':[len(d[d['消费次数']>1])],
   '复购用户比例':[len(d[d['消费次数']>1])/len(d)]})
print(e)