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
STATUS_BIT_group_OP10 = OrderedDict()
STATUS_BIT_group_OP20 = OrderedDict()
STATUS_BIT_group_OP30 = OrderedDict()
STATUS_BIT_group_OP40 = OrderedDict()
STATUS_BIT_group_OP50 = OrderedDict()


# In[4]:


# odbc 에러로 인해 초기에 선언해줘야함, 소켓 통신 필요
#OP_NO=10
#STATUS_BIT=150


# In[34]:



def CalActuater(OP_NO,STATUS_BIT):
    try:
        #print(OP_NO,STATUS_BIT) chk point1
        conn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                                  "Server=MDPLP1546701\\SQLEXPRESS;"
                                  "Database=CETA_LMS;"
                                  "Trusted_Connection=yes;")
        cursor = conn.cursor()  
        cursor.execute(''' SELECT TOP (1000) [MCH_STATUS_SUMMARY].[OP_NO],
                    MCH_STATUS_SUMMARY.STATUS_BIT,DATEDIFF([MS],[STATUS_SDATE],
                    [STATUS_EDATE]) as mstime ,STD_MCH_STATUS_INFO.STATUS_DESC 
                    FROM [CETA_LMS].[dbo].[MCH_STATUS_SUMMARY] left outer join CETA_LMS.dbo.STD_MCH_STATUS_INFO 
                    on MCH_STATUS_SUMMARY.STATUS_BIT = STD_MCH_STATUS_INFO.STATUS_IO_NO and MCH_STATUS_SUMMARY.OP_NO =STD_MCH_STATUS_INFO.OP_NO
                    where MCH_STATUS_SUMMARY.STATUS_BIT= ('%s') and MCH_STATUS_SUMMARY.OP_NO=('%s'); '''  %(STATUS_BIT,OP_NO) )  
                # sql string으로 두고 excute안에 string으로        
                


        rs = cursor.fetchall()
        mslist=list()
        descript = rs[1][3]
        for i in rs:
            #print(i[2])
            mslist.append(i[2]) # 2번자리는 변동없음, but sql문에 op_no와 bit가 입력변수로 들어가야함 %s형식, 익산것 참조
            # status_bit 별로 추가 

        aa=pd.DataFrame(mslist)
        mean=aa.mean()
        std=aa.std()

            # 아래부터 NG여부 판단
        cursor = conn.cursor()  
        cursor.execute(''' SELECT TOP (1) [MCH_STATUS_SUMMARY].[OP_NO],
                MCH_STATUS_SUMMARY.STATUS_BIT,DATEDIFF([MS],[STATUS_SDATE],
                [STATUS_EDATE]) as mstime ,STD_MCH_STATUS_INFO.STATUS_DESC 
                FROM [CETA_LMS].[dbo].[MCH_STATUS_SUMMARY] left outer join CETA_LMS.dbo.STD_MCH_STATUS_INFO 
                on MCH_STATUS_SUMMARY.STATUS_BIT = STD_MCH_STATUS_INFO.STATUS_IO_NO and MCH_STATUS_SUMMARY.OP_NO =STD_MCH_STATUS_INFO.OP_NO
                where MCH_STATUS_SUMMARY.STATUS_BIT= ('%s') and MCH_STATUS_SUMMARY.OP_NO=('%s'); '''  %(STATUS_BIT,OP_NO) )
        newdata= cursor.fetchone() #op,bit,time(ms)
        z_score=float((newdata[2]-mean)/std)
        cursor.close()
        if (z_score > 1):
            result=[OP_NO,STATUS_BIT,'NG']
        elif(z_score < -1):
            result=[OP_NO,STATUS_BIT,'NG']
        else:
            result=[OP_NO,STATUS_BIT,'OK']
        print(result) # chk point2

        LINE_group["LINE"] = "CETA31"
        if result[0]=="10":
            STATUS_BIT_group_OP10[result[1]]=result[2]
        elif result[0]=="20":
            STATUS_BIT_group_OP20[result[1]]=result[2]
        elif result[0]=="30":
            STATUS_BIT_group_OP30[result[1]]=result[2]
        elif result[0]=="40":
            STATUS_BIT_group_OP40[result[1]]=result[2]
        elif result[0]=="50":
            STATUS_BIT_group_OP50[result[1]]=result[2]    
        else:
            print("error!!! check OP_NO") 

        OP_group["10"]=STATUS_BIT_group_OP10
        OP_group["20"]=STATUS_BIT_group_OP20
        OP_group["30"]=STATUS_BIT_group_OP30
        OP_group["40"]=STATUS_BIT_group_OP40
        OP_group["50"]=STATUS_BIT_group_OP50
        LINE_group["OP_group"]=OP_group
        # print(json.dumps(LINE_group, ensure_ascii=False, indent="\t") )
                
        return LINE_group

    except:
        # print('nodata')
        result=[OP_NO,STATUS_BIT,'nodata']
     
        LINE_group["LINE"] = "CETA31"
        if result[0]=="10":
            STATUS_BIT_group_OP10[result[1]]=result[2]
        elif result[0]=="20":
            STATUS_BIT_group_OP20[result[1]]=result[2]
        elif result[0]=="30":
            STATUS_BIT_group_OP30[result[1]]=result[2]
        elif result[0]=="40":
            STATUS_BIT_group_OP40[result[1]]=result[2]
        elif result[0]=="50":
            STATUS_BIT_group_OP50[result[1]]=result[2]    
        else:
            print("error!!! check OP_NO") 

        OP_group["10"]=STATUS_BIT_group_OP10
        OP_group["20"]=STATUS_BIT_group_OP20
        OP_group["30"]=STATUS_BIT_group_OP30
        OP_group["40"]=STATUS_BIT_group_OP40
        OP_group["50"]=STATUS_BIT_group_OP50
        LINE_group["OP_group"]=OP_group
        # print(json.dumps(LINE_group, ensure_ascii=False, indent="\t") )
                
        return LINE_group


# In[ ]:


#예외 처리
def abort_if_OP_exist(OP_group):
    if OP_group not in LINE_group:
        abort(404, message="OP_group {} doesn't exist".format(OP_group))

def abort_if_actu_exist(act):
    if act not in OP_group:
        abort(404, message="equipment {} doesn't exist".format(act))

parser = reqparse.RequestParser()
parser.add_argument('task')


# Get, Delete, Put 정의


class actuater(Resource):
    def get(self,OP_group,OP_NO,STATUS_BIT):
        CalActuater(OP_NO,STATUS_BIT)
        return LINE_group[OP_group][OP_NO][STATUS_BIT]

class mch(Resource):
    def get(self,OP_group,OP_NO):
        abort_if_actu_exist(OP_NO)
        return LINE_group[OP_group][OP_NO]

class operation(Resource):
    def get(self, OP_group):
        abort_if_OP_exist(OP_group)
        return LINE_group[OP_group]


# Get, POST 정의
class line(Resource):
    def get(self):
        return LINE_group

    def post(self):
        args = parser.parse_args()
        OP_group = 'line%d' % (len(LINE_group) + 1)
        LINE_group[OP_group] = {'task': args['task']}
        return LINE_group[OP_group], 201

##
## URL Router에 맵핑한다.(Rest URL정의)
##

api.add_resource(line, '/CETA31/')
api.add_resource(operation, '/CETA31/<string:OP_group>/')
api.add_resource(mch, '/CETA31/<string:OP_group>/<string:OP_NO>/')
api.add_resource(actuater, '/CETA31/<string:OP_group>/<string:OP_NO>/<string:STATUS_BIT>/')


if __name__ == '__main__':
    app.run(debug=True)

