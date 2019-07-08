""" 
Created on Wed Jan 23 2019
 
MTS Program that graphs difference in mahalanobis distances, as well as an MTS 
 
@author: Taehee 
""" 
# DB연결
from __future__ import print_function
import os
import pyodbc  
# 수치계산
import numpy as np 
import matplotlib as plt 
import pandas as pd
from sklearn import preprocessing

# 버전확인
import sys
import PyQt5
print(sys.version)


def remakeNomarlMTS():
    # mssql 접속 2개 만들기 
    conn = pyodbc.connect("Driver={SQL Server Native Client 10.0};"
                          "Server=172.20.51.45;"
                          "Database=ROLLCURLING_MONITORING;"
                          "Trusted_Connection=yes;")

    #connection에서 cursor 생 (cursor는 fetch 동작 관리)
    cursor = conn.cursor()
    # OS와 맞는 DB설치할 것
    cursor.execute("drop table dbo.SAA8_MTS_BASE_DATA1; ") # 기존 base table 삭제
    cursor.execute("select top 5000 WC,DATE,TIME,CAR_TYPE,VALUE01,VALUE02,VALUE03,VALUE04,(VALUE07+50)VALUE07 into dbo.SAA8_MTS_BASE_DATA1 from dbo.QMS_MONITORING_DATA where WC='SAA8' and FLAG='Y' and (CAR_TYPE='10' or CAR_TYPE='12')  ; ")
    cursor.commit()
    # cursor.execute("select value01,value02,value03,value04,value07 from dbo.SAA8_MTS_BASE_DATA1 ") #안쓰는 코드
        # VALUE01 : 축력하중(kgf)
        # VALUE02 : 컬링하중(kgf)
        # VALUE03 : 토크상한 누적시간
        # VALUE04 : RPM 편차(rpm)
        # VALUE05 : 높이측정(mm) (사용x)
        # VALUE06 : 완료위치(mm) (사용x)
        # VALUE07 : 높이측정-완료위치(mm)
        # VALUE08 : 단차 측정(mm) (SAM2라인 사용X)


    SQL_Query = pd.read_sql_query('''select value01,value02,value03,value04,value07 from dbo.SAA8_MTS_BASE_DATA1''',conn)


    
    n = SQL_Query.shape[0]
    k = SQL_Query.shape[1]
    print("제품 수(n):",n,",","factor 수(k):",k)

   
    
    OKdata_factor_mean=[]
    OKdata_factor_std=[]

    
    for i in range(k):
        OKdata_factor_mean.append(float(SQL_Query.mean(axis=0)[i]))
        OKdata_factor_std.append(float(SQL_Query.std(axis=0)[i]))
        

    # 데이터 정규화(Z)
    scaler = preprocessing.StandardScaler()
    scaled_df_ok = scaler.fit_transform(SQL_Query)

    # 상관계수(R) 구하기
    pd_scaled_df_ok = pd.DataFrame(scaled_df_ok)
    OKdata_corr = pd_scaled_df_ok.corr()
    OKdata_corr
    OKdata_corr.shape

    # 상관계수의 역함수(R^-1)
    cor =np.linalg.inv(OKdata_corr)

    conn.close()
    
    
    # 파일로 저장
    OKdata_factor_mean=pd.DataFrame(OKdata_factor_mean).T
    OKdata_factor_std=pd.DataFrame(OKdata_factor_std).T
    cor=pd.DataFrame(cor)
    
    os.chdir("C:/Users/user/Desktop/MTS분석_python/cal_data_SAA8_1")
    OKdata_factor_mean.to_csv("OKdata_factor_mean.csv")
    OKdata_factor_std.to_csv("OKdata_factor_std.csv")
    cor.to_csv("cor.csv")



remakeNomarlMTS()
