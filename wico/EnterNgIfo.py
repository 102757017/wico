from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.bottomsheet import MDListBottomSheet
from kivymd.app import MDApp
from kivymd.uix.screen import Screen
from kivymd.uix.list import IRightBodyTouch, ILeftBody,OneLineAvatarIconListItem
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.label import MDIcon
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from pprint import pprint
import time
from search import *
from barcode_analysis import analysis_code
import os
import sys
from functools import partial
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.tab import MDTabsBase
from synch import sync_ngrecord_volume
from kivy.logger import Logger
from pathlib import Path
from font import font_definitions

#  所有基于模块的使用到__file__属性的代码，在源码运行时表示的是当前脚本的绝对路径，但是用pyinstaller打包后就是当前模块的模块名（即文件名xxx.py）
#  因此需要用以下代码来获取exe的绝对路径
if getattr(sys, "frozen", False):  # bundle mode with PyInstaller
    os.environ["WICO_ROOT"] = sys._MEIPASS
else:
    os.environ["WICO_ROOT"] = str(Path(__file__).parent)

KV_DIR = f"{os.environ['WICO_ROOT']}"
sys.path.append(KV_DIR)
Logger.info("EnterNginfo_KV_DIR:"+KV_DIR)


'''
Kv 语言特有的三个关键字：
app：总是指您的应用程序的实例。
root：指当前规则中的基本小部件/模板,root只代表其上层被<>包裹住的类
self：始终引用当前小部件
'''

class RightCheckbox(IRightBodyTouch, MDCheckbox):
    '''Custom right container.'''
    
class ListBottomSheetIconLeft(ILeftBody, MDIcon):
    pass

class OneLineAvatarIconListItem_CK(OneLineAvatarIconListItem):
    def __init__(self, **kwargs):
        #一定要注意这里要加super，才能把现有的新初始化方法覆盖掉继承来的旧初始化方法
        super().__init__(**kwargs)
        self.add_widget(ListBottomSheetIconLeft(icon="tools"))
        self.ck=RightCheckbox()
        self.add_widget(self.ck)
        
class MDListBottomSheet(MDListBottomSheet):

    def add_item_checkbox(self, text, callback):
        item = OneLineAvatarIconListItem_CK(text=text, on_release=callback)
        item.bind(on_release=lambda x: self.dismiss())
        self.sheet_list.ids.box_sheet_list.add_widget(item)



class EnterNgIfo(MDFloatLayout, MDTabsBase):
    
    def show_model1(self):
        bs_menu_1 = MDListBottomSheet()
        scroll = ScrollView()
        #CarModel=["2FW","2HY","2VH","2VP","2WB","2YC","2YN","2YS","2YT","3BS"]
        WicoPartNumber=self.ids.WicoPartNumber1.text
        print(WicoPartNumber)
        Supplier,PartType,WicoPartNumber,TsPartNumber,PartName,PartPicUrl,CarModel=get_CarModelBybar(WicoPartNumber)
        print(PartType)
        for item in CarModel:
            bs_menu_1.add_item(item,callback=lambda x, y=item: self.select_model1(y))                
        bs_menu_1.open()
    def select_model1(self, *args):
        self.ids.CarModel1.text=args[0]
        self.ids.NgInfo1.text=""
        self.ids.RepairMethod1.text=""

        SeatModel=get_SeatModelBybar(self.ids.WicoPartNumber1.text,args[0])
        if len(SeatModel)==1:
            self.ids.SeatModel1.text=SeatModel[0]
        else:
            self.ids.SeatModel1.text=""

    def show_SeatModel1(self):
        bs_menu_1 = MDListBottomSheet()
        scroll = ScrollView()
        WicoPartNumber=self.ids.WicoPartNumber1.text
        CarModel=self.ids.CarModel1.text
        SeatModel=get_SeatModelBybar(WicoPartNumber,CarModel)
        #SeatModel=["手动-前排-左席座椅","手动-前排-右席座椅"]
        for item in SeatModel:
            bs_menu_1.add_item(item,callback=lambda x, y=item: self.select_SeatModel1(y))                
        bs_menu_1.open()
    def select_SeatModel1(self, *args):
        self.ids.SeatModel1.text=args[0]
        self.ids.NgInfo1.text=""
        self.ids.RepairMethod1.text=""

    def show_ng_information1(self):
        bs_menu_1 = MDListBottomSheet()
        PartType=self.ids.PartType1.text
        NgInfo=get_NgInfo(PartType)
        #NgInfo=["异音","震动"]
        for item in NgInfo:
            bs_menu_1.add_item(item,callback=lambda x, y=item: self.select_ng_information1(y))
        bs_menu_1.open()
    def select_ng_information1(self, *args):
        self.ids.NgInfo1.text=args[0]
        self.ids.RepairMethod1.text=""
        
    def show_repair_method1(self):
        bs_menu_1 = MDListBottomSheet()
        PartType=self.ids.PartType1.text
        NgInfo=self.ids.NgInfo1.text
        RepairMethod=get_RepairMethod(PartType,NgInfo)
        bs_menu_1.add_item("确认",callback=partial(self.get_active_check))
        #RepairMethod=["涂油","换电机"]
        for item in RepairMethod:
            bs_menu_1.add_item_checkbox(item,callback=lambda x, y=item: self.select_repair_method1(y))
        self.bs_menu=bs_menu_1
        bs_menu_1.open()
    def select_repair_method1(self, *args):
        self.ids.RepairMethod1.text=args[0]

    def get_active_check(self, *args):
        nginfo=[]
        for ListItemWithCheckbox in self.bs_menu.sheet_list.ids.box_sheet_list.children:
            if isinstance(ListItemWithCheckbox, OneLineAvatarIconListItem_CK) and ListItemWithCheckbox.ck.active==True:
                nginfo.append(ListItemWithCheckbox.text)
        nginfo.sort()
        self.ids.RepairMethod1.text=','.join(nginfo)
        
    
    def upload(self):
        if self.ids.NgInfo1.text !="" and self.ids.RepairMethod1.text !="" and self.ids.SeatModel1.text!="":
            # 格式化成2016-03-20 11:45:39形式
            NgTime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            CarModel=self.ids.CarModel1.text
            SeatModel=self.ids.SeatModel1.text
            WicoPartNumber=self.ids.WicoPartNumber1.text
            TsPartNumber=self.ids.TsPartNumber1.text
            PartName=self.ids.PartName1.text
            PartType=self.ids.PartType1.text
            Supplier=self.Supplier1
            NgInfo=self.ids.NgInfo1.text
            RepairMethod=self.ids.RepairMethod1.text
            Lot=self.ids.Lot1.text
            ManufactureDate=self.ManufactureDate1
            Production_Line=self.Production_Line1
            if search_barcode(WicoPartNumber,Lot)==False:
                conn=uploade_ngrecord(NgTime,
                                 CarModel,
                                 SeatModel,
                                 WicoPartNumber,
                                 TsPartNumber,
                                 PartName,
                                 PartType,
                                 Supplier,
                                 NgInfo,
                                 RepairMethod,
                                 Lot,
                                 ManufactureDate,
                                 Production_Line,
                                 0)
                #conn.commit()
                #toast("数据在本地保存完成")
                f=sync_ngrecord_volume()
                if f==True:
                    toast("数据已上传到服务器")
                else:
                    toast("数据上传到服务器失败，稍后重新启动app将再次尝试上传")
                self.ids.CarModel1.text=""
                self.ids.SeatModel1.text=""
                self.ids.WicoPartNumber1.text=""
                self.ids.TsPartNumber1.text=""
                self.ids.PartName1.text=""
                self.ids.PartType1.text=""
                self.Supplier1=""
                self.ids.NgInfo1.text=""
                self.ids.RepairMethod1.text=""
                self.ids.Lot1.text="点击扫码"
                self.ManufactureDate1=""
                self.Production_Line1="" 
            else:
                toast("此批次号的产品此前已经上传过不良信息了，请勿重复上传")
        else:
            toast("请将表单填写完整后再上传")

  
    def start_cam(self):
        self.root.current = 'camera'
        self.root.get_screen('camera').ids.zbarcam.ids.xcamera.play=True


    def decode(self,*args):
        barcode=args[0]
        WicoPartNumber,Production_Line,ManufactureDate=analysis_code(barcode)
        Supplier,PartType,WicoPartNumber,TsPartNumber,PartName,PartPicUrl,CarModel=get_CarModelBybar(WicoPartNumber)
        self.ids.PartType1.text=PartType
        self.ids.WicoPartNumber1.text=WicoPartNumber
        self.ids.TsPartNumber1.text=TsPartNumber
        self.ids.PartName1.text=PartName
        self.ids.part_image.source=PartPicUrl
        self.Supplier1=Supplier
        self.Production_Line1=Production_Line
        self.ManufactureDate1=ManufactureDate
        self.ids.CarModel1.text=""
        self.ids.SeatModel1.text=""
        self.ids.NgInfo1.text=""
        self.ids.RepairMethod1.text=""
        
        if len(CarModel)==1:
            self.ids.CarModel1.text=CarModel[0]
            SeatModel=get_SeatModelBybar(WicoPartNumber,CarModel[0])
            if len(SeatModel)==1:
                self.ids.SeatModel1.text=SeatModel[0]

        toast("{}线{}生产的产品".format(Production_Line,ManufactureDate))
        


class DemoApp(MDApp):

    def build(self):
        scn=Screen()
        scn.add_widget(EnterNgIfo())
        return scn

    
if __name__ == '__main__':
    #如果KV定义了一个Root Widget，它将附加到 App 的root 属性并用作应用程序的根部件，这个根部件附加完成后，再执行__init__中的代码。
    Builder.load_file( f"{os.environ['WICO_ROOT']}/enterngifo.kv" )
    DemoApp().run()
