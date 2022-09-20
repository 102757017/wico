from kivy.metrics import dp,sp
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from search import *
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.pickers import MDDatePicker
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.clock import Clock
import pprint
import datetime
from kivy.logger import Logger
from font import font_definitions
import kivy
print(kivy.core.window.Window.size)

class Nginfo_tables(MDFloatLayout, MDTabsBase):
    def __init__(self, **kwargs):
        #一定要注意这里要加super，才能把现有的新初始化方法覆盖掉继承来的旧初始化方法
        super().__init__(**kwargs)
        self.title="已录入NG信息"
        self.name="inputed_ng_info"
        self.clock_variable=Clock.schedule_interval(self.update_clock, 60)

        info=query_nginfo(self.ids.date.text)
        k=1
        fontsize="[size={}]".format(int(25/k))
        for i,j in enumerate(info):
            info[i]=list(j)
            #调整字体大小
            for x,y in enumerate(j):
                y=fontsize+str(y)
                info[i][x]=y
        print("{}车型".format(fontsize))
        self.data_tables = MDDataTable(
            use_pagination=False,
            check=True,
            column_data=[
                ("{}车型".format(fontsize), dp(18*k)),
                ("{}座椅型号".format(fontsize), dp(20*k)),
                ("{}不良信息".format(fontsize), dp(25*k)),
                ("{}维修方法".format(fontsize), dp(25*k)),
                ("{}WICO番号".format(fontsize), dp(21*k)),
                ("{}TS番号".format(fontsize), dp(27*k)),
                ("{}零件名称".format(fontsize), dp(30*k)),
                ("{}批次号".format(fontsize), dp(18*k)),
                ("{}生产日期".format(fontsize), dp(18*k)),
            ],
            row_data=info,
            rows_num=20
            )
        self.data_tables.bind(on_row_press=self.on_row_press)
        self.data_tables.bind(on_check_press=self.on_check_press)
        self.ids.lay_table.add_widget(self.data_tables)
        


    def show_date_picker(self):
        t=datetime.datetime.now()-datetime.timedelta(hours=8)
        dialog = MDDatePicker(year=t.year, month=t.month, day=t.day)
        dialog.bind(on_save=self.set_previous_date)
        dialog.open()

    def set_previous_date(self, instance, value, date_rang):
        self.ids.date.text = (f"{value.year}-{value.month}-{value.day}")
        t=datetime.datetime.strftime(datetime.datetime.now()-datetime.timedelta(hours=8), "%Y-%m-%d")
        if self.ids.date.text==t:
            if self.clock_variable==None:
                self.clock_variable=Clock.schedule_interval(self.update_clock, 60)
        else:
            self.clock_variable.cancel()
        self.update()

    def update_clock(self, *args):
        self.ids.date.text = datetime.datetime.strftime(datetime.datetime.now()-datetime.timedelta(hours=8), "%Y-%m-%d")
        
    #更新表格中的数据
    def update(self):
        info=query_nginfo(self.ids.date.text)
        k=1
        fontsize="[size={}]".format(int(25/k))
        for i,j in enumerate(info):
            info[i]=list(j)
            for x,y in enumerate(j):
                y=fontsize+str(y)
                info[i][x]=y
        self.data_tables.update_row_data(instance_data_table=self.data_tables,data=info)
 
    def on_row_press(self, instance_table, instance_row):
        '''Called when a table row is clicked.'''
        print(instance_table, instance_row)

    def on_check_press(self, instance_table, current_row):
        '''Called when the check box in the table row is checked.'''

class DemoApp(MDApp):

    def build(self):
        scn=Screen()
        scn.add_widget(Nginfo_tables())
        return scn



if __name__=="__main__":
    Builder.load_file( f"{os.environ['WICO_ROOT']}/mddatatable.kv" )
    DemoApp().run()
