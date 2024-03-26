# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 10:51:15 2022

@author: haozheyang
"""
'''
Calculate the job year during 2020-2045
'''

import os
os.chdir("//babylon/phd/haozheyang/electricity modeling/labor")

from IPython import get_ipython
get_ipython().magic('reset -sf')

import labor_effect_investment
import labor_effect_operation
import labor_effect_OM


import pandas as pd
discount_2030=1/1.03**10
discount_2040=1/1.03**20

wage_increase_2030={
                    '1p5C':1.572397181,
                    '2C':1.5835176,
                    'NDC':1.589507527,
                    'BAU':1.616615617
                    }
			
			
wage_increase_2040={
                   '1p5C':2.135874455,
                   '2C':2.163681297,
                   'NDC':2.110867732,
                   'BAU':2.179628432}

wage_average=pd.DataFrame()
wage_average2=pd.DataFrame()
wage_average3=pd.DataFrame()

test_id=['BAU_LBNL','2C_LBNL','1p5C_LBNL']
for case in test_id:
    case_scenario=case.split('_')[1]
    #deflator_2030=wage_increase_2030[case_scenario]*discount_2030
    #deflator_2040=wage_increase_2040[case_scenario]*discount_2040
    deflator_2030=1
    deflator_2040=1
    multiplier=pd.DataFrame()
    multiplier_2020=pd.read_excel('input_output_multiplier/multiplier_capacity_2020_'+case+'.xlsx')
    multiplier_2030=pd.read_excel('input_output_multiplier/multiplier_capacity_2030_'+case+'.xlsx')
    multiplier_2040=pd.read_excel('input_output_multiplier/multiplier_capacity_2040_'+case+'.xlsx')
    multiplier['province']=multiplier_2020['Province']
    multiplier_tmp=multiplier_2020.iloc[:,1:]*5+multiplier_2030.iloc[:,1:]*10+multiplier_2040.iloc[:,1:]*10
    multiplier=pd.concat([multiplier,pd.DataFrame(multiplier_tmp)],axis=1)
    multiplier['total']=multiplier.loc[:,'Coal':'Wind'].sum(axis=1)
    
    multiplier_operation=pd.DataFrame()
    multiplier_operation_2020=pd.read_excel('input_output_multiplier/multiplier_operation_2020_'+case+'.xlsx')
    multiplier_operation_2030=pd.read_excel('input_output_multiplier/multiplier_operation_2030_'+case+'.xlsx')
    multiplier_operation_2040=pd.read_excel('input_output_multiplier/multiplier_operation_2040_'+case+'.xlsx')
    multiplier_operation['province']=multiplier_operation_2020['Province']
    multiplier_operation_tmp=multiplier_operation_2020.iloc[:,1:]*5+multiplier_operation_2030.iloc[:,1:]*10+multiplier_operation_2040.iloc[:,1:]*10
    multiplier_operation=pd.concat([multiplier_operation,pd.DataFrame(multiplier_operation_tmp)],axis=1)
    multiplier_operation['total']=multiplier_operation.loc[:,'Coal':'Wind'].sum(axis=1)
    #parameter
    job2=pd.DataFrame()
    job=pd.read_excel('employment/'+case+'.xlsx').fillna(0)
    job_tmp=pd.DataFrame(job.iloc[0:31,2:10].values*5+job.iloc[31:62,2:10].values*10+job.iloc[62:,2:10].values*10)
    job_tmp.columns=job.columns[2:10]
    
    #job2=pd.concat([job['load_zone'][0:31],job_tmp],axis=1)
    job2['load_zone']=job['load_zone'][0:31]
 
    job2['Coal']=multiplier['Coal']+multiplier_operation['Coal']+job_tmp['Coal']
    job2['Gas']=multiplier['Gas']+multiplier_operation['Gas']+job_tmp['Gas']
    job2['Hydro']=multiplier['Hydro']+multiplier_operation['Hydro']+job_tmp['Hydro']
    job2['Nuclear']=multiplier['Nuclear']+multiplier_operation['Nuclear']+job_tmp['Nuclear']
    job2['Solar']=multiplier['Solar']+multiplier_operation['Solar']+job_tmp['Solar']
    job2['Storage']=multiplier['Storage']+multiplier_operation['Storage']+job_tmp['Storage']
    job2['Transmission']=multiplier['Transmission']
    job2['Wind']=multiplier['Wind']+multiplier_operation['Wind']+job_tmp['Wind']

    
    wage=pd.DataFrame()
    wage_2020=pd.read_excel('input_output_multiplier/wage_capacity_2020_'+case+'.xlsx')
    wage_2030=pd.read_excel('input_output_multiplier/wage_capacity_2030_'+case+'.xlsx')
    wage_2040=pd.read_excel('input_output_multiplier/wage_capacity_2040_'+case+'.xlsx')
    wage['province']=wage_2020['Province']
    wage_tmp=wage_2020.iloc[:,1:]*5+wage_2030.iloc[:,1:]*10*deflator_2030+wage_2040.iloc[:,1:]*10*deflator_2040
    wage=pd.concat([wage,pd.DataFrame(wage_tmp)],axis=1)
    wage['total']=wage.loc[:,'Coal':'Wind'].sum(axis=1)/6.5
    
    wage_operation=pd.DataFrame()
    wage_operation_2020=pd.read_excel('input_output_multiplier/wage_operation_2020_'+case+'.xlsx')
    wage_operation_2030=pd.read_excel('input_output_multiplier/wage_operation_2030_'+case+'.xlsx')
    wage_operation_2040=pd.read_excel('input_output_multiplier/wage_operation_2040_'+case+'.xlsx')
    wage_operation['province']=wage_operation_2020['Province']
    wage_operation_tmp=wage_operation_2020.iloc[:,1:]*5+wage_operation_2030.iloc[:,1:]*10*deflator_2030+wage_operation_2040.iloc[:,1:]*10*deflator_2040
    wage_operation=pd.concat([wage_operation,pd.DataFrame(wage_operation_tmp)],axis=1)
    wage_operation['total']=wage_operation.loc[:,'Coal':'Wind'].sum(axis=1)/6.5
    
    wage_OM=pd.read_excel('employment/'+'wage_'+case+'.xlsx').fillna(0)
    wage_OM_tmp=(wage_OM.iloc[0:31,9].values*5+wage_OM.iloc[31:62,9].values*10*deflator_2030+wage_OM.iloc[62:,9].values*10*deflator_2040)
    
    wage_OM_tmp2=pd.DataFrame(wage_OM.iloc[0:31,2:10].values*5+wage_OM.iloc[31:62,2:10].values*10*deflator_2030+wage_OM.iloc[62:,2:10].values*10*deflator_2040)
    wage_OM_tmp2.columns=wage_OM.columns[2:10]
    
    wage_total_tmp=(wage_OM_tmp+wage_operation['total']+wage['total'])/job2.iloc[:,1:].sum(axis=1)
    wage_total_tmp2=(wage_operation['total']+wage['total'])/(multiplier['total']+multiplier_operation['total'])
    wage_total_tmp3=wage_operation.loc[:,'total']/multiplier_operation.loc[:,'total']
    
    wage_average[case]=wage_total_tmp
    wage_average2[case]=wage_total_tmp2
    wage_average3[case]=wage_total_tmp3
    
    wage2=pd.DataFrame()
    wage2['load_zone']=wage['province'][0:31]
    
    wage2['Coal']=wage['Coal']/6.5+wage_operation['Coal']/6.5+wage_OM_tmp2['Coal']
    wage2['Gas']=wage['Gas']/6.5+wage_operation['Gas']/6.5+wage_OM_tmp2['Gas']
    wage2['Hydro']=wage['Hydro']/6.5+wage_operation['Hydro']/6.5+wage_OM_tmp2['Hydro']
    wage2['Nuclear']=wage['Nuclear']/6.5+wage_operation['Nuclear']/6.5+wage_OM_tmp2['Nuclear']
    wage2['Solar']=wage['Solar']/6.5+wage_operation['Solar']/6.5+wage_OM_tmp2['Solar']
    wage2['Storage']=wage['Storage']/6.5+wage_operation['Storage']/6.5+wage_OM_tmp2['Storage']
    wage2['Transmission']=wage['Transmission']/6.5
    wage2['Wind']=wage['Wind']/6.5+wage_operation['Wind']/6.5+wage_OM_tmp2['Wind']
        
    job2.to_excel('job_new_'+case+'.xlsx')
    wage2.to_excel('wage_new_'+case+'.xlsx')
wage_average.insert(0,'province',wage_OM['load_zone'].values[0:31])
wage_average.to_excel('wage.xlsx')

wage_average2.insert(0,'province',wage_OM['load_zone'].values[0:31])
wage_average2.to_excel('wage_short.xlsx')

wage_average3.insert(0,'province',wage_OM['load_zone'].values[0:31])
wage_average3.to_excel('wage_operation.xlsx')
