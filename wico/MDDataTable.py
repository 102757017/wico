from kivy.metrics import dp,sp
from kivymd.app import MDApp
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
from kivy.properties import ListProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recyclegridlayout import RecycleGridLayout

class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior,
                                  RecycleGridLayout):
    ''' Adds selection and focus behaviour to the view. '''

class Nginfo_tables(MDFloatLayout, MDTabsBase):
    data_items = ListProperty([])


    def __init__(self, **kwargs):
        #一定要注意这里要加super，才能把现有的新初始化方法覆盖掉继承来的旧初始化方法
        super().__init__(**kwargs)
        self.title="已录入NG信息"
        self.name="inputed_ng_info"
        self.clock_variable=Clock.schedule_interval(self.update_clock, 60)

        self.Column_names=["录入时间","车型","座椅型号","不良信息","维修方法","WICO番号","TS番号","零件名称","批次号","生产日期"]
        for name in self.Column_names:
            self.data_items.append(name)
            
        info=query_nginfo(self.ids.date.text)
        # create data_items
        for row in info:
            for col in row:
                self.data_items.append(col)
        


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
        self.data_items.clear()
        
        for name in self.Column_names:
            self.data_items.append(name)
            
        for row in info:
            for col in row:
                self.data_items.append(col)

        
 

class DemoApp(MDApp):

    def build(self):
        scn=Screen()
        scn.add_widget(Nginfo_tables())
        return scn



if __name__=="__main__":
    Builder.load_file( f"{os.environ['WICO_ROOT']}/mddatatable.kv" )
    DemoApp().run()
