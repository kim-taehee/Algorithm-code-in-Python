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
SQL_Query = pd.read_sql_query('''SELECT top 3 DATE,TIME,SPEC,SPEC2,WC,CAR_TYPE,VALUE01,VALUE02,VALUE03,VALUE04,VALUE07 from dbo.QMS_MONITORING_DATA  where FLAG ='Y' order by DATE desc, TIME desc ''',conn)


    # VALUE01 : 축력하중(kgf)
    # VALUE02 : 컬링하중(kgf)
    # VALUE03 : 토크상한 누적시간
    # VALUE04 : RPM 편차(rpm)
    # VALUE05 : 높이측정(mm) (사용x)
    # VALUE06 : 완료위치(mm) (사용x)
    # VALUE07 : 높이측정-완료위치(mm)
    # VALUE08 : 단차 측정(mm) (SAM2라인 사용X)
    


# base data에 넣기 위한 할당
    


print(SQL_Query)

for i in range(3) :
    print(SQL_Query.iloc[[i]])
    date=SQL_Query.iloc[i,0]
    time=SQL_Query.iloc[i,1]
    spec1=SQL_Query.iloc[i,2]
    spec2=SQL_Query.iloc[i,3]
    WC=SQL_Query.iloc[i,4]
    car_type=SQL_Query.iloc[i,5]


    if WC == 'SAM2': # 차종 
        if car_type== '140' or car_type =='141' or car_type == '142':
            print('case 1')
            # 여기서 각 모델을 돌림
            # 기능 3번을 사용하지 않고(do not streaming , do batch update for calculating base MTS)

            # DB data 불러오기
            row_array = []
            z_array = []

            # 나머지로 MD계산을 위해 array로 변환
            row_array = np.array(SQL_Query.iloc[i,6:])
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
 
            print("done")


            
        else: #기준 함수
            print('case 2')
            row_array = []
            z_array = []

          
            # 나머지로 MD계산을 위해 array로 변환
            row_array = np.array(SQL_Query.iloc[i,6:])
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
        
            print("done")
            # NG여부
            if MD > spec2 :
                ng='NG2'
            elif  MD > spec1:
                ng='NG1'
            else:
                ng='OK'

            
    else: # SAA8인경우 
        if car_type== '10' or car_type =='12':
            
            print('case 3')
            row_array = []
            z_array = []


            # 나머지로 MD계산을 위해 array로 변환
            row_array = np.array(SQL_Query.iloc[i,6:])
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
    


            print("done")

                
        else:
            print('case 4')
            row_array = []
            z_array = []


            # 나머지로 MD계산을 위해 array로 변환
            row_array = np.array(SQL_Query.iloc[i,6:])
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
      

            print("done")


cursor.close()






            

