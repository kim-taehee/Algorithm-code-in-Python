#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import pyodbc

import numpy as np 
import matplotlib as plt 
import pandas as pd
from sklearn import preprocessing


import json
from collections import OrderedDict


# In[2]:



from flask import Flask
from flask_restful import Resource, Api
from flask_restful import reqparse, abort, Api, Resource

# make rule grape with deviation, mean from actucater data
# like SPC

app = Flask(__name__)
api = Api(app)


# In[3]:


LINE_group = OrderedDict()
OP_group = OrderedDict()


# In[34]:




def CalActuater(OP_NO,CYCLE_SEQ):
    #print(OP_NO,STATUS_BIT) chk point1
    conn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                              "Server=MDPLP1546701\\SQLEXPRESS;"
                              "Database=CETA_LMS;"
                              "Trusted_Connection=yes;")
    cursor = conn.cursor()  
    cursor.execute(''' SELECT TOP (1000) 
                            avg(DATEDIFF([MS],[STATUS_SDATE],[STATUS_EDATE])) as avg_mstime ,
            convert(int, STDEV(DATEDIFF([MS],[STATUS_SDATE],[STATUS_EDATE]))) as std_mstime  ,                                 
            STD_MCH_STATUS_INFO.STATUS_IO_NO
                        FROM [CETA_LMS].[dbo].[MCH_STATUS_SUMMARY] 
            left outer join CETA_LMS.dbo.STD_MCH_STATUS_INFO 
                            on MCH_STATUS_SUMMARY.STATUS_BIT = STD_MCH_STATUS_INFO.STATUS_IO_NO and MCH_STATUS_SUMMARY.OP_NO =STD_MCH_STATUS_INFO.OP_NO
                        Where  MCH_STATUS_SUMMARY.OP_NO=('%s')
            group by STD_MCH_STATUS_INFO.STATUS_IO_NO; '''  %(OP_NO) )  
                        # sql string으로 두고 excute안에 string으로        
    rs = cursor.fetchall()
    avg_byIO=pd.DataFrame(np.array(rs),columns=["avg_time","std_time","IO_NO"])
    pd.to_numeric(avg_byIO['avg_time'])
    pd.to_numeric(avg_byIO['std_time'])

        # 아래부터 NG여부 판단
    cursor = conn.cursor()  
    cursor.execute(''' SELECT 
                sum(DATEDIFF([MS],[STATUS_SDATE],[STATUS_EDATE])) as mstime ,
                        STD_MCH_STATUS_INFO.STATUS_IO_NO
                FROM [CETA_LMS].[dbo].[MCH_STATUS_SUMMARY]
                        left outer join CETA_LMS.dbo.STD_MCH_STATUS_INFO 
                        on MCH_STATUS_SUMMARY.STATUS_BIT = STD_MCH_STATUS_INFO.STATUS_IO_NO and MCH_STATUS_SUMMARY.OP_NO =STD_MCH_STATUS_INFO.OP_NO
                where MCH_STATUS_SUMMARY.CYCLE_SEQ= ('%s') and MCH_STATUS_SUMMARY.OP_NO=('%s')
                group by CYCLE_SEQ,STD_MCH_STATUS_INFO.STATUS_IO_NO ; '''  %(CYCLE_SEQ,OP_NO) )  
    newdata= cursor.fetchall() #op,bit,time(ms) 
    seq_list_byIO=pd.DataFrame(np.array(newdata),columns=["seq_time","IO_NO"])
    pd.to_numeric(seq_list_byIO['seq_time'])

    cursor.close()
    last_table=pd.merge(avg_byIO,seq_list_byIO,how='right',on='IO_NO')
    last_table['max_time']=pd.to_numeric(last_table['avg_time'])+pd.to_numeric(last_table['std_time'])
    last_table['min_time']=pd.to_numeric(last_table['avg_time'])-pd.to_numeric(last_table['std_time'])
    last_table['z_score']=(pd.to_numeric(last_table['avg_time'])-pd.to_numeric(last_table['seq_time']))/pd.to_numeric(last_table['std_time'])
    last_table['result']=0


    for i in range(0,len(last_table)):
        if (last_table.iloc[i,6] > 1):
            last_table.iloc[i,7]='NG'
        elif(last_table.iloc[i,6] < -1):
            last_table.iloc[i,7] ='NG'
        else:
            last_table.iloc[i,7] ='OK'
    last_table.index=last_table['IO_NO']
    last_table=last_table.iloc[:,[0,3,4,5,7]]
    string =last_table.to_json(orient='index')
    end=json.loads(string)
    return end






# In[ ]:


#예외 처리
def Abort_if_OP_exist(OP_NO):
    if OP_group not in LINE_group:
        abort(404, message="OP_NO {} doesn't exist".format(OP_NO))

def Abort_if_actu_exist(act):
    if act not in OP_group:
        abort(404, message="CYCLE_SEQ {} doesn't exist".format(act))

parser = reqparse.RequestParser()
parser.add_argument('task')


# Get, Delete, Put 정의


class Calseq(Resource):
    def get(self,OP_NO,CYCLE_SEQ):
        result=CalActuater(OP_NO,CYCLE_SEQ)
        return result

    def post(self):
        args = parser.parse_args()
        OP_group = 'line%d' % (len(LINE_group) + 1)
        LINE_group[OP_group] = {'task': args['task']}
        return OP_group[OP_NO], 201

##
## URL Router에 맵핑한다.(Rest URL정의)
##

api.add_resource(Calseq, '/CETA31/<string:OP_NO>/<string:CYCLE_SEQ>/')


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')

