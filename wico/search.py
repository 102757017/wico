#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sqlite3
import time
import os
import sys
import pprint
import datetime
from pathlib import Path
from kivy.logger import Logger
import traceback
import mysql.connector as mariadb
from datetime import timedelta


if getattr(sys, "frozen", False):  # bundle mode with PyInstaller
    os.environ["WICO_ROOT"] = sys._MEIPASS
else:
    os.environ["WICO_ROOT"] = str(Path(__file__).parent)

KV_DIR = f"{os.environ['WICO_ROOT']}"



# 连接到SQLite数据库
# 数据库文件是test.db
# 如果文件不存在，会自动在当前目录创建:
conn = sqlite3.connect(f"{os.environ['WICO_ROOT']}/db.db")

'''
conn_server = mariadb.connect(host='localhost',
                             user='user',
                             password='passwd',
                             database='db',
                             cursorclass=mariadb.cursors.DictCursor)
'''

def get_CarModel():
    t=datetime.datetime.now()-datetime.timedelta(days=7)
    # 创建一个Cursor:
    cursor = conn.cursor()
    sqlcmd='''
            SELECT
            t1.CarModel
            FROM
            (SELECT distinct CarModel from seatlist) as t1
            left join 
            (SELECT CarModel ,SUM(DAY)+ SUM(Night) as quantity FROM volume WHERE C_M_Date>"{}" GROUP BY CarModel ) as t2
            on
            t1.CarModel = t2.CarModel
            ORDER BY
            t2.quantity DESC,
            t1.CarModel
            '''.format(t.strftime("%Y-%m-%d"))
    cursor.execute(sqlcmd)
    values = cursor.fetchall()
    cursor.close()
    CarModel=[]
    for x in values:
        CarModel.append(x[0])
    return CarModel



def get_SeatModel(CarModel):
    cursor = conn.cursor()
    sqlcmd='''
    SELECT
    seatlist.SeatModel
    FROM
    seatlist
    WHERE seatlist.CarModel = "{}"
    GROUP BY
    seatlist.SeatModel
    ORDER BY
    seatlist.SeatModel desc
    '''.format(CarModel)
    cursor.execute(sqlcmd)
    values = cursor.fetchall()
    cursor.close()
    SeatModel=[]
    if len(values)>0:
        for x in values:
            SeatModel.append(x[0])
    return SeatModel





def get_PartType(CarModel,SeatModel):
    cursor = conn.cursor()
    sqlcmd='''
    SELECT
    partlist.PartType
    FROM
    seatlist
    INNER JOIN partlist ON seatlist.WicoPartNumber = partlist.WicoPartNumber
    WHERE
    seatlist.CarModel = "{}" AND
    seatlist.SeatModel = "{}"
    GROUP BY
    partlist.PartType
    '''.format(CarModel,SeatModel)
    cursor.execute(sqlcmd)
    values = cursor.fetchall()
    cursor.close()
    PartType=[]
    if len(values)>0:
        for x in values:
            PartType.append(x[0])
    return PartType


def get_PartNumberName(CarModel,SeatModel,PartType):
    cursor = conn.cursor()
    sqlcmd='''
    SELECT
    partlist.WicoPartNumber,
    partlist.TsPartNumber,
    partlist.PartName,
    partlist.Supplier,
    partlist.Regular,
    partlist."Production Line",
    partlist.PartPicUrl
    FROM
    seatlist
    INNER JOIN partlist ON seatlist.WicoPartNumber = partlist.WicoPartNumber
    WHERE
    seatlist.CarModel = "{}" AND
    seatlist.SeatModel = "{}" AND
    partlist.PartType = "{}"
    '''.format(CarModel,SeatModel,PartType)
    cursor.execute(sqlcmd)
    values = cursor.fetchall()
    cursor.close()
    WicoPartNumber=[]
    TsPartNumber=[]
    PartName=[]
    Supplier=[]
    Regular=[]
    Production_Line=[]
    PartPicUrl=[]
    if len(values)>0:
        for x in values:
            WicoPartNumber.append(x[0])
            TsPartNumber.append(x[1])
            PartName.append(x[2])
            Supplier.append(x[3])
            Regular.append(x[4])
            Production_Line.append(x[5])
            PartPicUrl.append(x[6])
    return WicoPartNumber,TsPartNumber,PartName,Supplier,Regular,Production_Line,PartPicUrl

    



def get_DetailByName(CarModel,SeatModel,PartType,PartName):
    cursor = conn.cursor()
    sqlcmd='''
    SELECT
    partlist.WicoPartNumber,
    partlist.TsPartNumber,
    partlist.PartName,
    partlist.PartPicUrl,
    partlist."Production Line",
    partlist.Regular
    FROM
    seatlist
    INNER JOIN partlist ON seatlist.WicoPartNumber = partlist.WicoPartNumber
    WHERE
    seatlist.CarModel = "{}" AND
    seatlist.SeatModel = "{}" AND
    partlist.PartType = "{}" AND
    partlist.PartName = "{}"
    '''.format(CarModel,SeatModel,PartType,PartName)
    cursor.execute(sqlcmd)
    values = cursor.fetchall()
    cursor.close()
    if len(values)>0:
        WicoPartNumber,TsPartNumber,PartName,PartPicUrl,Production_Line,Regular=values[0]
    else:
        WicoPartNumber,TsPartNumber,PartName,PartPicUrl,Production_Line,Regular="","","","","",""
    return WicoPartNumber,TsPartNumber,PartName,PartPicUrl,Production_Line,Regular



def get_DetailByNum(CarModel,SeatModel,PartType,PartName):
    cursor = conn.cursor()
    sqlcmd='''
    SELECT
    partlist.WicoPartNumber,
    partlist.TsPartNumber,
    partlist.PartName,
    partlist.PartPicUrl,
    partlist."Production Line",
    partlist.Regular
    FROM
    seatlist
    INNER JOIN partlist ON seatlist.WicoPartNumber = partlist.WicoPartNumber
    WHERE
    seatlist.CarModel = "{}" AND
    seatlist.SeatModel = "{}" AND
    partlist.PartType = "{}" AND
    partlist.TsPartNumber = "{}"
    '''.format(CarModel,SeatModel,PartType,PartName)
    cursor.execute(sqlcmd)
    values = cursor.fetchall()
    cursor.close()
    if len(values)>0:
        WicoPartNumber,TsPartNumber,PartName,PartPicUrl,Production_Line,Regular=values[0]
    else:
        WicoPartNumber,TsPartNumber,PartName,PartPicUrl,Production_Line,Regular="","","","","",""
    return WicoPartNumber,TsPartNumber,PartName,PartPicUrl,Production_Line,Regular



#使用扫条码的方式获取产品信息
def get_Regulars():
    # 创建一个Cursor:
    cursor = conn.cursor()
    sqlcmd='''
    SELECT
    WicoPartNumber,
    Regular,
    count(Regular) as c
    FROM
    partlist
    WHERE
    Regular != ""
    GROUP BY Regular
    HAVING c=1
    '''
    cursor.execute(sqlcmd)
    values = cursor.fetchall()
    cursor.close()
    return values
 

def get_CarModelBybar(WicoPartNumber):
    cursor = conn.cursor()
    sqlcmd='''
    SELECT
    partlist.Supplier,
    partlist.PartType,
    partlist.WicoPartNumber,
    partlist.TsPartNumber,
    partlist.PartName,
    partlist.PartPicUrl,
    seatlist.CarModel
    FROM
    seatlist
    INNER JOIN partlist ON seatlist.WicoPartNumber = partlist.WicoPartNumber
    WHERE
    partlist.WicoPartNumber = "{}"
    GROUP BY seatlist.CarModel
    '''.format(WicoPartNumber)
    cursor.execute(sqlcmd)
    values = cursor.fetchall()
    cursor.close()
    if len(values)>0:
        Supplier,PartType,WicoPartNumber,TsPartNumber,PartName,PartPicUrl=values[0][0:6]
        CarModel=[]
        for x in values:
            CarModel.append(x[6])
    else:
        Supplier,PartType,WicoPartNumber,TsPartNumber,PartName,PartPicUrl,CarModel="","","","","","",""
    return Supplier,PartType,WicoPartNumber,TsPartNumber,PartName,PartPicUrl,CarModel

def get_SeatModelBybar(WicoPartNumber,CarModel):
    cursor = conn.cursor()
    sqlcmd='''
    SELECT
    seatlist.SeatModel
    FROM
    seatlist
    INNER JOIN partlist ON seatlist.WicoPartNumber = partlist.WicoPartNumber
    WHERE
    partlist.WicoPartNumber = "{}" AND
    seatlist.CarModel = "{}"
    '''.format(WicoPartNumber,CarModel)
    cursor.execute(sqlcmd)
    values = cursor.fetchall()
    cursor.close()
    SeatModel=[]
    if len(values)>0:
        for x in values:
            SeatModel.append(x[0]) 
    return SeatModel


def get_NgInfo(PartType):
    cursor = conn.cursor()
    sqlcmd='''
    SELECT
            t1.NgInfo
    FROM
            (
            SELECT
                    NgInfo
            FROM
                    ngtype
            WHERE
                    PartType = "{}"
            GROUP BY
                    NgInfo) as t1
    left join 
            (
            SELECT
                    NgInfo,
                    COUNT(NgInfo) as quantity
            FROM
                    ngrecord
            WHERE
                    PartType = "{}"
            GROUP BY
                    NgInfo) as t2
    on
            t1.NgInfo = t2.NgInfo
    ORDER BY
            quantity DESC
    '''.format(PartType,PartType)
    cursor.execute(sqlcmd)
    values = cursor.fetchall()
    cursor.close()
    NgInfo=[]
    if len(values)>0:
        for x in values:
            NgInfo.append(x[0]) 
    return NgInfo


def get_RepairMethod(PartType,NgInfo):
    cursor = conn.cursor()
    sqlcmd='''
    SELECT
    RepairMethod
    FROM
    ngtype
    WHERE
    PartType = "{}" AND
    NgInfo = "{}"
    '''.format(PartType,NgInfo)
    cursor.execute(sqlcmd)
    values = cursor.fetchall()
    cursor.close()
    RepairMethod=[]
    if len(values)>0:
        for x in values:
            RepairMethod.append(x[0]) 
    return RepairMethod

def search_barcode(WicoPartNumber,barcode):
    cursor = conn.cursor()
    sqlcmd='''
    SELECT
    *
    FROM
    ngrecord
    WHERE
    WicoPartNumber = "{}" AND
    Lot = "{}"
    '''.format(WicoPartNumber,barcode)
    cursor.execute(sqlcmd)
    values = cursor.fetchall()
    cursor.close()
    if len(values)>0:
        return True
    else:
        return False


def uploade_ngrecord(NgTime, CarModel, SeatModel, WicoPartNumber, TsPartNumber, PartName, PartType, Supplier, NgInfo, RepairMethod, Lot, ManufactureDate, Production_Line, Sync):
    if Lot=="":
        Lot="NULL"
    else:
        Lot="'{}'".format(Lot)
        
    if ManufactureDate=="":
        ManufactureDate="NULL"
    else:
        ManufactureDate="'{}'".format(ManufactureDate)
        
    if Production_Line=="":
        Production_Line="NULL"
    else:
        Production_Line="'{}'".format(Production_Line)
    
    cursor = conn.cursor()
    sqlcmd='''
    INSERT INTO ngrecord
    (NgTime, CarModel, SeatModel, WicoPartNumber, TsPartNumber, PartName, PartType, Supplier, NgInfo, RepairMethod, Lot, ManufactureDate, "Production Line", Sync)
    VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', {}, {}, {}, 0)
    '''.format(NgTime, CarModel, SeatModel, WicoPartNumber, TsPartNumber, PartName, PartType, Supplier, NgInfo, RepairMethod, Lot, ManufactureDate, Production_Line, Sync)
    #print(sqlcmd)
    cursor.execute(sqlcmd)
    values = cursor.fetchall()
    cursor.close()
    conn.commit()
    #add_seat(CarModel,SeatModel,NgTime)
    return conn

#添加不良记录后同步添加该座椅的产量记录。
def add_seat(CarModel,SeatModel,NgTime):
    C_M_Date=datetime.datetime.strptime(NgTime, "%Y-%m-%d %H:%M:%S")-datetime.timedelta(hours=8)
    C_M_Date=C_M_Date.strftime("%Y-%m-%d")
    cursor = conn.cursor()
    sqlcmd='''
    SELECT
    C_M_Date,
    CarModel,
    SeatModel,
    Day,
    Night,
    Sync 
    FROM
    volume
    WHERE
    C_M_Date = "{}" AND
    CarModel = "{}" AND
    SeatModel  = "{}"
    '''.format(C_M_Date,CarModel,SeatModel)
    cursor.execute(sqlcmd)
    values = cursor.fetchall()
    cursor.close()
    
    if values==[]:
        data=(C_M_Date, CarModel,SeatModel, '0', '0', 0)
        submit_volume(data)
    return values



def query_volume_local(C_M_Date):
    cursor = conn.cursor()
    sqlcmd='''
    SELECT
    C_M_Date,
    CarModel,
    SeatModel,
    Day,
    Night,
    Sync 
    FROM
    volume
    WHERE
    C_M_Date = "{}"
    ORDER BY CarModel,SeatModel
    '''.format(C_M_Date)
    cursor.execute(sqlcmd)
    values = cursor.fetchall()
    cursor.close()
    return values

def query_volume_server(C_M_Date):
    try: 
        mariadb_conn = mariadb.connect( 
        user="imasenwh", 
        password="596bf648aa7f80d8", 
        host="mysql.sqlpub.com", 
        port=3306, 
        database="custom_feedback" )

        mariadb_cursor = mariadb_conn.cursor()
        
        sqlcmd='''
        SELECT
        C_M_Date,
        CarModel,
        SeatModel,
        Day,
        Night,
        Sync 
        FROM
        volume
        WHERE
        C_M_Date = "{}"
        ORDER BY CarModel,SeatModel
        '''.format(C_M_Date)
        mariadb_cursor.execute(sqlcmd)
        values = mariadb_cursor.fetchall()
        mariadb_cursor.close()
        return values
       
    except Exception:
        print(traceback.format_exc())
        return None



def query_nginfo(date):
    Timer = datetime.datetime.strptime(date, "%Y-%m-%d")
    start_time=Timer+timedelta(hours=8)
    end_time=Timer+timedelta(hours=32)
    start_time=datetime.datetime.strftime(start_time, "%Y-%m-%d %H:%M:%S")
    end_time=datetime.datetime.strftime(end_time, "%Y-%m-%d %H:%M:%S")
    
    try: 
        mariadb_conn = mariadb.connect( 
        user="imasenwh", 
        password="596bf648aa7f80d8", 
        host="mysql.sqlpub.com", 
        port=3306, 
        database="custom_feedback" )

        mariadb_cursor = mariadb_conn.cursor()
        
        sqlcmd='''
            SELECT
                    substring(Ngtime,12,8),
                    CarModel,
                    SeatModel,
                    NgInfo,
                    RepairMethod,
                    WicoPartNumber,
                    TsPartNumber,
                    PartName,
                    Lot,
                    ManufactureDate
            FROM
                    ngrecord
            WHERE NgTime>"{}" and NgTime<"{}"
            ORDER BY Ngtime DESC
        '''.format(start_time,end_time)
        mariadb_cursor.execute(sqlcmd)
        values = mariadb_cursor.fetchall()
        mariadb_cursor.close()
        return values
        
    except Exception:
        print(traceback.format_exc())
        return []



def submit_volume(data):
    conn = sqlite3.connect(f"{os.environ['WICO_ROOT']}/db.db")
    cursor = conn.cursor()
    sqlcmd='''
    REPLACE
    INTO
	volume
    (C_M_Date,CarModel,SeatModel,Day,Night,Sync)
    VALUES
    {}
    '''.format(data)
    #print(sqlcmd)
    #print(data)
    cursor.execute(sqlcmd)
    values = cursor.fetchall()
    cursor.close()
    conn.commit()
    return values



# 提交事务:execute后数据已经进入了数据库,但是如果最后没有commit 的话已经进入数据库的数据会被清除掉，自动回滚
#conn.commit()


# 关闭数据库
#conn.close()




if __name__=="__main__":

    CarModel=get_CarModel()
    pprint.pprint(CarModel)

    SeatModel=get_SeatModel("2VH")
    pprint.pprint(SeatModel)

    PartType=get_PartType("2VH","手动-前排-左席座椅")
    pprint.pprint(PartType)

    WicoPartNumber,TsPartNumber,PartName,Supplier,Regular,Production_Line,PartPicUrl=get_PartNumberName("2VH","手动-前排-左席座椅","手动滑轨")
    pprint.pprint(WicoPartNumber)
    pprint.pprint(TsPartNumber)
    pprint.pprint(PartName)
    pprint.pprint(Supplier)
    pprint.pprint(Regular)
    pprint.pprint(Production_Line)
    pprint.pprint(PartPicUrl)

    a=search_barcode("21-3390210W-2","1")
    print(a)
    

    '''
    WicoPartNumber,TsPartNumber,PartName,PartPicUrl,Production_Line,Regular=get_DetailByName("2VH","手动-前排-左席座椅","手动滑轨","SLIDE ADJR OUT L,FR SEAT")
    print(WicoPartNumber,TsPartNumber,PartName,PartPicUrl,Production_Line,Regular)


    WicoPartNumber,TsPartNumber,PartName,PartPicUrl,Production_Line,Regular=get_DetailByNum("2VH","手动-前排-左席座椅","手动滑轨","81660-TBA6-X110-M1-0004")
    print("\n",WicoPartNumber,TsPartNumber,PartName,PartPicUrl,Production_Line,Regular)

    #使用扫码方式输入
    Regular=get_Regulars()

    Supplier,PartType,WicoPartNumber,TsPartNumber,PartName,PartPicUrl,CarModel=get_CarModelBybar("23-4855430-2")
    print("\n",PartType,WicoPartNumber,TsPartNumber,PartName,PartPicUrl,CarModel)

    SeatModel=get_SeatModelBybar("2311-419-120","2VH")
    print("\n",SeatModel)

    NgInfo=get_NgInfo("电动滑轨")
    print("\n",NgInfo)

    RepairMethod=get_RepairMethod("电动滑轨","滑动异音")
    print("\n",RepairMethod)

    uploade_ngrecord("2022-03-29 14:30:21", "2LQ", '手动-前排-左席座椅', WicoPartNumber, TsPartNumber, PartName, PartType, Supplier, '上导轨螺丝脱落', '更换滑轨', "lotnumber", "2022-03-29", "58106", 0)



    pprint.pprint(query_volume_local("2022-04-01"))
    
    submit_volume("2022-04-02","2YC","test-car","10","10")

    pprint.pprint(query_nginfo())
    '''

