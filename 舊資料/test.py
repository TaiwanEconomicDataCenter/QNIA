# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import math, re, sys, calendar, os, copy, time
import pandas as pd
import numpy as np
from datetime import datetime, date

ENCODING = 'utf-8-sig'
out_path = './output/'
column = ['code', 'frequency', 'from', 'to', 'description', 'subject', 'by', 'unit', 'source', 'OECD_code', 'country']

"""
tStart = time.time()
print('Reading file: QNIA_key'+NAME1+', Time: ', int(time.time() - tStart),'s'+'\n')
KEY_DATA_t = readExcelFile(data_path+'QNIA_key'+NAME1+'.xlsx', header_ = 0, acceptNoFile=False, index_col_=0, sheet_name_='QNIA_key')
print('Reading file: QNIA_key'+NAME2+', Time: ', int(time.time() - tStart),'s'+'\n')
df_key = readExcelFile(data_path+'QNIA_key'+NAME2+'.xlsx', header_ = 0, acceptNoFile=False, index_col_=0, sheet_name_='QNIA_key')
#print('Reading file: MEI_database, Time: ', int(time.time() - tStart),'s'+'\n')
#DATA_BASE_t = readExcelFile(data_path+'MEI_database.xlsx', header_ = 0, index_col_=0, acceptNoFile=False)
"""
with open('./QNIA_A.txt','r',encoding='ANSI') as f:
    lines = f.readlines()
for l in range(len(lines)):
    lines[l] = lines[l].replace('\n','')
#print(lines)
#frequency = 'DAILY'

QNIA_A = []
g_t = []
code = ''
frequency = ''
fromt = ''
to = ''
des = ''
country = ''
subject = ''
by = ''
unit = ''
source = ''
OECD_code = ''
#note = ''
#last = ''
countS = 0
ignore = False
for l in range(len(lines)):
    #print(lines[l])
    sys.stdout.write("\rLoading...("+str(int((l+1)*100/len(lines)))+"%)*")
    sys.stdout.flush()
    if l+1 >= len(lines):
        QNIA_A.append(g_t)
        break
    if not lines[l] or lines[l] == ' ':
        if lines[l+1].find('SERIES') >= 0:
            if g_t != []:
                QNIA_A.append(g_t)
            g_t = []
            code = ''
            frequency = ''
            fromt = ''
            to = ''
            des = ''
            country = ''
            subject = ''
            by = ''
            unit = ''
            source = ''
            OECD_code = ''
            #note = ''
            loc7 = -1
            loc8 = loc7
            loc9 = loc7
            loc10 = loc7
            loc11 = loc7
            loc12 = loc7
            ignore = False
    elif ignore == True:
        continue
    elif lines[l].find('#') >= 0:
        continue
    else:
        if lines[l].find('SERIES') >= 0:
            countS+=1
            loc1 = lines[l].find(':')+1
            loc2 = lines[l].find(' ', loc1)
            code = lines[l][loc1:loc2]
            g_t.append(code)
        elif lines[l].find('Data for') >= 0:
            locf1 = lines[l].find('Data')-1
            frequency = lines[l][:locf1]
            g_t.append(frequency)
            loc3 = lines[l].find('from')+5
            loc4 = lines[l].find('to')-2
            loc5 = lines[l].find('to')+3
            loc6 = loc5+4
            fromt = lines[l][loc3:loc4]
            to = lines[l][loc5:loc6]
            if frequency == 'ANNUAL':
                #print(lines[l])
                try:
                    fromt = int(fromt)
                    to = int(to)
                except:
                    fromt = fromt
                    to = to
            g_t.append(fromt)
            g_t.append(to)
        else:
            d = lines[l]
            des = ''
            m = l
            while lines[m+1].find('SERIES') < 0 and lines[l].find('#') < 0:
                des = des+d+'/'
                m+=1
                d = lines[m]
                if m+1 >= len(lines):
                    break
            
            if des.replace('/','').find('SOURCE:') >= 0:
                loc7 = des.find('/')
                #loc8 = des.find('/',loc7)
                #loc9 = des.find('/',loc8)
                loc10 = des.replace('/','').find('MILLIONS')
                loc11 = des.replace('/','').find('SOURCE')
                loc12 = des.replace('/','').find(':',loc11)+1
                loc13 = des.replace('/','').find('.',loc11)-3
                country = des[:loc7].replace('/','').title()
                #subject = des[loc7+1:loc8].replace('/','')
                #by = des[loc8+1:loc9].replace('/','')
                unit = des.replace('/','')[loc10:loc11]
                source = des.replace('/','')[loc12:loc13]
                OECD_code = des.replace('/','')[loc13:]
                des = des[loc7:]
            elif des.replace('/','').find(' - ') >= 0:
                loc8 = des.find(',')
                #loc9 = loc8 + 2
                #loc10 = des.find(',',loc8)
                #loc11 = loc10 + 2
                #loc10 = des.find(',',loc10)
                loc7 = des.find('-', loc8)+2
                loc9 = des.find('-', loc8)-1
                country = des[loc7:].replace('/','').title()
                des = des[:loc9]
                #subject = des[:loc8]
                #currency = des[loc9:loc10]
            else:
                print(des)
            des = des.replace('/','')
            g_t.append(des)
            g_t.append(subject)
            g_t.append(by)
            g_t.append(unit)
            g_t.append(source)
            g_t.append(OECD_code)
            g_t.append(country)
            
            ignore = True
        #else:
        #    g_t.append(lines[l])
        
    #last = l
sys.stdout.write("\n\n")
#print(QNIA_A)
"""
for g in QNIA_A:
    if len(g) > 7:
        print(g)
""" 
print(countS)
ger = pd.DataFrame(QNIA_A, columns=column)
print(ger)
ger.to_excel(out_path+"QNIA_A.xlsx", sheet_name='QNIA_A')
