# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import math, re, sys, calendar, os, copy, time
import pandas as pd
import numpy as np
from datetime import datetime, date

ENCODING = 'utf-8-sig'
data_path = './output/'
out_path = './output/'
NAME = 'QNIA_'
NAME1 = ''
NAME2 = 'A'

def ERROR(error_text):
    print('\n\n= ! = '+error_text+'\n\n')
    with open('./ERROR.log','w', encoding=ENCODING) as f:    #用with一次性完成open、close檔案
        f.write(error_text)
    sys.exit()
def readExcelFile(dir, default=pd.DataFrame(), acceptNoFile=True, \
             header_=None,skiprows_=None,index_col_=None,sheet_name_=None):
    try:
        t = pd.read_excel(dir, header=header_,skiprows=skiprows_,index_col=index_col_,sheet_name=sheet_name_)
        #print(t)
        return t
    except FileNotFoundError:
        if acceptNoFile:
            return default
        else:
            ERROR('找不到檔案：'+dir)
    except:
        try: #檔案編碼格式不同
            t = pd.read_excel(dir, header=header_,skiprows=skiprows_,index_col=index_col_,sheet_name=sheet_name_)
            #print(t)
            return t
        except:
            return default  #有檔案但是讀不了:多半是沒有限制式，使skiprow後為空。 一律用預設值

#def CONCATE(df_key, DB_A, DB_Q, DB_M, DB_name_A, DB_name_Q, DB_name_M):
"""    
DB_TABLE = 'DB_'
DB_CODE = 'data'
this_year = datetime.now().year + 1
Year_list = [tmp for tmp in range(1947,this_year)]
Quarter_list = []
for q in range(1947,this_year):
    for r in range(1,5):
        Quarter_list.append(str(q)+'-Q'+str(r))
Month_list = []
for y in range(1947,this_year):
    for m in range(1,13):
        Month_list.append(str(y)+'-'+str(m).rjust(2,'0'))
"""
tStart = time.time()
print('Reading file: '+NAME+'key'+NAME1+', Time: ', int(time.time() - tStart),'s'+'\n')
QNIA_key = readExcelFile(data_path+NAME+'key'+NAME1+'.xlsx', header_ = 0, acceptNoFile=False, index_col_=0, sheet_name_=NAME+'key')
print('Reading file: '+NAME+NAME2+', Time: ', int(time.time() - tStart),'s'+'\n')
QNIA_t = readExcelFile(data_path+NAME+NAME2+'.xlsx', header_ = 0, acceptNoFile=False, index_col_=0, sheet_name_=NAME+NAME2)

not_found = []
print('Renaming the key file, Time: ', int(time.time() - tStart),'s'+'\n')
for key in range(QNIA_key.shape[0]):
    sys.stdout.write("\rLoading...("+str(round((key+1)*100/QNIA_key.shape[0], 1))+"%)*")
    sys.stdout.flush()
    name1 = str(QNIA_key.loc[key, 'name'])[:4]
    found = False
    for code in range(QNIA_t.shape[0]):
        name2 = str(QNIA_t.loc[code, 'code'])[:4]
        if name1 == name2:
            des = str(QNIA_t.loc[code, 'description'])
            if str(QNIA_key.loc[key, 'desc_e']).find(des) >= 0:
                QNIA_key.loc[key, 'name'] = QNIA_t.loc[code, 'code']
                found = True
                break
            else:
                continue
        else:
            continue
    if found == False:
        not_found.append(name1)
sys.stdout.write("\n\n")

print('Time: ', int(time.time() - tStart),'s'+'\n')

print(not_found)
print('Name not found:', len(not_found))
QNIA_key.to_excel(out_path+NAME+"key_rename.xlsx", sheet_name=NAME+'key_rename')

print('Time: ', int(time.time() - tStart),'s'+'\n')