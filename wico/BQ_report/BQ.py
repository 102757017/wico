# -*- coding: UTF-8 -*-
import mariadb
import numpy as np
import pandas.io.sql as sql
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import datetime
from datetime import timedelta
import webbrowser
from pathlib import Path
import sys
import os

# -----------------------------------------------------------------------------
# 1. 环境与数据库设置
# -----------------------------------------------------------------------------
if getattr(sys, "frozen", False):
    os.environ["WICO_ROOT"] = sys._MEIPASS
else:
    os.environ["WICO_ROOT"] = str(Path(__file__).parent)

KV_DIR = f"{os.environ['WICO_ROOT']}"
sys.path.append(KV_DIR)
os.chdir(KV_DIR)

# 建立数据库连接 (建议: 在实际生产环境中，应在回调函数内连接或使用连接池，防止连接超时)
try:
    mariadb_conn = mariadb.connect(
        user="imasenwh",
        password="596bf648aa7f80d8",
        host="mysql.sqlpub.com",
        port=3306,
        database="custom_feedback"
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# 初始化 Dash 应用
app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB, dbc.icons.BOOTSTRAP])

# -----------------------------------------------------------------------------
# 2. 核心逻辑封装：根据日期生成整个仪表盘内容
# -----------------------------------------------------------------------------
def generate_dashboard_layout(target_date_str):
    """
    输入: '2026-01-23' 格式的日期字符串
    输出: 包含该日数据的所有图表和 KPI 的 dbc.Container 组件
    """
    print(f"正在查询并生成 {target_date_str} 的报表...")
    
    # 日期计算
    try:
        t_obj = datetime.datetime.strptime(target_date_str, "%Y-%m-%d")
    except:
        return html.Div("日期格式错误", className="text-danger")

    start_date30 = datetime.datetime.strftime(t_obj - timedelta(days=30), "%Y-%m-%d")
    start_date7 = datetime.datetime.strftime(t_obj - timedelta(days=7), "%Y-%m-%d")
    start_date365 = datetime.datetime.strftime(t_obj - timedelta(days=365), "%Y-%m-%d")

    # --- 数据查询 1: 表格数据 ---
    try:
        sqlcmd = '''CALL custom_feedback.dataframe3("{}")'''.format(target_date_str)
        # 注意：如果在回调中长时间未操作，连接可能会断开，这里简单处理，实际需重连机制
        mariadb_conn.ping() 
        df1 = sql.read_sql(sqlcmd, mariadb_conn, coerce_float=False)

        if not df1.empty:
            df2 = df1.groupby(["车型"]).aggregate({'NG数量': np.sum}).rename(columns={'NG数量': '合计1'})
            df3 = df1.groupby(["车型", "零件类型"]).aggregate({'NG数量': np.sum}).rename(columns={'NG数量': '合计2'})
            df4 = df1.groupby(["车型", "零件类型", "不良内容"]).aggregate({'NG数量': np.sum}).rename(columns={'NG数量': '合计3'})

            df1 = pd.merge(df1, df2, how='left', on="车型")
            df1 = pd.merge(df1, df3, how='left', on=["车型", "零件类型"])
            df1 = pd.merge(df1, df4, how='left', on=["车型", "零件类型", "不良内容"])
            df_table = df1.set_index(["客户", "车型", "合计1", "零件类型", "合计2", "不良内容", "合计3", "维修方法"])
            table_html = df_table.to_html(
                classes='table table-bordered table-sm table-hover text-center align-middle',
                header=True, index=True, justify='center', border=0
            )
        else:
            table_html = "<h4 class='text-center p-5'>今日无不良记录</h4>"
    except Exception as e:
        print(f"表格查询出错: {e}")
        table_html = f"<div class='alert alert-danger'>数据查询出错: {e}</div>"

    # --- 数据查询 2: 分布图数据 ---
    sqlcmd = '''CALL custom_feedback.日内不良("{}")'''.format(target_date_str)
    df_dist1 = sql.read_sql(sqlcmd, mariadb_conn)

    sqlcmd = '''CALL custom_feedback.按生产线分类("{}")'''.format(target_date_str)
    df_dist2 = sql.read_sql(sqlcmd, mariadb_conn)

    # --- 数据查询 3: 产量数据 ---
    sqlcmd = '''SELECT * FROM volume WHERE C_M_Date = "{}" ORDER BY CarModel,SeatModel'''.format(target_date_str)
    df_volume = sql.read_sql(sqlcmd, mariadb_conn)
    if not df_volume.empty:
        df_volume["SeatModel"] = df_volume["CarModel"] + df_volume["SeatModel"]
        df_volume = df_volume.drop(["Sync", 'CarModel'], axis=1)
        df_volume = pd.melt(df_volume, id_vars=['C_M_Date', 'SeatModel'], var_name='班次', value_name='产量')

    # --- 数据查询 4: 趋势数据 ---
    def get_trend_data(start, end, limit):
        sqlcmd = '''CALL custom_feedback.不良趋势("{}","{}",{})'''.format(start, end, limit)
        df = sql.read_sql(sqlcmd, mariadb_conn)
        if not df.empty:
            df["nginfo"] = df["supplier"] + "-" + df["parttype"] + "-" + df["nginfo"]
        return df

    df_trend_7 = get_trend_data(start_date7, target_date_str, 5)
    df_trend_30 = get_trend_data(start_date30, target_date_str, 5)
    
    # --- 数据查询 5: 年度TOP10 ---
    sqlcmd = '''select * from 年度top10不良'''
    df_top10 = sql.read_sql(sqlcmd, mariadb_conn)
    if not df_top10.empty:
        df_top10["nginfo"] = df_top10["supplier"] + "-" + df_top10["parttype"] + "-" + df_top10["nginfo"]

    # --- 数据查询 6: KPI 数据 ---
    sqlcmd = '''SELECT ComplainDate FROM complain WHERE ComplainDate <= "{}" AND ComplainDate >= "{}-01-01" ORDER BY ComplainDate DESC'''.format(target_date_str, target_date_str[:4])
    df_complain = sql.read_sql(sqlcmd, mariadb_conn)

    sqlcmd_last = '''SELECT ComplainDate FROM complain ORDER BY ComplainDate DESC LIMIT 1'''
    df_last_complain = sql.read_sql(sqlcmd_last, mariadb_conn)

    if df_last_complain.empty:
        lastng_date_str = "无记录"
        delta_days = 0
    else:
        last_date = df_last_complain.iloc[0][0]
        if isinstance(last_date, str):
             last_date = datetime.datetime.strptime(last_date, "%Y-%m-%d").date()
        elif isinstance(last_date, pd.Timestamp):
             last_date = last_date.date()
        elif isinstance(last_date, datetime.datetime):
             last_date = last_date.date()
        query_date = t_obj.date()
        delta_days = (query_date - last_date).days
        lastng_date_str = last_date.strftime("%Y-%m-%d")

    current_month = t_obj.month
    unique_complain_months = df_complain['ComplainDate'].astype(str).str.slice(5, 7).unique()
    times_achieved = current_month - len(unique_complain_months)

    # -----------------------------------------------------------------------------
    # 图表生成逻辑 (包含所有样式优化)
    # -----------------------------------------------------------------------------
    common_layout = dict(
        template='plotly_white',
        margin=dict(l=10, r=10, t=30, b=10),
        font=dict(family="Microsoft YaHei, Arial", size=11),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    
    red_palette = [
        '#2C0000',       # 极暗（起始）
        '#FF6B6B',       # 极亮（最大对比）
        '#8B0000',       # 暗（切换回暗色）
        '#FF4500',       # 亮橙红（再次对比）
        '#4B0082',       # 靛蓝紫（引入冷调）*
        '#FF0000',       # 纯红（回归核心色）
        '#800080'        # 紫色（扩展色域边界）
    ]

    # 1. 供应商分布 (横向条形图)
    if not df_dist1.empty:
        df_dist1['Label'] = df_dist1['供应商'] + " - " + df_dist1['零件类型']
        fig_dist1 = px.bar(
            df_dist1, y="Label", x="不良数", color="不良内容",    
            color_discrete_sequence=red_palette, orientation='h', text="不良数",      
            title=f"{target_date_str} 不良统计（按产品类型汇总）"
        )
        fig_dist1.update_layout(**common_layout)
        fig_dist1.update_layout(
            yaxis={'categoryorder':'total ascending', 'tickfont': dict(size=20, family='Microsoft YaHei')}, 
            xaxis={'title': "", 'tickfont': dict(size=16, family='Arial')},
            legend=dict(orientation="h", y=-0.2, font=dict(size=16))
        )
        fig_dist1.update_traces(textposition='inside', insidetextanchor='middle', textfont=dict(size=28, family='Arial Black', color='white'))
    else:
        fig_dist1 = px.bar(title="今日无供应商不良数据")

    # 2. 产线分布 (横向条形图)
    if not df_dist2.empty:
        df_dist2['Label'] = df_dist2['生产线'] + " " + df_dist2['车型']
        fig_dist2 = px.bar(
            df_dist2, y="Label", x="不良数", color="不良内容",
            color_discrete_sequence=red_palette, orientation='h', text="不良数",
            title=f"{target_date_str} 不良统计（按产线汇总）"
        )
        fig_dist2.update_layout(**common_layout)
        fig_dist2.update_layout(
            yaxis={'categoryorder':'total ascending', 'tickfont': dict(size=20, family='Microsoft YaHei')},
            xaxis={'title': "", 'tickfont': dict(size=16, family='Arial')},
            legend=dict(orientation="h", y=-0.2, font=dict(size=16))
        )
        fig_dist2.update_traces(textposition='inside', insidetextanchor='middle', textfont=dict(size=28, family='Arial Black', color='white'))
    else:
        fig_dist2 = px.bar(title="今日无产线不良数据")

    # 3. 产量图
    if not df_volume.empty:
        fig_vol = px.bar(df_volume, x="SeatModel", y="产量", color="班次", text="产量", title=f"{target_date_str} 客户产量")
        fig_vol.update_traces(textposition='inside',textangle=0, insidetextanchor='middle', textfont=dict(size=28, family='Arial Black', color='white'))
        fig_vol.update_layout(**common_layout)
        fig_vol.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    else:
        fig_vol = px.bar(title="今日无产量数据")

    # 4. 趋势图
    def style_line_chart(fig, title):
        fig.update_layout(**common_layout)
        fig.update_layout(
            title=title, yaxis_tickformat='0%',
            legend=dict(orientation="h", y=-0.2), margin=dict(b=20, l=40)
        )
        fig.update_yaxes(range=[0, 0.05])
        return fig

    fig_tr7 = px.line(df_trend_7, x="ngdate", y="不良率", color="nginfo", markers=True, symbol="nginfo")
    style_line_chart(fig_tr7, "近7日不良趋势 (Top 5)")

    fig_tr30 = px.line(df_trend_30, x="ngdate", y="不良率", color="nginfo", markers=True, symbol="nginfo")
    style_line_chart(fig_tr30, "近30日不良趋势 (Top 5)")

    fig_bar = px.bar(df_top10, x='nginfo', y='不良数量', text='不良数量', labels={'nginfo': '类型'}, title='年度不良 Top 10')
    fig_bar.update_traces(textposition='inside', marker_color='#d9534f')
    fig_bar.update_layout(**common_layout)
    fig_bar.update_xaxes(tickangle=15, tickfont=dict(size=9))

    # -----------------------------------------------------------------------------
    # 布局组件
    # -----------------------------------------------------------------------------
    def create_kpi_card(title, value, color):
        return dbc.Card(
            dbc.CardBody([
                html.H6(title, className="card-subtitle text-muted mb-2", style={'fontSize': '0.9rem'}),
                html.H2(value, className=f"text-{color} fw-bold mb-0"),
            ]),
            className="h-100 shadow-sm border-0 d-flex flex-column justify-content-center"
        )

    def create_graph_card(fig):
        return dbc.Card(
            dcc.Graph(figure=fig, config={'displayModeBar': False}, style={'height': '100%'}),
            className="h-100 shadow-sm border-0",
            style={'overflow': 'hidden'}
        )

    # 返回整个 Container 内容
    return dbc.Container([
        # --- 标题栏 (现在由外部 DatePicker 控制，这里只显示辅助信息) ---
        # 实际的标题栏放在了外部布局

        # --- 第一行：KPI ---
        dbc.Row([
            dbc.Col(create_kpi_card("上次客诉发生日", lastng_date_str, "danger"), width=3),
            dbc.Col(create_kpi_card("客诉0件持续天数", f"{delta_days} 天", "success"), width=3),
            dbc.Col(create_kpi_card("客诉0件持续月数", f"{int(delta_days // 30)} 个月", "primary"), width=3),
            dbc.Col(create_kpi_card(f"{target_date_str[:4]}年月度达成次数", f"{times_achieved} 次", "warning"), width=3),
        ], className="mb-3 g-3"),

        # --- 第二行：趋势 ---
        dbc.Row([
            dbc.Col(create_graph_card(fig_tr7), width=4, style={'height': '280px'}),
            dbc.Col(create_graph_card(fig_tr30), width=4, style={'height': '280px'}),
            dbc.Col(create_graph_card(fig_bar), width=4, style={'height': '280px'}),
        ], className="mb-3 g-3"),

        # --- 第三行：分布 ---
        dbc.Row([
            dbc.Col(create_graph_card(fig_dist2), width=6, style={'height': '350px'}),
            dbc.Col(create_graph_card(fig_dist1), width=6, style={'height': '350px'}),
        ], className="mb-3 g-3"),

        # --- 第四行：表格 & 产量 ---
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("今日不良明细", className="fw-bold bg-light py-2"),
                    html.Div(
                        dcc.Markdown(table_html, dangerously_allow_html=True), 
                        className="table-container p-2"
                    )
                ], className="h-100 shadow-sm border-0"),
                width=6, style={'height': '400px'}
            ),
            dbc.Col(create_graph_card(fig_vol), width=6, style={'height': '400px'})
        ], className="mb-4 g-3")
    ], fluid=True, style={'maxWidth': '1800px'})


# -----------------------------------------------------------------------------
# 3. 页面主布局与回调
# -----------------------------------------------------------------------------
custom_css = '''
<style>
    body { background-color: #f0f2f5; font-family: 'Microsoft YaHei', sans-serif; }
    .table-container { font-size: 0.75rem; overflow-y: auto; height: 100%; }
    .table thead th { position: sticky; top: 0; background-color: #e9ecef; z-index: 1; vertical-align: middle;}
    .table td { vertical-align: middle; padding: 0.25rem !important; }
    
    @media print {
        @page { size: A3 landscape; margin: 5mm; }
        body { background-color: white; -webkit-print-color-adjust: exact; }
        .card { box-shadow: none !important; border: 1px solid #ddd !important; break-inside: avoid; }
        .no-print { display: none; }
        .js-plotly-plot .plotly .bg { fill-opacity: 0 !important; }
        /* 打印时隐藏日期选择器，只保留文字 */
        .date-picker-container { display: none; }
    }
</style>
'''

# 默认日期为昨天
default_date = datetime.datetime.now() - timedelta(days=1)

app.layout = html.Div([
    dcc.Markdown(custom_css, dangerously_allow_html=True),
    
    # --- 1. 顶部导航栏 (修改点：添加 d-print-none) ---
    dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H3("WICO 质量日报监控看板", className="text-white fw-bold mb-0"),
                ], width="auto", className="d-flex align-items-center"),
                
                dbc.Col([
                    dcc.DatePickerSingle(
                        id='date-picker',
                        min_date_allowed=datetime.date(2023, 1, 1),
                        max_date_allowed=datetime.date(2030, 12, 31),
                        initial_visible_month=default_date,
                        date=default_date.date(),
                        display_format='YYYY-MM-DD',
                        style={'border': 'none', 'borderRadius': '5px'}
                    )
                ], width="auto", className="d-flex align-items-center ms-3")
            ], 
            align="center",
            justify="center",
            className="w-100"
            ),
        ], fluid=True),
        color="dark",
        dark=True,
        # 【关键修改】这里添加了 "d-print-none"，打印时整个黑条和日期选择器都会消失
        className="mb-3 py-2 d-print-none" 
    ),

    # --- 2. 打印专用标题 (保持不变：d-none d-print-block) ---
    # d-none: 屏幕上不显示
    # d-print-block: 打印时显示
    html.H2(id='print-title', className="text-center d-none d-print-block fw-bold mb-3"),

    # 内容区域
    dcc.Loading(
        id="loading-spinner",
        type="circle",
        children=html.Div(id='page-content')
    )
])

# 回调函数：当日期改变时，更新内容
@app.callback(
    [Output('page-content', 'children'),
     Output('print-title', 'children')],
    [Input('date-picker', 'date')]
)
def update_output(date_value):
    if date_value is not None:
        # date_value 可能是字符串，确保格式
        if isinstance(date_value, str) and 'T' in date_value:
            date_str = date_value.split('T')[0]
        else:
            date_str = str(date_value)
            
        layout = generate_dashboard_layout(date_str)
        # 打印时的标题
        title_text = f"WICO 质量日报监控看板 - {date_str}"
        return layout, title_text
    return html.Div(), ""

if __name__ == "__main__":
    webbrowser.open(r"http://127.0.0.1:8050/")
    app.run_server(debug=False, port=8050)
