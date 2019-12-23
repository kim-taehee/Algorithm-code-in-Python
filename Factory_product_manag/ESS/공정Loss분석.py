#!/usr/bin/env python
# coding: utf-8

# In[4]:


import os
import pyodbc

import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

font_path = 'C:/Windows/Fonts/gulim.ttc'
fontprop = fm.FontProperties(fname=font_path, size=18)
plt.rcParams["figure.figsize"] = (20,5)
plt.rcParams['lines.color'] = 'b'
import pandas as pd
from sklearn import preprocessing


# In[5]:


def makeplot(time,mch):
    conn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                              "Server=172.20.66.89;"
                              "Database=CEPS4MSV_%s;"
                              "UID=ceps1;"
                              "PWD=ceps1" %(time))

    cursor = conn.cursor()  
    cursor.execute(''' SELECT ProcNO,ErrMsg ,  
          sum(dTIME)/1000 as stime_byProcNO,
          avg(dTIME) as atime_byProcNO,
          count(ErrMsg) as cnt
          FROM [CEPS4MSV_201911].[dbo].[ERRLOG]
          group by ProcNO ,ErrMsg 
          order by ProcNo asc ,ErrMsg asc  ''')
    rs = cursor.fetchall()
    df=pd.DataFrame(np.array(rs),columns=["Proc","ErrMsg","stime_byProcNo","atime_byProcNo","cnt"])
    df['cnt']=pd.to_numeric(df['cnt'])
    aa=df.ErrMsg.str.split(' ').str[1]
    df['ErrMsg']='Err'+aa
    
    df1=df[(df['Proc']==str(mch))]; 
    
    
    
    plt.subplot(121)
    plt.bar('ErrMsg','cnt',data=df1 )
    plt.title('HSG체결 cnt',fontproperties=fontprop)
    plt.subplot(122)
    plt.bar('ErrMsg','stime_byProcNo',data=df1)
    plt.title('HSG체결 err_time_sum',fontproperties=fontprop)

    


# In[6]:


makeplot(201911,2) #년월, 설비번호


# In[ ]:




