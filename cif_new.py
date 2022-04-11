# COMPOSITE INDICATORS
# FUNCTIONS

import os
import requests as rq
from requests.adapters import HTTPAdapter
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import matplotlib as mpl
import statsmodels.tsa.x13 as smX13
import statsmodels.tsa.arima_model as smARIMA
#import statsmodels.tsa.statespace.sarimax as smSARIMAX
import statsmodels.tsa.filters.hp_filter as smHP
from dateutil.relativedelta import relativedelta
#from subprocess import call
#from pathlib import Path
#import numbers
import warnings
import zipfile


# OECD API FUNCTIONS

def makeOECDRequest(dsname, dimensions, params = None, root_dir = 'https://stats.oecd.org/SDMX-JSON/data'):
    
    """
    Make URL for the OECD API and return a response.
    
    Parameters
    -----
    dsname: str
        dataset identifier (e.g., MEI for main economic indicators)
    dimensions: list
        list of 4 dimensions (usually location, subject, measure, frequency)
    params: dict or None
        (optional) dictionary of additional parameters (e.g., startTime)
    root_dir: str
        default OECD API (https://data.oecd.org/api/sdmx-json-documentation/#d.en.330346)
        
    Returns
    -----
    results: requests.Response
        `Response <Response>` object
    
    """
    
    if not params:
        params = {}
    
    dim_args = ['+'.join(d) for d in dimensions]
    dim_str = '.'.join(dim_args)
    
    url = root_dir + '/' + dsname + '/' + dim_str + '/all'
    
    print('Requesting URL ' + url)
    s = rq.Session()
    s.mount('http://', HTTPAdapter(max_retries=10))
    s.mount('https://', HTTPAdapter(max_retries=10))
    return s.get(url = url, params = params, timeout=60)

    
def getOECDJSONStructure(dsname, root_dir = 'http://stats.oecd.org/SDMX-JSON/dataflow', showValues = [], returnValues = False):
    
    """
    Check structure of OECD dataset.
    
    Parameters
    -----
    dsname: str
        dataset identifier (e.g., MEI for main economic indicators)
    root_dir: str
        default OECD API structure uri
    showValues: list
        shows available values of specified variable, accepts list of integers
        which mark position of variable of interest (e.g. 0 for LOCATION)
    returnValues: bool
        if True, the observations are returned
        
    Returns
    -----
    results: list
        list of dictionaries with observations parsed from JSON object, if returnValues = True
        
    """ 
    
    url = root_dir + '/' + dsname + '/all'
    
    print('Requesting URL ' + url)
    
    response = rq.get(url = url)
    
    if (response.status_code == 200):
        
        responseJson = response.json()
        
        keyList = [item['id'] for item in responseJson.get('structure').get('dimensions').get('observation')]
        
        print('\nStructure: ' + ', '.join(keyList))
        
        for i in showValues:
            
            print('\n%s values:' % (keyList[i]))
            print('\n'.join([str(j) for j in responseJson.get('structure').get('dimensions').get('observation')[i].get('values')]))
            
        if returnValues:
        
            return(responseJson.get('structure').get('dimensions').get('observation'))
        
    else:
        
        print('\nError: %s' % response.status_code)
        

def createOneCountryDataFrameFromOECD(country = 'CZE', dsname = 'MEI', subject = [], measure = [], frequency = 'M', startDate = None, endDate = None):      
    
    """
    Request data from OECD API and return pandas DataFrame. This works with OECD datasets
    where the first dimension is location (check the structure with getOECDJSONStructure()
    function).
    
    Parameters
    -----
    country: str
        country code (max 1, use createDataFrameFromOECD() function to download data from more countries),
        list of OECD codes available at http://www.oecd-ilibrary.org/economics/oecd-style-guide/country-names-codes-and-currencies_9789264243439-8-en
    dsname: str
        dataset identifier (default MEI for main economic indicators)
    subject: list
        list of subjects, empty list for all
    measure: list
        list of measures, empty list for all
    frequency: str
        'M' for monthly and 'Q' for quaterly time series
    startDate: str of None
        date in YYYY-MM (2000-01) or YYYY-QQ (2000-Q1) format, None for all observations
    endDate: str or None
        date in YYYY-MM (2000-01) or YYYY-QQ (2000-Q1) format, None for all observations
        
    Returns
    -----
    data: pandas.DataFrame
        data downloaded from OECD
    subjects: pandas.DataFrame
        subject codes and full names
    measures: pandas.DataFrame
        measure codes and full names
        
    """
    
    # Data download
    
    if dsname == 'MEI_CLI':
        response = makeOECDRequest(dsname
                                    , [subject, [country], [frequency]]
                                    , {'startTime': startDate, 'endTime': endDate, 'dimensionAtObservation': 'AllDimensions'})
    elif dsname == 'MEI_BTS_COS':
        response = makeOECDRequest(dsname
                                    , [subject, [country], measure, [frequency]]
                                    , {'startTime': startDate, 'endTime': endDate, 'dimensionAtObservation': 'AllDimensions'})
    else:
        response = makeOECDRequest(dsname
                                    , [[country], subject, measure, [frequency]]
                                    , {'startTime': startDate, 'endTime': endDate, 'dimensionAtObservation': 'AllDimensions'})
    
    # Data transformation
    
    if (response.status_code == 200):
        
        responseJson = response.json()
        
        obsList = responseJson.get('dataSets')[0].get('observations')
        
        if (len(obsList) > 0):
            
            if (len(obsList) >= 999999):
                print('Warning: You are near response limit (1 000 000 observations).')
        
            print('Data downloaded from %s' % response.url)
            
            timeList = [item for item in responseJson.get('structure').get('dimensions').get('observation') if item['id'] == 'TIME_PERIOD'][0]['values']
            subjectList = [item for item in responseJson.get('structure').get('dimensions').get('observation') if item['id'] == 'SUBJECT'][0]['values']
            if dsname == 'MEI_CLI':
                measureList = []
            else:
                measureList = [item for item in responseJson.get('structure').get('dimensions').get('observation') if item['id'] == 'MEASURE'][0]['values']
            #subjectList = responseJson.get('structure').get('dimensions').get('observation')[1]['values']
            #measureList = responseJson.get('structure').get('dimensions').get('observation')[2]['values']
            unitList = [item for item in responseJson.get('structure').get('attributes').get('observation')if item['id'] == 'UNIT'][0]['values']
            powercodeList = [item for item in responseJson.get('structure').get('attributes').get('observation')if item['id'] == 'POWERCODE'][0]['values']
            reference_periodList = [item for item in responseJson.get('structure').get('attributes').get('observation')if item['id'] == 'REFERENCEPERIOD'][0]['values']
            
            obs = pd.DataFrame(obsList).transpose()
            obs.rename(columns = {0: 'series',3: 'unitCode',4: 'powercodeCode',5: 'reference_periodCode'}, inplace = True)
            obs['id'] = obs.index
            obs = obs[['id', 'series', 'unitCode', 'powercodeCode', 'reference_periodCode']]
            obs['dimensions'] = obs.apply(lambda x: re.findall('\\d+', x['id']), axis = 1)
            
            if dsname == 'MEI_CLI':
                obs['subject'] = obs.apply(lambda x: subjectList[int(x['dimensions'][0])]['id'], axis = 1)
                id = list(obs['id'])
                obs['measure'] = ['' for tmp in range(len(id))]
                obs['time'] = obs.apply(lambda x: timeList[int(x['dimensions'][3])]['id'], axis = 1)
            elif dsname == 'MEI_BTS_COS':
                obs['subject'] = obs.apply(lambda x: subjectList[int(x['dimensions'][0])]['id'], axis = 1)
                obs['measure'] = obs.apply(lambda x: measureList[int(x['dimensions'][2])]['id'], axis = 1)
                obs['time'] = obs.apply(lambda x: timeList[int(x['dimensions'][4])]['id'], axis = 1)
            else:
                obs['subject'] = obs.apply(lambda x: subjectList[int(x['dimensions'][1])]['id'], axis = 1)
                obs['measure'] = obs.apply(lambda x: measureList[int(x['dimensions'][2])]['id'], axis = 1)
                obs['time'] = obs.apply(lambda x: timeList[int(x['dimensions'][4])]['id'], axis = 1)
            unit = list(obs['unitCode'])
            for i in range(len(unit)):
                if str(unit[i]) != 'nan': 
                    unit[i] = unitList[int(unit[i])]['name']
                else:
                    unit[i] = ''
            obs['unit'] = unit
            powercode = list(obs['powercodeCode'])
            for i in range(len(powercode)):
                if str(powercode[i]) != 'nan': 
                    powercode[i] = powercodeList[int(powercode[i])]['name']
                else:
                    powercode[i] = ''
            obs['powercode'] = powercode
            reference_period = list(obs['reference_periodCode'])
            for i in range(len(reference_period)):
                if str(reference_period[i]) != 'nan': 
                    reference_period[i] = reference_periodList[int(reference_period[i])]['name']
                else:
                    reference_period[i] = ''
            obs['reference_period'] = reference_period
            #obs['names'] = obs['subject'] + '_' + obs['measure']
            
            #data = obs.pivot_table(index = 'time', columns = ['names'], values = 'series')
            
            data = obs.pivot_table(index = 'time', columns = ['subject', 'measure', 'unit', 'powercode', 'reference_period'], values = 'series')
            
            return(data, pd.DataFrame(subjectList), pd.DataFrame(measureList))
        
        else:
        
            print('Error: No available records, please change parameters')
            return(pd.DataFrame(), pd.DataFrame(), pd.DataFrame())

    else:
        
        print('Error: %s' % response.status_code)
        return(pd.DataFrame(), pd.DataFrame(), pd.DataFrame())


def createDataFrameFromOECD(countries = ['CZE', 'AUT', 'DEU', 'POL', 'SVK'], dsname = 'MEI', subject = [], measure = [], frequency = 'M', startDate = None, endDate = None):
    
    """
    Request data from OECD API and return pandas DataFrame. This works with OECD datasets
    where the first dimension is location (check the structure with getOECDJSONStructure()
    function).
    
    Parameters
    -----
    countries: list
        list of country codes, list of OECD codes available at http://www.oecd-ilibrary.org/economics/oecd-style-guide/country-names-codes-and-currencies_9789264243439-8-en
    dsname: str
        dataset identifier (default MEI for main economic indicators)
    subject: list
        list of subjects, empty list for all
    measure: list
        list of measures, empty list for all
    frequency: str
        'M' for monthly and 'Q' for quaterly time series
    startDate: str or None
        date in YYYY-MM (2000-01) or YYYY-QQ (2000-Q1) format, None for all observations
    endDate: str or None
        date in YYYY-MM (2000-01) or YYYY-QQ (2000-Q1) format, None for all observations
        
    Returns
    -----
    data: pandas.DataFrame
        data downloaded from OECD
    subjects: pandas.DataFrame
        subject codes and full names
    measures: pandas.DataFrame
        measure codes and full names
        
    """        
    
    dataAll = pd.DataFrame()
    subjectsAll = pd.DataFrame()
    measuresAll = pd.DataFrame()
    
    for country in countries:
        
        dataPart, subjectsPart, measuresPart = createOneCountryDataFrameFromOECD(country = country, dsname = dsname, subject = subject, measure = measure, frequency = frequency, startDate = startDate, endDate = endDate)
        
        if (len(dataPart) > 0):
            
            dataPart.columns = pd.MultiIndex(levels = [[country], dataPart.columns.levels[0], dataPart.columns.levels[1], dataPart.columns.levels[2], dataPart.columns.levels[3], dataPart.columns.levels[4]],
                codes = [np.repeat(0, dataPart.shape[1]), dataPart.columns.codes[0], dataPart.columns.codes[1], dataPart.columns.codes[2], dataPart.columns.codes[3], dataPart.columns.codes[4]], 
                names = ['country', dataPart.columns.names[0], dataPart.columns.names[1], dataPart.columns.names[2], dataPart.columns.names[3], dataPart.columns.names[4]])
            
            dataAll = pd.concat([dataAll, dataPart], axis = 1)
            subjectsAll = pd.concat([subjectsAll, subjectsPart], axis = 0)
            measuresAll = pd.concat([measuresAll, measuresPart], axis = 0)
    
    if (len(subjectsAll) > 0):
        
        subjectsAll.drop_duplicates(inplace = True)
        
    if (len(measuresAll) > 0):
        
        measuresAll.drop_duplicates(inplace = True)
    
    return(dataAll, subjectsAll, measuresAll)
