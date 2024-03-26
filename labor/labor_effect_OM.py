# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 14:11:18 2022

@author: haozheyang
"""

# -*- coding: utf-8 -*-
"""
Using multiplier from "Job creation during the global energy transition towards 100% renewable power system by 2050"
and Meeting well-below 2°C target would increase energy sector jobs globally
"""
import os
os.chdir("//babylon/phd/haozheyang/electricity modeling/labor")

from IPython import get_ipython
get_ipython().magic('reset -sf')


import pandas as pd


wage=pd.read_excel('employment_province.xlsx',sheet_name='OM_wage').melt(id_vars='Province',var_name='energy_source',value_name='wage')

test_id=['BAU_LBNL','2C_LBNL','1p5C_LBNL']


cluster=pd.read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/raw_data/cluster.csv')[['project','gen_dbid','technology','gen_full_load_heat_rate']]
cluster['technology']=cluster['technology'].str.replace('_EP','')

employment=pd.read_excel('employment_multiplier.xlsx',sheet_name='multiplier',usecols=range(0,6))

trend_construction=pd.read_excel('employment_multiplier.xlsx',sheet_name='construction_moderate').melt(id_vars='Vintage',var_name='technology',value_name='Scale_Capital')
trend_construction=trend_construction.rename(columns={'Vintage': 'period'})

trend_OM=pd.read_excel('employment_multiplier.xlsx',sheet_name='OM_moderate').melt(id_vars='Vintage',var_name='technology',value_name='Scale_OM')
trend_OM=trend_OM.rename(columns={'Vintage': 'period'})

for case in test_id:
    path='H:/electricity modeling/data/'+case+'/results/'
    
    file1='dispatch_all.csv'
    file2='capacity_all.csv'
    file3='costs_transmission_capacity.csv'
    
    dispatch_path=path+file1
    capacity_path=path+file2
    transmission_cost_path=path+file3
    
    capacity=pd.read_csv(capacity_path).rename(columns={'technology':'energy_source'}).merge(cluster,how='left').sort_values(['project','period'])
    capacity=capacity.merge(employment,how='left')
    capacity=capacity.merge(trend_OM,how='left').merge(trend_construction,how='left')
    
    capacity.loc[capacity['period']==2020,'delta_capacity']=0

    for j in [2030,2040]:
        capacity.loc[capacity['period']==j,'delta_capacity']=capacity.loc[capacity['period']==j,'capacity_mw'].values-capacity.loc[capacity['period']==j-10,'capacity_mw'].values
    
    capacity['build_capacity']=0
    capacity['retire_capacity']=0
    
    capacity.loc[capacity['delta_capacity']>0,'build_capacity']=capacity.loc[capacity['delta_capacity']>0,'delta_capacity']
    capacity.loc[capacity['delta_capacity']<0,'retire_capacity']=-capacity.loc[capacity['delta_capacity']<0,'delta_capacity']

    capacity['manufacture_employment']=(capacity['Manufacture'])*capacity['build_capacity']*capacity['Scale_Capital']
    capacity['construction_employment']=(capacity['Construction'])*capacity['build_capacity']*capacity['Scale_Capital']
    capacity['decomission_employment']=capacity['Decomission']*capacity['retire_capacity']
    capacity['operation_employment']=capacity['O&M']*capacity['capacity_mw']*capacity['Scale_OM']

    dispatch=pd.read_csv(dispatch_path).drop('technology',axis=1)
    dispatch=dispatch.groupby(['period','load_zone','project'])['power_mw'].mean().reset_index()
    dispatch['generation']=dispatch['power_mw']*8760
    dispatch=dispatch.merge(cluster,how='left').merge(employment,how='left')
    dispatch['mining_employment']=dispatch['generation']*dispatch['gen_full_load_heat_rate']*1.055*dispatch['Fuel']/10**6 #GJ
    
    transmission=pd.read_csv(transmission_cost_path).sort_values(['period','tx_line'])
    transmission.loc[transmission['period']==2020,'delta_cost']=0

    for j in [2030,2040]:
        transmission.loc[transmission['period']==j,'delta_cost']=transmission.loc[transmission['period']==j,'capacity_cost'].values-transmission.loc[transmission['period']==j-10,'capacity_cost'].values
    
    crf_t=((1+0.08)**20*0.08)/((1+0.08)**20-1)
    transmission['transmission_job']=0.97*transmission['delta_cost']/crf_t/10*4725/10**9/2 #0.97 is the investment fraction
    
    #Job creation during the global energy transition towards 100% renewable power system by 2050
    
    '''
    job_grid_from=transmission[['period','load_zone_from','transmission_job']]
    job_grid_to=transmission[['period','load_zone_to','transmission_job']]
    job_grid=pd.merge(job_grid_from,job_grid_to,left_on=['period','load_zone_from'],right_on=['period','load_zone_to'])
    job_grid['transmission_job']=job_grid['transmission_job_x']+job_grid['transmission_job_y']
    job_grid=job_grid.groupby(['period','load_zone_to'])['transmission_job'].sum().reset_index().rename(columns={'load_zone_to':'load_zone','transmission_job':'total'})
    job_grid.loc[job_grid['total']<0,'total']=0
    job_grid['energy_source']='Transmission'
    '''
    job=pd.merge(capacity[['period','project','energy_source','load_zone','manufacture_employment','construction_employment','operation_employment','decomission_employment']],
                 dispatch[['period','project','load_zone','mining_employment']])
    job=job.fillna(0)
    
    #job['total']=job['capital_employment']/10+job['operation_employment']+job['decomission_employment']/10+job['mining_employment']
    
    job['total']=job['operation_employment']
    #job['decomission_employment']/10

    #job.loc[job['energy_source'].isin(['Coal,Gas']),'total']=job.loc[job['energy_source'].isin(['Coal,Gas']),'construction_employment']/10+job.loc[job['energy_source'].isin(['Coal,Gas']),'operation_employment']+job.loc[job['energy_source'].isin(['Coal,Gas']),'decomission_employment']/10
    #job.loc[job['energy_source'].isin(['Storage']),'total']=job.loc[job['energy_source'].isin(['Storage']),'construction_employment']/10+job.loc[job['energy_source'].isin(['Storage']),'manufacture_employment']/10+job.loc[job['energy_source'].isin(['Storage']),'operation_employment']+job.loc[job['energy_source'].isin(['Storage']),'decomission_employment']/10

    
    job_province=job.groupby(['period','load_zone','energy_source'])['total'].sum().reset_index()
    #job_province=job_province.append(job_grid)                                                                                                
    
    West_Inner=job_province.loc[job_province['load_zone']=='West_Inner_Mongolia',:]
    East_Inner=job_province.loc[job_province['load_zone']=='East_Inner_Mongolia',:]
    Inner=pd.merge(West_Inner,East_Inner,on=['period','energy_source']).drop(['load_zone_x','load_zone_y'],axis=1)
    Inner['load_zone']='Inner Mongolia'
    Inner['total']=Inner['total_x']+Inner['total_y']
    Inner=Inner.drop(['total_x','total_y'],axis=1)
    job_province=job_province.drop(job_province[job_province['load_zone'].isin(['East_Inner_Mongolia','West_Inner_Mongolia'])].index)
    job_province=job_province.append(Inner, ignore_index=True)
    job_province=job_province.merge(wage,how='left',left_on=['load_zone','energy_source'],right_on=['Province','energy_source'])
    job_province['wage_total']=job_province['total']*job_province['wage']/6.5
    
    job_employ=job_province.pivot(index=['period','load_zone'],columns=['energy_source'],values='total').reset_index()
    
    job_wage=job_province.pivot(index=['period','load_zone'],columns=['energy_source'],values='wage_total').reset_index()

    province=pd.read_excel("2017-MRIO.xlsx",sheet_name="Province")
    province.loc[26,'Province']='Shaanxi'
    province_order=pd.CategoricalDtype(province['Province'],ordered=True) 
    
    job_employ['load_zone'] = job_employ['load_zone'].astype(province_order)
    job_employ=job_employ.sort_values(['period','load_zone'])
    
    job_wage['load_zone'] = job_wage['load_zone'].astype(province_order)
    job_wage=job_wage.sort_values(['period','load_zone'])

    job_employ['sum']=job_employ.iloc[:,2:].sum(axis=1)
    job_employ.to_excel('employment/'+case+'.xlsx',index=False)

    job_wage['sum']=job_wage.iloc[:,2:].sum(axis=1)
    job_wage.to_excel('employment/'+'wage_'+case+'.xlsx',index=False)    
    
