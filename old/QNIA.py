# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import math, re, sys, calendar, os, copy, time
import pandas as pd
import numpy as np
from datetime import datetime, date
from QNIA_concat import CONCATE, readExcelFile

ENCODING = 'utf-8-sig'

NAME = 'QNIA_'
data_path = './data/'
out_path = "./output/"
databank = 'QNIA'
#freq = 'A'
key_list = ['databank', 'name', 'db_table', 'db_code', 'desc_e', 'desc_c', 'freq', 'start', 'unit', 'name_ord', 'snl', 'book', 'form_e', 'form_c']
merge_file = readExcelFile(out_path+'QNIA_key.xlsx', header_ = 0, sheet_name_='QNIA_key')
start_file = 1
last_file = 1
for i in range(len(key_list)):
    if key_list[i] == 'snl':
        snl_pos = i
        break

# 回報錯誤、儲存錯誤檔案並結束程式
def ERROR(error_text):
    print('\n\n= ! = '+error_text+'\n\n')
    with open('./ERROR.log','w', encoding=ENCODING) as f:    #用with一次性完成open、close檔案
        f.write(error_text)
    sys.exit()

def readFile(dir, default=pd.DataFrame(), acceptNoFile=False, \
             header_=None,skiprows_=None,index_col_=None,encoding_=ENCODING):
    try:
        t = pd.read_csv(dir, header=header_,skiprows=skiprows_,index_col=index_col_,\
                        encoding=encoding_,engine='python')
        #print(t)
        return t
    except FileNotFoundError:
        if acceptNoFile:
            return default
        else:
            ERROR('找不到檔案：'+dir)
    except:
        try: #檔案編碼格式不同
            t = pd.read_csv(dir, header=header_,skiprows=skiprows_,index_col=index_col_,\
                        engine='python')
            #print(t)
            return t
        except:
            return default  #有檔案但是讀不了:多半是沒有限制式，使skiprow後為空。 一律用預設值

def takeFirst(alist):
	return alist[0]

def COUNTRY_CODE(location):
    country_list={'ARG':213,'AUS':193,'AUT':122,'BEL':124,'BGR':918,'BRA':223,'CAN':156,'CHL':228,'CHN':924, \
                'COL':233,'CRI':238,'CZE':935,'DNK':128,'EA19':719,'EST':939,'EU15':715,'EU27_2020':727, \
                'EU28':728,'FIN':172,'FRA':132,'G-20':920,'G-7':907,'DEU':134,'GRC':174,'HUN':944,'IDN':536, \
                'IND':534,'ISL':176,'IRL':178,'ISR':436,'ITA':136,'JPN':158,'KOR':542,'LVA':941,'LTU':946,'LUX':126, \
                'MEX':273,'NAFTA':121,'NZL':196,'NOR':142,'OECD':950,'OECDE':930,'OTF':990,'POL':964, \
                'PRT':182,'ROU':968,'RUS':922,'SAU':456,'SVK':936,'SVN':961,'ESP':184,'SWE':144,'CHE':146,'NLD':138, \
                'TUR':186,"IKR":926,'GBR':112,'USA':111,"DEW":134,'ZAF':199}
    if location in country_list:
        return country_list[location]
    else:
        ERROR('國家代碼錯誤: '+location)

this_year = datetime.now().year + 1
Year_list = [tmp for tmp in range(1947,this_year)]
Quarter_list = []
for q in range(1947,this_year):
    for r in range(1,5):
        Quarter_list.append(str(q)+'-Q'+str(r))
#print(Quarter_list)
nY = len(Year_list)
nQ = len(Quarter_list)
KEY_DATA = []
SORT_DATA_A = []
SORT_DATA_Q = []
DATA_BASE_A = {}
DATA_BASE_Q = {}
db_table_A_t = pd.DataFrame(index = Year_list, columns = [])
db_table_Q_t = pd.DataFrame(index = Quarter_list, columns = [])
DB_name_A = []
DB_name_Q = []
DB_TABLE = 'DB_'
DB_CODE = 'data'

if merge_file.empty == False:
    snl = int(merge_file['snl'][merge_file.shape[0]-1]+1)
    for a in range(1,10000):
        if DB_TABLE+'A_'+str(a).rjust(4,'0') not in list(merge_file['db_table']):
            table_num_A = a-1
            code_t = []
            for c in range(merge_file.shape[0]):
                if merge_file['db_table'][c] == DB_TABLE+'A_'+str(a-1).rjust(4,'0'):
                    code_t.append(merge_file['db_code'][c])
            for code in range(1,200):
                if max(code_t) == DB_CODE+str(code).rjust(3,'0'):
                    code_num_A = code+1
                    break
            break
    for q in range(1,10000):
        if DB_TABLE+'Q_'+str(q).rjust(4,'0') not in list(merge_file['db_table']):
            table_num_Q = q-1
            code_t = []
            for c in range(merge_file.shape[0]):
                if merge_file['db_table'][c] == DB_TABLE+'Q_'+str(q-1).rjust(4,'0'):
                    code_t.append(merge_file['db_code'][c])
            for code in range(1,200):
                if max(code_t) == DB_CODE+str(code).rjust(3,'0'):
                    code_num_Q = code+1
                    break
            break
else:
    table_num_A = 1
    table_num_Q = 1
    code_num_A = 1
    code_num_Q = 1
    snl = 1
if code_num_A == 200:
    code_num_A = 1
if code_num_Q == 200:
    code_num_Q = 1
start_snl = snl
start_table_A = table_num_A
start_table_Q = table_num_Q
start_code_A = code_num_A
start_code_Q = code_num_Q

#print(QNIA_t.head(10))

#for i in range(10):
#    print(QNIA_t['TIME'][i], QNIA_t['Value'][i])
tStart = time.time()

for g in range(start_file,last_file+1):
    print('Reading file: '+NAME+str(g)+' Time: ', int(time.time() - tStart),'s'+'\n')
    QNIA_t = readFile(data_path+NAME+str(g)+'.csv', header_ = 0)
    nG = QNIA_t.shape[0]
    
    for i in range(nG):
        sys.stdout.write("\rLoading...("+str(round(i*100/nG, 1))+"%)*")
        sys.stdout.flush()
        
        if i==0:
            if QNIA_t['FREQUENCY'][i] == 'A':
                if code_num_A >= 200:
                    DATA_BASE_A[db_table_A] = db_table_A_t
                    DB_name_A.append(db_table_A)
                    table_num_A += 1
                    code_num_A = 1
                    db_table_A_t = pd.DataFrame(index = Year_list, columns = [])
                
                name = str(QNIA_t['FREQUENCY'][i])+str(COUNTRY_CODE(QNIA_t['LOCATION'][i]))+str(QNIA_t['SUBJECT'][i])+'__'+str(QNIA_t['MEASURE'][i])+'.a'
            
                value = QNIA_t['Value'][i]
                db_table_A = DB_TABLE+'A_'+str(table_num_A).rjust(4,'0')
                db_code_A = DB_CODE+str(code_num_A).rjust(3,'0')
                db_table_A_t[db_code_A] = ['' for tmp in range(nY)]
                for j in range(nY):
                    if db_table_A_t.index[j] == int(QNIA_t['TIME'][i]):
                        db_table_A_t[db_code_A][db_table_A_t.index[j]] = value
                        break
            
                desc_e = str(QNIA_t['Subject'][i]) + ', '+str(QNIA_t['Measure'][i]) + ', ' + str(QNIA_t['PowerCode'][i]) + ' of ' + str(QNIA_t['Unit'][i])
                form_e = str(QNIA_t['Subject'][i])
                
                desc_c = 'from_csv'
                freq = QNIA_t['FREQUENCY'][i]
                start = int(QNIA_t['TIME'][i])
                unit = str(QNIA_t['PowerCode'][i]) + ' of ' + str(QNIA_t['Unit'][i])
                name_ord = QNIA_t['LOCATION'][i]
                book = QNIA_t['Country'][i]
                #form_c = QNIA_t['Reference Period'][i]
                if str(QNIA_t['Reference Period'][i]) != 'nan' and str(QNIA_t['Reference Period'][i]).find('-') < 0:
                    form_c = int(QNIA_t['Reference Period'][i])
                else:
                    form_c = QNIA_t['Reference Period'][i]
                #flags = QNIA_t['Flags'][i]
                key_tmp= [databank, name, db_table_A, db_code_A, desc_e, desc_c, freq, start, unit, name_ord, snl, book, form_e, form_c]
                KEY_DATA.append(key_tmp)
                sort_tmp_A = [name, snl, db_table_A, db_code_A]
                SORT_DATA_A.append(sort_tmp_A)
                snl += 1

                code_num_A += 1
            elif QNIA_t['FREQUENCY'][i] == 'Q':
                if code_num_Q >= 200:
                    DATA_BASE_Q[db_table_Q] = db_table_Q_t
                    DB_name_Q.append(db_table_Q)
                    table_num_Q += 1
                    code_num_Q = 1
                    db_table_Q_t = pd.DataFrame(index = Quarter_list, columns = [])
                
                name = str(QNIA_t['FREQUENCY'][i])+str(COUNTRY_CODE(QNIA_t['LOCATION'][i]))+str(QNIA_t['SUBJECT'][i])+'__'+str(QNIA_t['MEASURE'][i])+'.q'
            
                value = QNIA_t['Value'][i]
                db_table_Q = DB_TABLE+'Q_'+str(table_num_Q).rjust(4,'0')
                db_code_Q = DB_CODE+str(code_num_Q).rjust(3,'0')
                db_table_Q_t[db_code_Q] = ['' for tmp in range(nQ)]
                for j in range(nQ):
                    if db_table_Q_t.index[j] == QNIA_t['TIME'][i]:
                        db_table_Q_t[db_code_Q][db_table_Q_t.index[j]] = value
                        break
            
                desc_e = str(QNIA_t['Subject'][i]) + ', '+str(QNIA_t['Measure'][i]) + ', ' + str(QNIA_t['PowerCode'][i]) + ' of ' + str(QNIA_t['Unit'][i])
                form_e = str(QNIA_t['Subject'][i])
                 
                desc_c = 'from_csv'
                freq = QNIA_t['FREQUENCY'][i]
                start = QNIA_t['TIME'][i]
                unit = str(QNIA_t['PowerCode'][i]) + ' of ' + str(QNIA_t['Unit'][i])
                name_ord = QNIA_t['LOCATION'][i]
                book = QNIA_t['Country'][i]
                #form_c = QNIA_t['Reference Period'][i]
                if str(QNIA_t['Reference Period'][i]) != 'nan' and str(QNIA_t['Reference Period'][i]).find('-') < 0:
                    form_c = int(QNIA_t['Reference Period'][i])
                else:
                    form_c = QNIA_t['Reference Period'][i]
                #flags = QNIA_t['Flags'][i]
                key_tmp= [databank, name, db_table_Q, db_code_Q, desc_e, desc_c, freq, start, unit, name_ord, snl, book, form_e, form_c]
                KEY_DATA.append(key_tmp)
                sort_tmp_Q = [name, snl, db_table_Q, db_code_Q]
                SORT_DATA_Q.append(sort_tmp_Q)
                snl += 1

                code_num_Q += 1
        else:
            if QNIA_t['LOCATION'][i] == QNIA_t['LOCATION'][i-1] and QNIA_t['SUBJECT'][i] == QNIA_t['SUBJECT'][i-1] and QNIA_t['MEASURE'][i] == QNIA_t['MEASURE'][i-1] and QNIA_t['FREQUENCY'][i] == QNIA_t['FREQUENCY'][i-1]:
                value = QNIA_t['Value'][i]
                if QNIA_t['FREQUENCY'][i] == 'A':
                    for j in range(nY):
                        if db_table_A_t.index[j] == int(QNIA_t['TIME'][i]):
                            db_table_A_t[db_code_A][db_table_A_t.index[j]] = value
                            break
                elif QNIA_t['FREQUENCY'][i] == 'Q':
                    for j in range(nQ):
                        if db_table_Q_t.index[j] == QNIA_t['TIME'][i]:
                            db_table_Q_t[db_code_Q][db_table_Q_t.index[j]] = value
                            break
                continue
            else:
                if QNIA_t['FREQUENCY'][i] == 'A':
                    if code_num_A >= 200:
                        DATA_BASE_A[db_table_A] = db_table_A_t
                        DB_name_A.append(db_table_A)
                        table_num_A += 1
                        code_num_A = 1
                        db_table_A_t = pd.DataFrame(index = Year_list, columns = [])
                
                    name = str(QNIA_t['FREQUENCY'][i])+str(COUNTRY_CODE(QNIA_t['LOCATION'][i]))+str(QNIA_t['SUBJECT'][i])+'__'+str(QNIA_t['MEASURE'][i])+'.a'
                
                    value = QNIA_t['Value'][i]
                    db_table_A = DB_TABLE+'A_'+str(table_num_A).rjust(4,'0')
                    db_code_A = DB_CODE+str(code_num_A).rjust(3,'0')
                    db_table_A_t[db_code_A] = ['' for tmp in range(nY)]
                    for j in range(nY):
                        if db_table_A_t.index[j] == int(QNIA_t['TIME'][i]):
                            db_table_A_t[db_code_A][db_table_A_t.index[j]] = value
                            break
                    
                    desc_e = str(QNIA_t['Subject'][i]) + ', '+str(QNIA_t['Measure'][i]) + ', ' + str(QNIA_t['PowerCode'][i]) + ' of ' + str(QNIA_t['Unit'][i])
                    form_e = str(QNIA_t['Subject'][i])
                    
                    desc_c = 'from_csv'
                    freq = QNIA_t['FREQUENCY'][i]
                    start = int(QNIA_t['TIME'][i])
                    unit = str(QNIA_t['PowerCode'][i]) + ' of ' + str(QNIA_t['Unit'][i])
                    name_ord = QNIA_t['LOCATION'][i]
                    book = QNIA_t['Country'][i]
                    #form_c = QNIA_t['Reference Period'][i]
                    if str(QNIA_t['Reference Period'][i]) != 'nan' and str(QNIA_t['Reference Period'][i]).find('-') < 0:
                        form_c = int(QNIA_t['Reference Period'][i])
                    else:
                        form_c = QNIA_t['Reference Period'][i]
                    #flags = QNIA_t['Flags'][i]
                    key_tmp= [databank, name, db_table_A, db_code_A, desc_e, desc_c, freq, start, unit, name_ord, snl, book, form_e, form_c]
                    KEY_DATA.append(key_tmp)
                    sort_tmp_A = [name, snl, db_table_A, db_code_A]
                    SORT_DATA_A.append(sort_tmp_A)
                    snl += 1

                    code_num_A += 1
                elif QNIA_t['FREQUENCY'][i] == 'Q':
                    if code_num_Q >= 200:
                        DATA_BASE_Q[db_table_Q] = db_table_Q_t
                        DB_name_Q.append(db_table_Q)
                        table_num_Q += 1
                        code_num_Q = 1
                        db_table_Q_t = pd.DataFrame(index = Quarter_list, columns = [])
                
                    name = str(QNIA_t['FREQUENCY'][i])+str(COUNTRY_CODE(QNIA_t['LOCATION'][i]))+str(QNIA_t['SUBJECT'][i])+'__'+str(QNIA_t['MEASURE'][i])+'.q'
                
                    value = QNIA_t['Value'][i]
                    db_table_Q = DB_TABLE+'Q_'+str(table_num_Q).rjust(4,'0')
                    db_code_Q = DB_CODE+str(code_num_Q).rjust(3,'0')
                    db_table_Q_t[db_code_Q] = ['' for tmp in range(nQ)]
                    for j in range(nQ):
                        if db_table_Q_t.index[j] == QNIA_t['TIME'][i]:
                            db_table_Q_t[db_code_Q][db_table_Q_t.index[j]] = value
                            break
                    
                    desc_e = str(QNIA_t['Subject'][i]) + ', '+str(QNIA_t['Measure'][i]) + ', ' + str(QNIA_t['PowerCode'][i]) + ' of ' + str(QNIA_t['Unit'][i])
                    form_e = str(QNIA_t['Subject'][i])
                     
                    desc_c = 'from_csv'
                    freq = QNIA_t['FREQUENCY'][i]
                    start = QNIA_t['TIME'][i]
                    unit = str(QNIA_t['PowerCode'][i]) + ' of ' + str(QNIA_t['Unit'][i])
                    name_ord = QNIA_t['LOCATION'][i]
                    book = QNIA_t['Country'][i]
                    #form_c = QNIA_t['Reference Period'][i]
                    if str(QNIA_t['Reference Period'][i]) != 'nan' and str(QNIA_t['Reference Period'][i]).find('-') < 0:
                        form_c = int(QNIA_t['Reference Period'][i])
                    else:
                        form_c = QNIA_t['Reference Period'][i]
                    #flags = QNIA_t['Flags'][i]
                    key_tmp= [databank, name, db_table_Q, db_code_Q, desc_e, desc_c, freq, start, unit, name_ord, snl, book, form_e, form_c]
                    KEY_DATA.append(key_tmp)
                    sort_tmp_Q = [name, snl, db_table_Q, db_code_Q]
                    SORT_DATA_Q.append(sort_tmp_Q)
                    snl += 1

                    code_num_Q += 1
    
    if g == last_file:
        if db_table_A_t.empty == False:
            DATA_BASE_A[db_table_A] = db_table_A_t
            DB_name_A.append(db_table_A)
        if db_table_Q_t.empty == False:
            DATA_BASE_Q[db_table_Q] = db_table_Q_t
            DB_name_Q.append(db_table_Q)
    
    sys.stdout.write("\n")        

print('Time: ', int(time.time() - tStart),'s'+'\n')    
SORT_DATA_A.sort(key=takeFirst)
repeated_A = 0
for i in range(1, len(SORT_DATA_A)):
    if SORT_DATA_A[i][0] == SORT_DATA_A[i-1][0]:
        repeated_A += 1
        #print(SORT_DATA_A[i][0],' ',SORT_DATA_A[i-1][1],' ',SORT_DATA_A[i][1],' ',SORT_DATA_A[i][2],' ',SORT_DATA_A[i][3])
        for key in KEY_DATA:
            if key[snl_pos] == SORT_DATA_A[i][1]:
                #print(key)
                KEY_DATA.remove(key) 
                break
        DATA_BASE_A[SORT_DATA_A[i][2]] = DATA_BASE_A[SORT_DATA_A[i][2]].drop(columns = SORT_DATA_A[i][3])
        if DATA_BASE_A[SORT_DATA_A[i][2]].empty == True:
            DB_name_A.remove(SORT_DATA_A[i][2])
    sys.stdout.write("\r"+str(repeated_A)+" repeated annual data key(s) found")
    sys.stdout.flush()
sys.stdout.write("\n")

print('Time: ', int(time.time() - tStart),'s'+'\n')    
SORT_DATA_Q.sort(key=takeFirst)
repeated_Q = 0
for i in range(1, len(SORT_DATA_Q)):
    if SORT_DATA_Q[i][0] == SORT_DATA_Q[i-1][0]:
        repeated_Q += 1
        #print(SORT_DATA_Q[i][0],' ',SORT_DATA_Q[i-1][1],' ',SORT_DATA_Q[i][1],' ',SORT_DATA_Q[i][2],' ',SORT_DATA_Q[i][3])
        for key in KEY_DATA:
            if key[snl_pos] == SORT_DATA_Q[i][1]:
                #print(key)
                KEY_DATA.remove(key) 
                break
        DATA_BASE_Q[SORT_DATA_Q[i][2]] = DATA_BASE_Q[SORT_DATA_Q[i][2]].drop(columns = SORT_DATA_Q[i][3])
        if DATA_BASE_Q[SORT_DATA_Q[i][2]].empty == True:
            DB_name_Q.remove(SORT_DATA_Q[i][2])
    sys.stdout.write("\r"+str(repeated_Q)+" repeated quarter data key(s) found")
    sys.stdout.flush()
sys.stdout.write("\n")

print('Time: ', int(time.time() - tStart),'s'+'\n')
df_key = pd.DataFrame(KEY_DATA, columns = key_list)
df_key = df_key.sort_values(by=['name', 'db_table'], ignore_index=True)
if df_key.iloc[0]['snl'] != start_snl:
    df_key.loc[0, 'snl'] = start_snl
for s in range(1,df_key.shape[0]):
    sys.stdout.write("\rSetting new snls: "+str(s))
    sys.stdout.flush()
    df_key.loc[s, 'snl'] = df_key.loc[0, 'snl'] + s
sys.stdout.write("\n")
#if repeated_A > 0 or repeated_Q > 0:
print('Setting new files, Time: ', int(time.time() - tStart),'s'+'\n')

DATA_BASE_A_new = {}
DATA_BASE_Q_new = {}
db_table_A_t = pd.DataFrame(index = Year_list, columns = [])
db_table_Q_t = pd.DataFrame(index = Quarter_list, columns = [])
DB_name_A_new = []
DB_name_Q_new = []
db_table_new = 0
db_code_new = 0
for f in range(df_key.shape[0]):
    sys.stdout.write("\rSetting new keys: "+str(db_table_new)+" "+str(db_code_new))
    sys.stdout.flush()
    if df_key.iloc[f]['freq'] == 'A':
        if start_code_A >= 200:
            DATA_BASE_A_new[db_table_A] = db_table_A_t
            DB_name_A_new.append(db_table_A)
            start_table_A += 1
            start_code_A = 1
            db_table_A_t = pd.DataFrame(index = Year_list, columns = [])
        db_table_A = DB_TABLE+'A_'+str(start_table_A).rjust(4,'0')
        db_code_A = DB_CODE+str(start_code_A).rjust(3,'0')
        db_table_A_t[db_code_A] = DATA_BASE_A[df_key.iloc[f]['db_table']][df_key.iloc[f]['db_code']]
        df_key.loc[f, 'db_table'] = db_table_A
        df_key.loc[f, 'db_code'] = db_code_A
        start_code_A += 1
        db_table_new = db_table_A
        db_code_new = db_code_A
    elif df_key.iloc[f]['freq'] == 'Q':
        if start_code_Q >= 200:
            DATA_BASE_Q_new[db_table_Q] = db_table_Q_t
            DB_name_Q_new.append(db_table_Q)
            start_table_Q += 1
            start_code_Q = 1
            db_table_Q_t = pd.DataFrame(index = Quarter_list, columns = [])
        db_table_Q = DB_TABLE+'Q_'+str(start_table_Q).rjust(4,'0')
        db_code_Q = DB_CODE+str(start_code_Q).rjust(3,'0')
        db_table_Q_t[db_code_Q] = DATA_BASE_Q[df_key.iloc[f]['db_table']][df_key.iloc[f]['db_code']]
        df_key.loc[f, 'db_table'] = db_table_Q
        df_key.loc[f, 'db_code'] = db_code_Q
        start_code_Q += 1
        db_table_new = db_table_Q
        db_code_new = db_code_Q
    
    if f == df_key.shape[0]-1:
        if db_table_A_t.empty == False:
            DATA_BASE_A_new[db_table_A] = db_table_A_t
            DB_name_A_new.append(db_table_A)
        if db_table_Q_t.empty == False:
            DATA_BASE_Q_new[db_table_Q] = db_table_Q_t
            DB_name_Q_new.append(db_table_Q)
sys.stdout.write("\n")
DATA_BASE_A = DATA_BASE_A_new
DATA_BASE_Q = DATA_BASE_Q_new
DB_name_A = DB_name_A_new
DB_name_Q = DB_name_Q_new

print(df_key)
#print(DATA_BASE_t)

print('Time: ', int(time.time() - tStart),'s'+'\n')
if merge_file.empty == False:
    df_key, DATA_BASE = CONCATE(df_key, DATA_BASE_A, DATA_BASE_Q, DB_name_A, DB_name_Q)
    df_key.to_excel(out_path+NAME+"key.xlsx", sheet_name=NAME+'key')
    with pd.ExcelWriter(out_path+NAME+"database.xlsx") as writer: # pylint: disable=abstract-class-instantiated
        endl = True
        for key in sorted(DATA_BASE.keys()):
            if key.find('DB_A') >= 0:
                sys.stdout.write("\rOutputing sheet: "+str(key))
                sys.stdout.flush()
            elif key.find('DB_Q') >= 0:
                if endl == True:
                    sys.stdout.write("\n")
                    endl = False
                sys.stdout.write("\rOutputing sheet: "+str(key))
                sys.stdout.flush()
            DATA_BASE[key].to_excel(writer, sheet_name = key)
    sys.stdout.write("\n")
else:
    df_key.to_excel(out_path+NAME+"key.xlsx", sheet_name=NAME+'key')
    with pd.ExcelWriter(out_path+NAME+"database.xlsx") as writer: # pylint: disable=abstract-class-instantiated
        for d in DB_name_A:
            sys.stdout.write("\rOutputing sheet: "+str(d))
            sys.stdout.flush()
            if DATA_BASE_A[d].empty == False:
                DATA_BASE_A[d].to_excel(writer, sheet_name = d)
        sys.stdout.write("\n")
        for d in DB_name_Q:
            sys.stdout.write("\rOutputing sheet: "+str(d))
            sys.stdout.flush()
            if DATA_BASE_Q[d].empty == False:
                DATA_BASE_Q[d].to_excel(writer, sheet_name = d)
    sys.stdout.write("\n")

print('Time: ', int(time.time() - tStart),'s'+'\n')