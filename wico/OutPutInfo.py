from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.bottomsheet import MDListBottomSheet
from kivymd.app import MDApp
from kivymd.uix.screen import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from pprint import pprint
import time
from search import *
import os
import sys
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.uix.textinput import TextInput
import datetime
from kivy.clock import Clock
from functools import partial
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.tab import MDTabsBase
from synch import sync_ngrecord_volume
from pathlib import Path
from kivy.logger import Logger
import threading
from kivy.clock import Clock
from kivymd.uix.pickers import MDDatePicker
from font import font_definitions


#  所有基于模块的使用到__file__属性的代码，在源码运行时表示的是当前脚本的绝对路径，但是用pyinstaller打包后就是当前模块的模块名（即文件名xxx.py）
#  因此需要用以下代码来获取exe的绝对路径
if getattr(sys, "frozen", False):  # bundle mode with PyInstaller
    os.environ["WICO_ROOT"] = sys._MEIPASS
else:
    os.environ["WICO_ROOT"] = str(Path(__file__).parent)

KV_DIR = f"{os.environ['WICO_ROOT']}"
sys.path.append(KV_DIR)
Logger.info("OutPut_KV_DIR:"+KV_DIR)

font_path=Path(os.environ['WICO_ROOT'])/"font"/"DroidSansFallback.ttf"
font_path=str(font_path)


'''
Kv 语言特有的三个关键字：
app：总是指您的应用程序的实例。
root：指当前规则中的基本小部件/模板,root只代表其上层被<>包裹住的类
self：始终引用当前小部件
'''

#button内的文本自动换行
class WrappedButton(Button):
    # Based on Tshirtman's answer
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        #按钮内的文本自动换行
        self.bind(
            width=lambda *x:
            self.setter('text_size')(self, (self.width, None)),
            texture_size=lambda *x: self.setter('height')(self, self.texture_size[1]))


class OutPutInfo(MDFloatLayout, MDTabsBase):

    def __init__(self, **kwargs):
        #一定要注意这里要加super，才能把现有的新初始化方法覆盖掉继承来的旧初始化方法
        super().__init__(**kwargs)
        self.name="outputinfo"
        print(self)
        self.clock_variable=Clock.schedule_interval(self.update_clock, 60)
        self.load_volume()

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
        self.ids.quantity.clear_widgets()
        self.load_volume()

    def load_volume(self):
        #根据日期在数据库中查询当天的产量,优先显示服务器数据
        values=query_volume_server(self.ids.date.text)
        if values==None:
            values=query_volume_local(self.ids.date.text)
        #values=query_volume_local("2022-04-01")
        self.CarModel_rows=[]
        self.SeatModel_rows=[]
        self.Day_rows=[]
        self.Night_rows=[]
        for x in values:
            HB = BoxLayout(orientation='horizontal')
            t1 = WrappedButton(text=x[1],font_name=font_path,size_hint_x=0.1)
            t2 = WrappedButton(text=x[2],font_name=font_path,size_hint_x=0.5)
            t3 = TextInput(text=str(x[3]),size_hint_x=0.2,halign="center",multiline=False,input_filter="int",input_type="number")
            t4 = TextInput(text=str(x[4]),size_hint_x=0.2,halign="center",multiline=False,input_filter="int",input_type="number")

            t1.bind(on_press=partial(self.all_model2, t1))
            t2.bind(on_press=partial(self.show_SeatModel2, t2))

            HB.add_widget(t1)
            HB.add_widget(t2)
            HB.add_widget(t3)
            HB.add_widget(t4)
            
            self.CarModel_rows.append(t1)
            self.SeatModel_rows.append(t2)
            self.Day_rows.append(t3)
            self.Night_rows.append(t4)
            
            self.ids.quantity.add_widget(HB)
        
    def all_model2(self,*args):
        bs_menu_1 = MDListBottomSheet()
        scroll = ScrollView()
        CarModel=get_CarModel()
        button=args[0]
        for item in CarModel:
            bs_menu_1.add_item(item,callback=lambda x, y=item: self.select_model2(y,button)) 
        bs_menu_1.open()
    def select_model2(self, *args):
        args[1].text=args[0]
                    
    def show_SeatModel2(self,*args):
        bs_menu_1 = MDListBottomSheet()
        scroll = ScrollView()
        button=args[0]
        #获取这个按钮的索引号
        Index=self.SeatModel_rows.index(button)
        #前一个按钮的车型
        CarModel=self.CarModel_rows[Index].text
        SeatModel=get_SeatModel(CarModel)
        for item in SeatModel:
            bs_menu_1.add_item(item,callback=lambda x, y=item: self.select_SeatModel2(y,button)) 
        bs_menu_1.open()
    def select_SeatModel2(self, *args):
        args[1].text=args[0]

    def update_clock(self, *args):
        self.ids.date.text = datetime.datetime.strftime(datetime.datetime.now()-datetime.timedelta(hours=8), "%Y-%m-%d")


    def add_quantity(self):
        HB = BoxLayout(orientation='horizontal')
        t1 = WrappedButton(text='',font_name=font_path,size_hint_x=0.1)
        t2 = WrappedButton(text='',font_name=font_path,size_hint_x=0.5)
        t3 = TextInput(text="",size_hint_x=0.2,halign="center",multiline=False,input_filter="int",input_type="number")
        t4 = TextInput(text="",size_hint_x=0.2,halign="center",multiline=False,input_filter="int",input_type="number")

        
        t1.bind(on_press=partial(self.all_model2, t1))
        t2.bind(on_press=partial(self.show_SeatModel2, t2))
        
        HB.add_widget(t1)
        HB.add_widget(t2)
        HB.add_widget(t3)
        HB.add_widget(t4)

        self.CarModel_rows.append(t1)
        self.SeatModel_rows.append(t2)
        self.Day_rows.append(t3)
        self.Night_rows.append(t4)
        
        self.ids.quantity.add_widget(HB)



    def upload_volume(self):
        Date=self.ids.date.text
        data=[]
        for i in range(len(self.CarModel_rows)):
            if self.SeatModel_rows[i].text !="" and (self.Day_rows[i].text !="" or self.Night_rows[i].text !=""):
                if self.Day_rows[i].text =="":
                    self.Day_rows[i].text ="0"
                if self.Night_rows[i].text =="":
                    self.Night_rows[i].text ="0"
                d=(
                    Date,
                    self.CarModel_rows[i].text,
                    self.SeatModel_rows[i].text,
                    self.Day_rows[i].text,
                    self.Night_rows[i].text,
                    0
                   )
                #print(d)
                data.append(d)
            else:
                toast("{} {}座椅数据未填写完整".format(self.CarModel_rows[i].text,self.SeatModel_rows[i].text))

        data=str(data)[1:-1]
        if data !="":
            #t1 = threading.Thread(target=self.child_Thread,args=(data,))
            #t1.start()
            self.ids.submit.disabled=True
            try:
                submit_volume(data)
                f=sync_ngrecord_volume()
                if f==False:
                    toast("网络不好,稍后再试")
                else:
                    toast("数据已提交")
            except:
                toast("数据提交出错")
            self.ids.submit.disabled=False


    def child_Thread(self,data):
        self.ids.submit.disabled=True
        try:
            submit_volume(data)
            f=sync_ngrecord_volume()
            if f==False:
                Clock.schedule_once(lambda a: toast("网络不好,稍后再试"))
            else:
                Clock.schedule_once(lambda a: toast("数据已提交"))
        except:
            Clock.schedule_once(lambda a: toast("数据提交出错"))
        self.ids.submit.disabled=False


class DemoApp(MDApp):

    def build(self):
        scn=Screen()
        scn.add_widget(OutPutInfo())
        return scn


        
        
           
    
if __name__ == '__main__':
    #如果KV定义了一个Root Widget，它将附加到 App 的root 属性并用作应用程序的根部件，这个根部件附加完成后，再执行__init__中的代码。
    Builder.load_file( f"{os.environ['WICO_ROOT']}/outputinfo.kv" )
    DemoApp().run()
