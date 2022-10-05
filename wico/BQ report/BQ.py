import mariadb
import pandas.io.sql as sql
import plotly.express as px
from dash import Dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
import datetime
from datetime import timedelta
import pprint
import webbrowser
import pandas as pd
import numpy as np


mariadb_conn = mariadb.connect( 
user="hewei", 
password="wico2022", 
host="sunnyho.f3322.net", 
port=3306, 
database="pyytest" )


t=datetime.datetime.strftime(datetime.datetime.now()-timedelta(days=1), "%Y-%m-%d")
end_date=input("直接回车查询昨天的日报，如需指定日期，请输入查询日报的日期（例:{}）：".format(t))
if end_date=="":
    end_date=t
t=datetime.datetime.strptime(end_date, "%Y-%m-%d")
start_date30=t-timedelta(days=30)
start_date30=datetime.datetime.strftime(start_date30, "%Y-%m-%d")
start_date365=t-timedelta(days=365)
start_date365=datetime.datetime.strftime(start_date365, "%Y-%m-%d")



sqlcmd='''CALL pyytest.dataframe("{}")'''.format(end_date)
#df_table=sql.read_sql(sqlcmd,mariadb_conn)
#df_table=df_table.set_index(["车型","零件类型","不良内容","维修方法"])
df1=sql.read_sql(sqlcmd,mariadb_conn)
df2=df1.groupby(["车型"]).aggregate({'NG数量':np.sum})
df2.rename(columns={'NG数量':'合计1'}, inplace = True)

df3=df1.groupby(["车型","零件类型"]).aggregate({'NG数量':np.sum})
df3.rename(columns={'NG数量':'合计2'}, inplace = True)

df4=df1.groupby(["车型","零件类型","不良内容"]).aggregate({'NG数量':np.sum})
df4.rename(columns={'NG数量':'合计3'}, inplace = True)

df1=pd.merge(df1, df2, how='left', on="车型")
df1=pd.merge(df1, df3, how='left', on=["车型","零件类型"])
df1=pd.merge(df1, df4, how='left', on=["车型","零件类型","不良内容"])

df_table=df1.set_index(["车型","合计1","零件类型","合计2","不良内容","合计3","维修方法"])
#df_table=df1.groupby(["车型","合计1","零件类型","合计2","不良内容","合计3","维修方法"]).aggregate({'NG数量':np.sum})


#df_table.to_html('assets/test.html',header=True, index=True, justify='justify-all',bold_rows=True,col_space='280px')
table_html=df_table.to_html(classes='mystyle',header=True, index=True, justify='justify-all',bold_rows=True,col_space='180px')
table_html=table_html.replace("top","middle")
pd.set_option('colheader_justify', 'center')   # FOR TABLE <th>
html_string = '''
<html>
  <head><title>HTML Pandas Dataframe with CSS</title></head>
  <link rel="stylesheet" type="text/css" href="df_style.css"/>
  <body>
    {table}
  </body>
</html>.
'''
# OUTPUT AN HTML FILE
with open('assets/test.html', 'w', encoding="utf-8") as f:
    f.write(html_string.format(table=table_html))


sqlcmd='''CALL pyytest.日内不良("{}")'''.format(end_date)
df=sql.read_sql(sqlcmd,mariadb_conn)
fig_distribution = px.sunburst(df, path=['供应商', '零件类型', '不良内容'], values='不良数',title="{} 所有不良分布情况".format(end_date))
#设置图形边距
fig_distribution.update_layout(margin=dict(l=30, r=30, t=30, b=30))


sqlcmd='''CALL pyytest.按生产线分类("{}")'''.format(end_date)
df=sql.read_sql(sqlcmd,mariadb_conn)
fig_distribution2 = px.sunburst(df, path=['生产线' ,'车型', '不良内容'], values='不良数',title="{} WICO各生产线不良分布".format(end_date))
#设置图形边距
fig_distribution2.update_layout(margin=dict(l=30, r=30, t=30, b=30)) 


sqlcmd='''SELECT * FROM volume WHERE C_M_Date = "{}" ORDER BY CarModel,SeatModel'''.format(end_date)
df=sql.read_sql(sqlcmd,mariadb_conn)
df["SeatModel"]=df["CarModel"]+df["SeatModel"]
df=df.drop(["Sync",'CarModel'],axis=1)
df=pd.melt(df,id_vars=['C_M_Date','SeatModel'],var_name='班次',value_name='产量')
fig_volume = px.bar(df,x="SeatModel",y="产量",color="班次",text="产量",title="{} 客户产量".format(end_date))
fig_volume.update_traces(texttemplate='%{text:.2s}', # 显示的整数位数：示例为2位
                         textfont=dict(family=['Arial Black', 'Arial'],size=[15]),
                         textposition='auto')   # 文本显示位置：['inside', 'outside', 'auto', 'none']
#设置图形边距
fig_volume.update_layout(
    margin=dict(l=0, r=0, t=30, b=30),
    uniformtext_mode='show'
    )



#30日不良趋势
sqlcmd='''CALL pyytest.不良趋势("{}","{}")'''.format(start_date30,end_date)
df=sql.read_sql(sqlcmd,mariadb_conn)
df["nginfo"]=df["supplier"]+"-"+df["parttype"]+"-"+df["nginfo"]
fig_trend_30 = px.line(df,x="ngdate",y="不良率",color="nginfo",title="近30日内不良发展趋势（TOP10）",markers=True)
#设置y轴为百分比
fig_trend_30.update_layout(
    yaxis_tickformat='0%',
    margin=dict(l=0, r=30, t=30, b=0),
    legend=dict(orientation="h",yanchor="bottom",y=1.07,xanchor="right",x=1),
    title=dict(x=0.05, y=0.85)
    )


#365日不良趋势
sqlcmd='''CALL pyytest.不良趋势("{}","{}")'''.format(start_date365,end_date)
df=sql.read_sql(sqlcmd,mariadb_conn)
df["nginfo"]=df["supplier"]+"-"+df["parttype"]+"-"+df["nginfo"]
fig_trend_365 = px.line(df,x="ngdate",y="不良率",color="nginfo",title="年度不良发展趋势（TOP10）",markers=True)
#设置y轴为百分比
fig_trend_365.update_layout(
    yaxis_tickformat='0%',
    margin=dict(l=0, r=30, t=30, b=0),
    legend=dict(orientation="h",yanchor="bottom",y=1.07,xanchor="right",x=1),
    title=dict(x=0.05, y=0.85)
    )


#不良批次分布
sqlcmd='''CALL pyytest.不良批次分布("{}","{}")'''.format("2311-550-120","%焊穿%")
df=sql.read_sql(sqlcmd,mariadb_conn)


sqlcmd='''
SELECT
	ComplainDate
FROM
	complain
WHERE
	ComplainDate <= "{}"
	and ComplainDate >= "{}-01-01"
ORDER BY
	ComplainDate DESC
'''.format(end_date,end_date[:4])
df=sql.read_sql(sqlcmd,mariadb_conn)
if len(df)==0:
    firstday="{}-01-01".format(end_date[:4])
    delta=datetime.datetime.strptime(end_date, "%Y-%m-%d")-datetime.datetime.strptime(firstday, "%Y-%m-%d")
    lastng_date="无"
    
else:
    lastng_date=df.iloc[0][0]
    lastng_date=datetime.datetime.strftime(lastng_date, "%Y-%m-%d")
    delta=datetime.datetime.strptime(end_date, "%Y-%m-%d")-datetime.datetime.strptime(lastng_date, "%Y-%m-%d")

sqlcmd='''
SELECT
	SUBSTRING(COMPLAINDATE, 6, 2) AS 月份
FROM
	complain
WHERE
	COMPLAINDATE <= "{}"
	AND COMPLAINDATE >= "{}-01-01"
GROUP BY 
    SUBSTRING(COMPLAINDATE, 6, 2)
'''.format(end_date,end_date[:4])
df=sql.read_sql(sqlcmd,mariadb_conn)
#月度达成客诉0件的次数
times=datetime.datetime.strptime(end_date, "%Y-%m-%d").month-len(df)


print(type(delta),delta)
complain=dbc.Container([
        html.H2(html.Strong("{}年度客户投诉0件达成情况".format(end_date[:4])),style={'textAlign': 'center'}),
        html.Hr(),
        html.H3('上次客诉发生',style={'textAlign': 'center'}),
        html.H5(html.Strong("{}".format(lastng_date)),style={'textAlign': 'center'}),
        html.Hr(),
        html.H3('客诉0件达成持续天数',style={'textAlign': 'center'}),
        html.H5(html.Strong('第{}天'.format(delta.days)),style={'textAlign': 'center'}),
        html.Hr(),
        html.H3('客诉0件达成持续月数',style={'textAlign': 'center'}),
        html.H5(html.Strong('{}个月'.format(int(delta.days//30))),style={'textAlign': 'center'}),
        html.Hr(),
        html.H4('月度达成客诉0件的次数',style={'textAlign': 'center'}),
        html.H5(html.Strong('{}个月'.format(times)),style={'textAlign': 'center'})
        ])
    


app = Dash(
    __name__,
    # 从国内可顺畅访问的cdn获取所需的原生bootstrap对应css
    #external_stylesheets=['https://cdn.staticfile.org/twitter-bootstrap/4.5.2/css/bootstrap.min.css']
    external_stylesheets=['https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.2.0/css/bootstrap.css']

)


app.layout = html.Div(
    [
        html.H1(end_date,style={'textAlign': 'center'}),
        #html.Hr(), # 水平分割线
        dbc.Row(
            [
                #dbc.Col(dbc.Table.from_dataframe(df_table, striped=True, hover=True,index=True), width=12, style={'margin-top': '30px','overflow': 'auto','font-size':'26px'})
                html.Iframe(src="assets/test.html",style={"height": "{}px".format((df_table.shape[0]+2)*50), "width": "100%"})
                
                
            ]
        ),

        dbc.Row(
            [
                dbc.Col(complain, width=2),
                dbc.Col(dcc.Graph(id = '所有不良分布',figure=fig_distribution,style={"height": "100%", "width": "100%"}), width=3,style={'background-color': 'lightskyblue'}),
                dbc.Col(dcc.Graph(id = 'WICO各生产线不良分布',figure=fig_distribution2,style={"height": "100%", "width": "100%"}), width=3,style={'background-color': 'lightskyblue'}),
                dbc.Col(dcc.Graph(id = '产量',figure=fig_volume,style={"height": "100%", "width": "100%"}), width=4, style={'background-color': 'lightskyblue'})
            ]
        ),
        
        html.Hr(), # 水平分割线
        
        #所谓的网格系统指的是每个Row()部件内部分成宽度相等的12份，传入的Col()部件具有参数width可以传入整数来分配对应数量的宽度
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id = '30day',figure=fig_trend_30), width=6, style={'background-color': 'lightskyblue'}),
                dbc.Col(dcc.Graph(id = '365day',figure=fig_trend_365), width=6, style={'background-color': 'lightskyblue'})
            ]
        )
    ]
)

#pprint.pprint(dir())

if __name__ == "__main__":
    webbrowser.open(r"http://127.0.0.1:8050/")
    app.run_server()


