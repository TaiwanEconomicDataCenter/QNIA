# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import math, re, sys, calendar, os, copy, time, csv
import pandas as pd
import numpy as np
from datetime import datetime, date

ENCODING = 'utf-8-sig'
data_path = './output/'
out_path = './output/'
NAME = 'QNIA_'
specified_start_year = True
make_doc = True
part_file = False
from_year = '2019'
latest = True
to_year = '2020'
if specified_start_year == True:
    START_YEAR = '_'+str(datetime.now().year - 10)
else:
    START_YEAR = ''

def SPECIAL(special_text):
    print('\n= ! = '+special_text+'\n\n')
    #with open('./ERROR.log','w', encoding=ENCODING) as f:    #用with一次性完成open、close檔案
    #    f.write(special_text)
    sys.exit()
def readExcelFile(dir, default=pd.DataFrame(), acceptNoFile=False, \
             header_=None,skiprows_=None,index_col_=None,sheet_name_=None):
    try:
        t = pd.read_excel(dir,sheet_name=sheet_name_, header=header_,index_col=index_col_,skiprows=skiprows_)
        #print(t)
        return t
    except FileNotFoundError:
        if acceptNoFile:
            return default
        else:
            SPECIAL('Several files input')
    except:
        try: #檔案編碼格式不同
            t = pd.read_excel(dir, header=header_,skiprows=skiprows_,index_col=index_col_,sheet_name=sheet_name_)
            #print(t)
            return t
        except:
            return default  #有檔案但是讀不了:多半是沒有限制式，使skiprow後為空。 一律用預設值

def FREQUENCY(freq):
    if freq == 'D':
        return 'Daily'
    elif freq == 'W':
        return 'Weekly'
    elif freq == 'M':
        return 'Monthly'
    elif freq == 'Q':
        return 'Quarterly'
    elif freq == 'S':
        return 'Semiannual'
    elif freq == 'A':
        return 'Annual'

tStart = time.time()
print('Reading file: '+NAME+'key'+START_YEAR+', Time: ', int(time.time() - tStart),'s'+'\n')
df_key = readExcelFile(data_path+NAME+'key'+START_YEAR+'.xlsx', header_ = 0, acceptNoFile=False, index_col_=0, sheet_name_=NAME+'key')
try:
    print('Reading file: '+NAME+'database'+START_YEAR+', Time: ', int(time.time() - tStart),'s'+'\n')
    DATA_BASE_t = readExcelFile(data_path+NAME+'database'+START_YEAR+'.xlsx', header_ = 0, index_col_=0, acceptNoFile=False)
except:
    with open(data_path+'database_num.txt','r',encoding=ENCODING) as f:  #用with一次性完成open、close檔案
        database_num = int(f.read().replace('\n', ''))
    DATA_BASE_t = {}
    for i in range(1,database_num+1):
        print('Reading file: '+NAME+'database_'+str(i)+', Time: ', int(time.time() - tStart),'s'+'\n')
        DB_t = readExcelFile(data_path+NAME+'database_'+str(i)+'.xlsx', header_ = 0, index_col_=0, acceptNoFile=False, sheet_name_=None)
        for d in DB_t.keys():
            DATA_BASE_t[d] = DB_t[d]

#endyear = '1956'  
AREMOS = []
AREMOS_DATA = []
print('Outputing AREMOS files, Time: ', int(time.time() - tStart),'s'+'\n')
#while from_year >= endyear:
#AREMOS = []
#AREMOS_DATA = []
#print('From year',from_year,'to year',to_year)
for key in range(df_key.shape[0]):
    sys.stdout.write("\rLoading...("+str(round((key+1)*100/df_key.shape[0], 1))+"%)*")
    sys.stdout.flush()

    freq = df_key.loc[key,'freq']
    freq2 = freq
    if freq == 'A':
        freq2 = ''
    
    DATA = df_key.loc[key,'name']+'='
    nA = DATA_BASE_t[df_key.loc[key,'db_table']].shape[0]
    if DATA_BASE_t[df_key.loc[key,'db_table']].index[0] > DATA_BASE_t[df_key.loc[key,'db_table']].index[1]:
        array = reversed(range(nA))
    else:
        array = range(nA)
    
    if part_file == True:
        if from_year+'-01-01' <= df_key.loc[key,'last']:
            if latest == True:
                if df_key.loc[key,'start'] <= str(date.fromisoformat(df_key.loc[key,'last']).year)+'-01-01':
                    SERIES_DATA = 'SERIES<FREQ '+freq+' PER '+from_year+freq2+'001'+' TO '+str(date.fromisoformat(df_key.loc[key,'last']).year)+freq2+date.fromisoformat(df_key.loc[key,'last']).strftime('%j')+'>!'
                else:
                    continue
            else:
                if df_key.loc[key,'start'] <= to_year+'-01-01':
                    SERIES_DATA = 'SERIES<FREQ '+freq+' PER '+from_year+freq2+'001'+' TO '+to_year+freq2+'001'+'>!'
                else:
                    continue
            found = False
            for ar in array:
                if latest == True:
                    if DATA_BASE_t[df_key.loc[key,'db_table']].index[ar] >= from_year+'-01-01' and DATA_BASE_t[df_key.loc[key,'db_table']].index[ar] <= df_key.loc[key,'last']:
                        if found == True:
                            DATA = DATA + ',' 
                        if str(DATA_BASE_t[df_key.loc[key,'db_table']].loc[DATA_BASE_t[df_key.loc[key,'db_table']].index[ar], df_key.loc[key,'db_code']]) == 'nan' or\
                            str(DATA_BASE_t[df_key.loc[key,'db_table']].loc[DATA_BASE_t[df_key.loc[key,'db_table']].index[ar], df_key.loc[key,'db_code']]) == '':
                            DATA = DATA + 'M'
                        else:
                            if str(DATA_BASE_t[df_key.loc[key,'db_table']].loc[DATA_BASE_t[df_key.loc[key,'db_table']].index[ar], df_key.loc[key,'db_code']]).find('e-') >= 0:
                                loc1 = str(DATA_BASE_t[df_key.loc[key,'db_table']].loc[DATA_BASE_t[df_key.loc[key,'db_table']].index[ar], df_key.loc[key,'db_code']]).find('e-')
                                significand = str(DATA_BASE_t[df_key.loc[key,'db_table']].loc[DATA_BASE_t[df_key.loc[key,'db_table']].index[ar], df_key.loc[key,'db_code']])[:loc1]
                                power = int(str(DATA_BASE_t[df_key.loc[key,'db_table']].loc[DATA_BASE_t[df_key.loc[key,'db_table']].index[ar], df_key.loc[key,'db_code']])[-2:])
                                number = significand.replace('.','').rjust(len(significand)+power-2,'0')
                                number = '0.'+number
                                DATA = DATA + number
                            else:
                                DATA = DATA + str(DATA_BASE_t[df_key.loc[key,'db_table']].loc[DATA_BASE_t[df_key.loc[key,'db_table']].index[ar], df_key.loc[key,'db_code']])
                        found = True
                else:
                    if DATA_BASE_t[df_key.loc[key,'db_table']].index[ar] >= from_year+'-01-01' and DATA_BASE_t[df_key.loc[key,'db_table']].index[ar] <= to_year+'-01-01':
                        if found == True:
                            DATA = DATA + ',' 
                        if str(DATA_BASE_t[df_key.loc[key,'db_table']].loc[DATA_BASE_t[df_key.loc[key,'db_table']].index[ar], df_key.loc[key,'db_code']]) == 'nan' or\
                            str(DATA_BASE_t[df_key.loc[key,'db_table']].loc[DATA_BASE_t[df_key.loc[key,'db_table']].index[ar], df_key.loc[key,'db_code']]) == '':
                            DATA = DATA + 'M'
                        else:
                            if str(DATA_BASE_t[df_key.loc[key,'db_table']].loc[DATA_BASE_t[df_key.loc[key,'db_table']].index[ar], df_key.loc[key,'db_code']]).find('e-') >= 0:
                                loc1 = str(DATA_BASE_t[df_key.loc[key,'db_table']].loc[DATA_BASE_t[df_key.loc[key,'db_table']].index[ar], df_key.loc[key,'db_code']]).find('e-')
                                significand = str(DATA_BASE_t[df_key.loc[key,'db_table']].loc[DATA_BASE_t[df_key.loc[key,'db_table']].index[ar], df_key.loc[key,'db_code']])[:loc1]
                                power = int(str(DATA_BASE_t[df_key.loc[key,'db_table']].loc[DATA_BASE_t[df_key.loc[key,'db_table']].index[ar], df_key.loc[key,'db_code']])[-2:])
                                number = significand.replace('.','').rjust(len(significand)+power-2,'0')
                                number = '0.'+number
                                DATA = DATA + number
                            else:
                                DATA = DATA + str(DATA_BASE_t[df_key.loc[key,'db_table']].loc[DATA_BASE_t[df_key.loc[key,'db_table']].index[ar], df_key.loc[key,'db_code']])
                        found = True
        else:
            continue
    else:
        if freq == 'D':
            SERIES_DATA = 'SERIES<FREQ '+freq+' PER '+str(date.fromisoformat(df_key.loc[key,'start']).year)+freq2+date.fromisoformat(df_key.loc[key,'start']).strftime('%j')+\
                ' TO '+str(date.fromisoformat(df_key.loc[key,'last']).year)+freq2+date.fromisoformat(df_key.loc[key,'last']).strftime('%j')+'>!'
        elif freq == 'M':
            SERIES_DATA = 'SERIES<FREQ '+freq+' PER '+str(df_key.loc[key,'start'])[:4]+freq2+str(df_key.loc[key,'start'])[-2:]+\
                ' TO '+str(df_key.loc[key,'last'])[:4]+freq2+str(df_key.loc[key,'last'])[-2:]+'>!'
        elif freq == 'Q':
            SERIES_DATA = 'SERIES<FREQ '+freq+' PER '+str(df_key.loc[key,'start'])[:4]+freq2+str(df_key.loc[key,'start'])[-1:]+\
                ' TO '+str(df_key.loc[key,'last'])[:4]+freq2+str(df_key.loc[key,'last'])[-1:]+'>!'
        elif freq == 'A':
            SERIES_DATA = 'SERIES<FREQ '+freq+' PER '+str(df_key.loc[key,'start'])[:4]+freq2+\
                ' TO '+str(df_key.loc[key,'last'])[:4]+freq2+'>!'
        found = False
        for ar in array:
            if DATA_BASE_t[df_key.loc[key,'db_table']].index[ar] >= df_key.loc[key,'start'] and DATA_BASE_t[df_key.loc[key,'db_table']].index[ar] <= df_key.loc[key,'last']:
                if found == True:
                    DATA = DATA + ',' 
                if str(DATA_BASE_t[df_key.loc[key,'db_table']].loc[DATA_BASE_t[df_key.loc[key,'db_table']].index[ar], df_key.loc[key,'db_code']]) == 'nan' or\
                    str(DATA_BASE_t[df_key.loc[key,'db_table']].loc[DATA_BASE_t[df_key.loc[key,'db_table']].index[ar], df_key.loc[key,'db_code']]) == '':
                    DATA = DATA + 'M'
                else:
                    if str(DATA_BASE_t[df_key.loc[key,'db_table']].loc[DATA_BASE_t[df_key.loc[key,'db_table']].index[ar], df_key.loc[key,'db_code']]).find('e-') >= 0:
                        loc1 = str(DATA_BASE_t[df_key.loc[key,'db_table']].loc[DATA_BASE_t[df_key.loc[key,'db_table']].index[ar], df_key.loc[key,'db_code']]).find('e-')
                        significand = str(DATA_BASE_t[df_key.loc[key,'db_table']].loc[DATA_BASE_t[df_key.loc[key,'db_table']].index[ar], df_key.loc[key,'db_code']])[:loc1]
                        power = int(str(DATA_BASE_t[df_key.loc[key,'db_table']].loc[DATA_BASE_t[df_key.loc[key,'db_table']].index[ar], df_key.loc[key,'db_code']])[-2:])
                        number = significand.replace('.','').rjust(len(significand)+power-2,'0')
                        number = '0.'+number
                        DATA = DATA + number
                    else:
                        DATA = DATA + str(DATA_BASE_t[df_key.loc[key,'db_table']].loc[DATA_BASE_t[df_key.loc[key,'db_table']].index[ar], df_key.loc[key,'db_code']])
                found = True
    
    end = ';'
    DATA = DATA + end
    
    if make_doc == True:
        SERIES = 'SERIES<FREQ '+FREQUENCY(freq)+' >'+df_key.loc[key,'name']+'!'
        DESC = "'"+str(df_key.loc[key,'desc_e']).replace("'",'"')+' - '+str(df_key.loc[key,'book'])+"'"+'!'
        AREMOS.append(SERIES)
        AREMOS.append(DESC)
        AREMOS.append(end)
    AREMOS_DATA.append(SERIES_DATA)
    AREMOS_DATA.append(DATA)
sys.stdout.write("\n\n")

if make_doc == True:
    aremos = pd.DataFrame(AREMOS)
    aremos.to_csv(out_path+NAME+"doc"+START_YEAR+".txt", header=False, index=False, sep='|', quoting=csv.QUOTE_NONE, quotechar='')
aremos_data = pd.DataFrame(AREMOS_DATA)
aremos_data.to_csv(out_path+NAME+"data"+START_YEAR+".txt", header=False, index=False, sep='|', quoting=csv.QUOTE_NONE, quotechar='')
#aremos_data.to_csv(out_path+NAME+"data"+from_year[-2:]+".txt", header=False, index=False, sep='|', quoting=csv.QUOTE_NONE, quotechar='')

print('Time: ', int(time.time() - tStart),'s'+'\n')
#to_year = from_year
#from_year = str(int(from_year)-2)