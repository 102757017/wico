import mariadb
import pandas.io.sql as sql
import webbrowser
import pandas as pd
import numpy as np
import datetime
from pathlib import Path
import os

os.chdir(Path(__file__).parent)

mariadb_conn = mariadb.connect( 
user="imasenwh", 
password="596bf648aa7f80d8", 
host="mysql.sqlpub.com", 
port=3306, 
database="custom_feedback" )


sqlcmd='''
select
	`ngrecord`.`PartType` AS `零件类型`,
	cast(`ngrecord`.`NgTime` as date) AS `日期`,
	`ngrecord`.`NgInfo` AS `不良内容`,
	`ngrecord`.`RepairMethod` AS `维修方法`,
	count(`ngrecord`.`NgInfo`) AS `NG数量`,
	#concat(left(count(`ngrecord`.`NgInfo`) / (any_value(`volume`.`Day`) + any_value(`volume`.`Night`)) * 100, 4), '%') AS `不良率`,
	(any_value(`volume`.`Day`) + any_value(`volume`.`Night`)) AS `产量`
from
	(`ngrecord`
left join `volume` on
	(cast(`ngrecord`.`NgTime` as date) = `volume`.`C_M_Date`
		and `ngrecord`.`CarModel` = `volume`.`CarModel`
		and `ngrecord`.`SeatModel` = `volume`.`SeatModel`))
WHERE
	cast(`ngrecord`.`NgTime` as date)>"2022-08-24" AND 
	`ngrecord`.`CarModel`="2YC" AND
	`ngrecord`.`PartType`="电动滑轨" AND
	`ngrecord`.`Supplier`="WICO"
	
group by
	cast(`ngrecord`.`NgTime` as date),
	`ngrecord`.`CarModel`,
	`ngrecord`.`PartType`,
	`ngrecord`.`NgInfo`,
	`ngrecord`.`RepairMethod`
ORDER BY 
	`ngrecord`.`PartType`,
	cast(`ngrecord`.`NgTime` as date),
	`ngrecord`.`NgInfo`
'''

df1=sql.read_sql(sqlcmd,mariadb_conn)

df2=df1.groupby(["零件类型","日期"]).aggregate({'NG数量':np.sum})
df2.rename(columns={'NG数量':'按日期合计'}, inplace = True)

df3=df1.groupby(["零件类型","日期","不良内容"]).aggregate({'NG数量':np.sum})
df3.rename(columns={'NG数量':'按不良内容合计'}, inplace = True)

#df1=pd.merge(df1, df2, how='left', on=["零件类型","日期"])
#df1=pd.merge(df1, df3, how='left', on=["零件类型","日期","不良内容"])

df_table=df1.set_index(["零件类型","日期","不良内容","维修方法"])
#df_table=df1.set_index(["零件类型","日期","按日期合计","不良内容","按不良内容合计","维修方法"])



table_html=df_table.to_html(classes='mystyle',header=True, index=True, justify='justify-all',bold_rows=True,col_space='280px')
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
with open('assets/2YC电动滑轨.html', 'w', encoding="utf-8") as f:
    f.write(html_string.format(table=table_html))



sqlcmd='''
select
	`ngrecord`.`PartType` AS `零件类型`,
	cast(`ngrecord`.`NgTime` as date) AS `日期`,
	`ngrecord`.`NgInfo` AS `不良内容`,
	`ngrecord`.`RepairMethod` AS `维修方法`,
	count(`ngrecord`.`NgInfo`) AS `NG数量`,
	#concat(left(count(`ngrecord`.`NgInfo`) / (any_value(`volume`.`Day`) + any_value(`volume`.`Night`)) * 100, 4), '%') AS `不良率`,
	(any_value(`volume`.`Day`) + any_value(`volume`.`Night`)) AS `产量`
from
	(`ngrecord`
left join `volume` on
	(cast(`ngrecord`.`NgTime` as date) = `volume`.`C_M_Date`
		and `ngrecord`.`CarModel` = `volume`.`CarModel`
		and `ngrecord`.`SeatModel` = `volume`.`SeatModel`))
WHERE
	cast(`ngrecord`.`NgTime` as date)>"2022-08-24" AND 
	`ngrecord`.`CarModel`="2YC" AND
	`ngrecord`.`PartType`="前升降电动支架" AND
	`ngrecord`.`Supplier`="WICO"
group by
	cast(`ngrecord`.`NgTime` as date),
	`ngrecord`.`CarModel`,
	`ngrecord`.`PartType`,
	`ngrecord`.`NgInfo`,
	`ngrecord`.`RepairMethod`
ORDER BY 
	`ngrecord`.`PartType`,
	cast(`ngrecord`.`NgTime` as date),
	`ngrecord`.`NgInfo`
'''
df1=sql.read_sql(sqlcmd,mariadb_conn)

df2=df1.groupby(["零件类型","日期"]).aggregate({'NG数量':np.sum})
df2.rename(columns={'NG数量':'按日期合计'}, inplace = True)

df3=df1.groupby(["零件类型","日期","不良内容"]).aggregate({'NG数量':np.sum})
df3.rename(columns={'NG数量':'按不良内容合计'}, inplace = True)

#df1=pd.merge(df1, df2, how='left', on=["零件类型","日期"])
#df1=pd.merge(df1, df3, how='left', on=["零件类型","日期","不良内容"])

df_table=df1.set_index(["零件类型","日期","不良内容","维修方法"])
#df_table=df1.set_index(["零件类型","日期","按日期合计","不良内容","按不良内容合计","维修方法"])

table_html=df_table.to_html(classes='mystyle',header=True, index=True, justify='justify-all',bold_rows=True,col_space='280px')
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
with open('assets/2YC电动支架INN.html', 'w', encoding="utf-8") as f:
    f.write(html_string.format(table=table_html))


sqlcmd='''
select
	`ngrecord`.`PartType` AS `零件类型`,
	cast(`ngrecord`.`NgTime` as date) AS `日期`,
	`ngrecord`.`NgInfo` AS `不良内容`,
	`ngrecord`.`RepairMethod` AS `维修方法`,
	count(`ngrecord`.`NgInfo`) AS `NG数量`,
	#concat(left(count(`ngrecord`.`NgInfo`) / (any_value(`volume`.`Day`) + any_value(`volume`.`Night`)) * 100, 4), '%') AS `不良率`,
	(any_value(`volume`.`Day`) + any_value(`volume`.`Night`)) AS `产量`
from
	(`ngrecord`
left join `volume` on
	(cast(`ngrecord`.`NgTime` as date) = `volume`.`C_M_Date`
		and `ngrecord`.`CarModel` = `volume`.`CarModel`
		and `ngrecord`.`SeatModel` = `volume`.`SeatModel`))
WHERE
	cast(`ngrecord`.`NgTime` as date)>"2022-08-24" AND 
	`ngrecord`.`CarModel`="2YC" AND
	`ngrecord`.`PartType`="后升降电动支架" AND
	`ngrecord`.`Supplier`="WICO"
group by
	cast(`ngrecord`.`NgTime` as date),
	`ngrecord`.`CarModel`,
	`ngrecord`.`PartType`,
	`ngrecord`.`NgInfo`,
	`ngrecord`.`RepairMethod`
ORDER BY 
	`ngrecord`.`PartType`,
	cast(`ngrecord`.`NgTime` as date),
	`ngrecord`.`NgInfo`
'''
df1=sql.read_sql(sqlcmd,mariadb_conn)

df2=df1.groupby(["零件类型","日期"]).aggregate({'NG数量':np.sum})
df2.rename(columns={'NG数量':'按日期合计'}, inplace = True)

df3=df1.groupby(["零件类型","日期","不良内容"]).aggregate({'NG数量':np.sum})
df3.rename(columns={'NG数量':'按不良内容合计'}, inplace = True)

#df1=pd.merge(df1, df2, how='left', on=["零件类型","日期"])
#df1=pd.merge(df1, df3, how='left', on=["零件类型","日期","不良内容"])

df_table=df1.set_index(["零件类型","日期","不良内容","维修方法"])
#df_table=df1.set_index(["零件类型","日期","按日期合计","不良内容","按不良内容合计","维修方法"])

table_html=df_table.to_html(classes='mystyle',header=True, index=True, justify='justify-all',bold_rows=True,col_space='280px')
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
with open('assets/2YC电动支架OUT.html', 'w', encoding="utf-8") as f:
    f.write(html_string.format(table=table_html))




sqlcmd='''
select
	`ngrecord`.`PartType` as `零件类型`,
	`ngrecord`.`NgInfo` as `不良内容`,
	`ngrecord`.`RepairMethod` as `维修方法`,
	count(`ngrecord`.`NgInfo`) as `NG数量`
	#concat(left(count(`ngrecord`.`NgInfo`) / (any_value(`volume`.`Day`) + any_value(`volume`.`Night`)) * 100, 4), '%') AS `不良率`,
from
	`ngrecord`
WHERE
	`ngrecord`.`CarModel`="2YC" AND
	`ngrecord`.`Supplier`="WICO"
group by
	`ngrecord`.`CarModel`,
	`ngrecord`.`PartType`,
	`ngrecord`.`NgInfo`,
	`ngrecord`.`RepairMethod`
ORDER BY 
	`ngrecord`.`PartType`,
	`ngrecord`.`NgInfo`
'''
df1=sql.read_sql(sqlcmd,mariadb_conn)

df2=df1.groupby(["零件类型"]).aggregate({'NG数量':np.sum})
df2.rename(columns={'NG数量':'按零件合计'}, inplace = True)

df3=df1.groupby(["零件类型","不良内容"]).aggregate({'NG数量':np.sum})
df3.rename(columns={'NG数量':'按不良内容合计'}, inplace = True)

#df1=pd.merge(df1, df2, how='left', on=["零件类型"])
#df1=pd.merge(df1, df3, how='left', on=["零件类型","不良内容"])

df_table=df1.set_index(["零件类型","不良内容","维修方法"])
#df_table=df1.set_index(["零件类型","按零件合计","不良内容","按不良内容合计","维修方法"])
df_table = df_table.sort_index(ascending=False)



table_html=df_table.to_html(classes='mystyle',header=True, index=True, justify='justify-all',bold_rows=True,col_space='280px')
table_html=table_html.replace("top","middle")
pd.set_option('colheader_justify', 'center')   # FOR TABLE <th>
html_string = '''
<html>
  <head><title>HTML Pandas Dataframe with CSS</title></head>
  <link rel="stylesheet" type="text/css" href="df_style.css"/>
  <body>
    <h1>2022/8/28~{}</h1>
    {table}
  </body>
</html>.
'''.format(datetime.datetime.now(),table=table_html)
# OUTPUT AN HTML FILE
with open('assets/合计.html', 'w', encoding="utf-8") as f:
    f.write(html_string)




#webbrowser.open(r"assets/2YC.html")
