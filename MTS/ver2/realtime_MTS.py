""" 
Created on Wed Jan 23 2019
 
MTS Program that graphs difference in mahalanobis distances, as well as an MTS 
 
@author: Taehee 
""" 
#
from __future__ import print_function
import sys
import os

# DB연결

import os
import pyodbc  
# 수치계산
import numpy as np 
import matplotlib as plt 
import copy 
import math
import csv
import pandas as pd
from sklearn import preprocessing

#--------------------------------------------------------------------------------#

# 함수화해서 객체 지향형으로 사용하자
# 





#---------------------------------------------------------------------------------------------#



# OKdata_factor_mean1,2
# OKdata_factor_std 1,2를 각각 받아오거나 하드코딩으로 저장해야 한다.
# 외부에서 read OKdata


# mssql 접속 2개 만들기 
conn = pyodbc.connect("Driver={SQL Server Native Client 10.0};"
                      "Server=172.20.51.45;"
                      "Database=ROLLCURLING_MONITORING;"
                      "Trusted_Connection=yes;")

#connection에서 cursor 생 (cursor는 fetch 동작 관리)
cursor = conn.cursor()
# OS와 맞는 DB설치할 것



cursor.execute("SELECT * from dbo.QMS_MONITORING_DATA  WHERE TIME = (select MAX(TIME) FROM dbo.QMS_MONITORING_DATA where DATE = (select max(DATE) FROM dbo.QMS_MONITORING_DATA where FLAG='Y') AND FLAG='Y') AND FLAG='Y' ORDER BY DATE DESC ; ")
    # from dbo.QMS_MONITORING_DATA  WHERE TIME = (select MAX(TIME) FROM dbo.QMS_MONITORING_DATA where DATE = (select max(DATE) FROM dbo.QMS_MONITORING_DATA where FLAG='Y') AND FLAG='Y') AND FLAG='Y' ORDER BY DATE DESC                          
    # VALUE01 : 축력하중(kgf)
    # VALUE02 : 컬링하중(kgf)
    # VALUE03 : 토크상한 누적시간
    # VALUE04 : RPM 편차(rpm)
    # VALUE05 : 높이측정(mm) (사용x)
    # VALUE06 : 완료위치(mm) (사용x)
    # VALUE07 : 높이측정-완료위치(mm)
    # VALUE08 : 단차 측정(mm) (SAM2라인 사용X)
    
row =cursor.fetchone()
print(row)

# base data에 넣기 위한 할당
date=row[0]
time=row[1]
wc=row[2]
car_type=row[4]
serial_n=row[5]
var_aweight=row[13]
var_cweight=row[14]
var_tqu=row[15]
var_rpm=row[16]
var10=None
var_h=row[19]
var13=None
var14=None





if row[2] == 'SAM2': # 차종 
    if row[4]== '140' or row[4] =='141' or row[4] == '142':
        print('case 1')
        # 여기서 각 모델을 돌림
        # 기능 3번을 사용하지 않고(do not streaming , do batch update for calculating base MTS)


        # DB data 불러오기
        row_array = []
        z_array = []

        cursor.execute("SELECT DATE,TIME,SPEC,SPEC2,VALUE01,VALUE02,VALUE03,VALUE04,VALUE07 from dbo.QMS_MONITORING_DATA  WHERE TIME = (select MAX(TIME) FROM dbo.QMS_MONITORING_DATA where DATE = (select max(DATE) FROM dbo.QMS_MONITORING_DATA where FLAG='Y') AND FLAG='Y') AND FLAG='Y' ORDER BY DATE DESC ; ")

        row = cursor.fetchone()
         # update를 위해 date와 time은 따로 변수로 저장
        date=row[0]
        time=row[1]
        spec1=row[2]
        spec2=row[3]
        print(date,time)
        # 나머지로 MD계산을 위해 array로 변환
        row_array = np.array(row[4:])
        k=5
        print("raw data:", row_array)

        
        # base data 불러오기
        OKdata_factor_mean=pd.read_csv("C:/Users/user/Desktop/MTS분석_python/cal_data_SAM2_1/OKdata_factor_mean.csv")
        OKdata_factor_std=pd.read_csv("C:/Users/user/Desktop/MTS분석_python/cal_data_SAM2_1/OKdata_factor_std.csv")
        cor=pd.read_csv("C:/Users/user/Desktop/MTS분석_python/cal_data_SAM2_1/cor.csv")

        OKdata_factor_mean=np.array(OKdata_factor_mean.drop(['Unnamed: 0'],1))
        OKdata_factor_std=np.array(OKdata_factor_std.drop(['Unnamed: 0'],1))
        cor=np.array(cor.drop(['Unnamed: 0'],1))


        #MD 연산

        for i in range(k):

            data_minus_mean = float(row_array[i])-OKdata_factor_mean[0][i]
            z = data_minus_mean/OKdata_factor_std[0][i]
            #print("z:",z)
            z_array.append(z)

        print("z:", z_array)
        z_transpose = np.transpose(z_array)
        #print(z_transpose)
        MD_1 = np.dot(z_array,cor)
        MD = np.dot(MD_1, z_transpose)
        D = np.sqrt(MD)

        print("MD:",MD,",","D:",D)
        
        # NG여부
        if MD > spec2 :
            result='NG2'
        elif MD > spec1:
            result='NG1'
        else:
            result='OK'
        print()
        print(result)
        
        cursor.execute("update dbo.QMS_MONITORING_DATA  set MD=('%s'),RESULT=('%s'),MD_FLAG=1 where DATE='%s' and TIME='%s';" %(MD,result,date,time) )
        cursor.commit()
        cursor.close()
        print("done")


        
    else: #기준 함수
        print('case 2')
        row_array = []
        z_array = []

        cursor.execute("SELECT DATE,TIME,SPEC,SPEC2,VALUE01,VALUE02,VALUE03,VALUE04,VALUE07 from dbo.QMS_MONITORING_DATA  WHERE TIME = (select MAX(TIME) FROM dbo.QMS_MONITORING_DATA where DATE = (select max(DATE) FROM dbo.QMS_MONITORING_DATA where FLAG='Y') AND FLAG='Y') AND FLAG='Y' ORDER BY DATE DESC ; ")

        row = cursor.fetchone()
         # update를 위해 date와 time은 따로 변수로 저장
        date=row[0]
        time=row[1]
        spec1=row[2]
        spec2=row[3]
        print(date,time)
        # 나머지로 MD계산을 위해 array로 변환
        row_array = np.array(row[4:])
        k=5
        print("raw data:", row_array)
        
        
        # base data 불러오기
        OKdata_factor_mean=pd.read_csv("C:/Users/user/Desktop/MTS분석_python/cal_data_SAM2_2/OKdata_factor_mean.csv")
        OKdata_factor_std=pd.read_csv("C:/Users/user/Desktop/MTS분석_python/cal_data_SAM2_2/OKdata_factor_std.csv")
        cor=pd.read_csv("C:/Users/user/Desktop/MTS분석_python/cal_data_SAM2_2/cor.csv")

        OKdata_factor_mean=np.array(OKdata_factor_mean.drop(['Unnamed: 0'],1))
        OKdata_factor_std=np.array(OKdata_factor_std.drop(['Unnamed: 0'],1))
        cor=np.array(cor.drop(['Unnamed: 0'],1))


        #MD 연산

        for i in range(k):

            data_minus_mean = float(row_array[i])-OKdata_factor_mean[0][i]
            z = data_minus_mean/OKdata_factor_std[0][i]
            #print("z:",z)
            z_array.append(z)

        print("z:", z_array)
        z_transpose = np.transpose(z_array)
        #print(z_transpose)
        MD_1 = np.dot(z_array,cor)
        MD = np.dot(MD_1, z_transpose)
        D = np.sqrt(MD)

        print("MD:",MD,",","D:",D)

        # NG여부를 안만들었음
        if MD > spec2 :
            result='NG2'
        elif MD > spec1:
            result='NG1'
        else:
            result='OK'
        print()
        print(result)        
        
        cursor.execute("update dbo.QMS_MONITORING_DATA  set MD=('%s'),RESULT=('%s'),MD_FLAG=1 where DATE='%s' and TIME='%s';" %(MD,result,date,time) )
        cursor.commit()
        cursor.close()
        print("done")
        # NG여부
        if MD > spec2 :
            ng='NG2'
        elif  MD > spec1:
            ng='NG1'
        else:
            ng='OK'

        
else: # SAA8인경우 
    if row[2]== '10' or row[2] =='12':
        
        print('case 3')
        row_array = []
        z_array = []

        cursor.execute("SELECT DATE,TIME,SPEC,SPEC2,VALUE01,VALUE02,VALUE03,VALUE04,VALUE07 from dbo.QMS_MONITORING_DATA  WHERE TIME = (select MAX(TIME) FROM dbo.QMS_MONITORING_DATA where DATE = (select max(DATE) FROM dbo.QMS_MONITORING_DATA where FLAG='Y') AND FLAG='Y') AND FLAG='Y' ORDER BY DATE DESC ; ")

        row = cursor.fetchone()
         # update를 위해 date와 time은 따로 변수로 저장
        date=row[0]
        time=row[1]
        spec1=row[2]
        spec2=row[3]
        print(date,time)
        # 나머지로 MD계산을 위해 array로 변환
        row_array = np.array(row[4:])
        k=5
        print("raw data:", row_array)
        
        
        # base data 불러오기
        OKdata_factor_mean=pd.read_csv("C:/Users/user/Desktop/MTS분석_python/cal_data_SAA8_1/OKdata_factor_mean.csv")
        OKdata_factor_std=pd.read_csv("C:/Users/user/Desktop/MTS분석_python/cal_data_SAA8_1/OKdata_factor_std.csv")
        cor=pd.read_csv("C:/Users/user/Desktop/MTS분석_python/cal_data_SAA8_1/cor.csv")

        OKdata_factor_mean=np.array(OKdata_factor_mean.drop(['Unnamed: 0'],1))
        OKdata_factor_std=np.array(OKdata_factor_std.drop(['Unnamed: 0'],1))
        cor=np.array(cor.drop(['Unnamed: 0'],1))


        #MD 연산

        for i in range(k):

            data_minus_mean = float(row_array[i])-OKdata_factor_mean[0][i]
            z = data_minus_mean/OKdata_factor_std[0][i]
            #print("z:",z)
            z_array.append(z)

        print("z:", z_array)
        z_transpose = np.transpose(z_array)
        #print(z_transpose)
        MD_1 = np.dot(z_array,cor)
        MD = np.dot(MD_1, z_transpose)
        D = np.sqrt(MD)

        print("MD:",MD,",","D:",D)


        # NG여부
        if MD > spec2 :
            result='NG2'
        elif MD > spec1:
            result='NG1'
        else:
            result='OK'
        print()
        print(result)
        
        
        cursor.execute("update dbo.QMS_MONITORING_DATA  set MD=('%s'),RESULT=('%s'),MD_FLAG=1 where DATE='%s' and TIME='%s';" %(MD,result,date,time) )
        cursor.commit()
        cursor.close()


        print("done")

            
    else:
        print('case 4')
                row_array = []
        z_array = []

        cursor.execute("SELECT DATE,TIME,SPEC,SPEC2,VALUE01,VALUE02,VALUE03,VALUE04,VALUE07 from dbo.QMS_MONITORING_DATA  WHERE TIME = (select MAX(TIME) FROM dbo.QMS_MONITORING_DATA where DATE = (select max(DATE) FROM dbo.QMS_MONITORING_DATA where FLAG='Y') AND FLAG='Y') AND FLAG='Y' ORDER BY DATE DESC ; ")

        row = cursor.fetchone()
         # update를 위해 date와 time은 따로 변수로 저장
        date=row[0]
        time=row[1]
        spec1=row[2]
        spec2=row[3]
        print(date,time)
        # 나머지로 MD계산을 위해 array로 변환
        row_array = np.array(row[4:])
        k=5
        print("raw data:", row_array)
        
        
        # base data 불러오기
        OKdata_factor_mean=pd.read_csv("C:/Users/user/Desktop/MTS분석_python/cal_data_SAA8_2/OKdata_factor_mean.csv")
        OKdata_factor_std=pd.read_csv("C:/Users/user/Desktop/MTS분석_python/cal_data_SAA8_2/OKdata_factor_std.csv")
        cor=pd.read_csv("C:/Users/user/Desktop/MTS분석_python/cal_data_SAA8_2/cor.csv")

        OKdata_factor_mean=np.array(OKdata_factor_mean.drop(['Unnamed: 0'],1))
        OKdata_factor_std=np.array(OKdata_factor_std.drop(['Unnamed: 0'],1))
        cor=np.array(cor.drop(['Unnamed: 0'],1))


        #MD 연산

        for i in range(k):

            data_minus_mean = float(row_array[i])-OKdata_factor_mean[0][i]
            z = data_minus_mean/OKdata_factor_std[0][i]
            #print("z:",z)
            z_array.append(z)

        print("z:", z_array)
        z_transpose = np.transpose(z_array)
        #print(z_transpose)
        MD_1 = np.dot(z_array,cor)
        MD = np.dot(MD_1, z_transpose)
        D = np.sqrt(MD)

        print("MD:",MD,",","D:",D)


        # NG여부
        if MD > spec2 :
            result='NG2'
        elif MD > spec1:
            result='NG1'
        else:
            result='OK'
        print()
        print(result)
        
        
        cursor.execute("update dbo.QMS_MONITORING_DATA  set MD=('%s'),RESULT=('%s'),MD_FLAG=1 where DATE='%s' and TIME='%s';" %(MD,result,date,time) )
        cursor.commit()
        cursor.close()

        print("done")









        
