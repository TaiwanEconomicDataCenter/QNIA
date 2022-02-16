# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import math, re, sys, calendar, os, copy, time
import pandas as pd
import numpy as np
from datetime import datetime, date

ENCODING = 'utf-8-sig'
data_path = './output/'
NAME1 = ''
NAME2 = '_new'

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

tStart = time.time()
print('Reading file: QNIA_key'+NAME1+', Time: ', int(time.time() - tStart),'s'+'\n')
df_key1 = readExcelFile(data_path+'QNIA_key'+NAME1+'.xlsx', header_ = 0, acceptNoFile=False, index_col_=0, sheet_name_='QNIA_key')
df_key1.insert(loc=0, column='Label', value=['QNIA_key'+NAME1 for i in range(df_key1.shape[0])])
print('Reading file: QNIA_key'+NAME2+', Time: ', int(time.time() - tStart),'s'+'\n')
df_key2 = readExcelFile(data_path+'QNIA_key'+NAME2+'.xlsx', header_ = 0, acceptNoFile=False, index_col_=0, sheet_name_='QNIA_key')
df_key2.insert(loc=0, column='Label', value=['QNIA_key'+NAME2 for i in range(df_key2.shape[0])])
#print('Reading file: MEI_database, Time: ', int(time.time() - tStart),'s'+'\n')
#DATA_BASE_t = readExcelFile(data_path+'MEI_database.xlsx', header_ = 0, index_col_=0, acceptNoFile=False)

print('Concating file: QNIA_key'+NAME1+', Time: ', int(time.time() - tStart),'s'+'\n')
KEY_DATA_t = pd.concat([df_key1, df_key2], ignore_index=True)

print('Time: ', int(time.time() - tStart),'s'+'\n')
KEY_DATA_t = KEY_DATA_t.sort_values(by=['name', 'db_table'], ignore_index=True)
unrepeated = 0
earliest = str(date.today().year)
#unrepeated_index = []
for i in range(1, len(KEY_DATA_t)):
    if KEY_DATA_t['name'][i] != KEY_DATA_t['name'][i-1] and KEY_DATA_t['name'][i] != KEY_DATA_t['name'][i+1]:
        print(list(KEY_DATA_t.iloc[i]),'\n')
        if str(KEY_DATA_t.iloc[i]['start']) < earliest:
            earliest = str(KEY_DATA_t.iloc[i]['start'])[:4]
        unrepeated += 1
        #repeated_index.append(i)
        #print(KEY_DATA_t['name'][i],' ',KEY_DATA_t['name'][i-1])
        #key = KEY_DATA_t.iloc[i]
        #DATA_BASE_t[key['db_table']] = DATA_BASE_t[key['db_table']].drop(columns = key['db_code'])
        #unrepeated_index.append(i)
        
    #sys.stdout.write("\r"+str(repeated)+" repeated data key(s) found")
    #sys.stdout.flush()
#sys.stdout.write("\n")
print('unrepeated: ', unrepeated)
print('earliest year: ', earliest)
#for i in unrepeated_index:
    #sys.stdout.write("\rDropping repeated data key(s): "+str(i))
    #sys.stdout.flush()
    #KEY_DATA_t = KEY_DATA_t.drop([i])
#sys.stdout.write("\n")
