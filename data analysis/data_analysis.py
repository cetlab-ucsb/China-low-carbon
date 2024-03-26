# -*- coding: utf-8 -*-
"""
Created on Sat Nov 20 18:10:04 2021

@author: haozheyang
"""

from pandas import read_csv,merge,concat, DataFrame, read_excel
import numpy as np

output_gen='yes'
output_cost='yes'

tech=['coal','gas','hydro','nuclear','solar','storage','wind']
output=DataFrame({
    'period': np.repeat([2020,2030,2040],7),
    'technology_TWh':np.tile(tech,3)
     })

output_capacity=DataFrame({
    'period': np.repeat([2020,2030,2040],7),
    'technology_MW':np.tile(tech,3)
     })

new_cost_description='moderate'
capital_cost=read_excel('C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/annualized_cost.xlsx',sheet_name=new_cost_description)
#offshore_sheet=new_cost_description+'_offshore'
#offshore=read_excel('C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/annualized_cost.xlsx',sheet_name=offshore_sheet)

cluster=read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/raw_data/cluster.csv')
technology=cluster.loc[cluster['gen_dbid']=="new",'technology']
generator=cluster.loc[cluster['gen_dbid']=="new",'project']
zone=cluster.loc[cluster['gen_dbid']=="new",'zone']
project_new_cost=DataFrame()
for i in range(len(technology)):
   tech_tmp=technology.iloc[i]
   cost_tmp=capital_cost[tech_tmp]
   zone_tmp=zone.iloc[i]
   cost_tmp_energy=[0 for i in range(len(cost_tmp))]
#   if tech_tmp=='Offshore_Wind':
#      cost_tmp=offshore[zone_tmp]
       
   if tech_tmp=='Battery_Storage':
       cost_tmp_energy=capital_cost['Battery_Storage_energy']
       
   project_new_cost=project_new_cost.append(DataFrame({
            'project': [generator.iloc[i] for j in range(len(cost_tmp))],
            'period': capital_cost['Vintage'],          
            'investment': cost_tmp,
            'energy': cost_tmp_energy
            }))
        

for test_id in ['BAU_LBNL','2C_LBNL','1p5C_LBNL']:
    
    path='H:/electricity modeling/data/'+test_id+'/results/'

    file1='dispatch_all.csv'
    file2='carbon_emissions_by_project.csv'
    file3='costs_capacity_all_projects.csv'
    file4='costs_operations.csv'
    file5='costs_transmission_capacity.csv'
    file6='capacity_all.csv'
    file7='transmission_new_capacity.csv'
    file8='capacity_gen_new_lin.csv'
    file9='capacity_stor_new_lin.csv'

    dispatch_path=path+file1
    capacity_path=path+file6
    carbon_path=path+file2
    capacity_cost_path=path+file3
    operation_cost_path=path+file4
    transmission_cost_path=path+file5
    transmission_capacity_path=path+file7
    capacity_new_path=path+file8
    stor_new_path=path+file9
    

#%%
    carbon=read_csv(carbon_path)
    carbon_province=carbon.groupby(['period','load_zone'])['carbon_emissions_tons'].sum()

#dispatch
    dispatch=read_csv(dispatch_path)
    mean_dispatch=dispatch.groupby(['period','load_zone','project','technology'])['power_mw'].mean().reset_index()
    def power_total(x):
        return sum(x)*8760/10**6

    capacity_technology=mean_dispatch.groupby(['period','technology'])['power_mw'].sum().reset_index()
    output_technology=mean_dispatch.groupby(['period','technology'])['power_mw'].apply(power_total).reset_index()
    output_technology_province=mean_dispatch.groupby(['period','load_zone','technology'])['power_mw'].apply(power_total).reset_index()
    Inner_Mongolia_output=DataFrame({
        'load_zone': 'Inner Mongolia',
        'period':output_technology_province.loc[output_technology_province.load_zone=='East_Inner_Mongolia','period'].values,
        'technology': output_technology_province.loc[output_technology_province.load_zone=='East_Inner_Mongolia','technology'].values,
        'power_mw':output_technology_province.loc[output_technology_province.load_zone=='East_Inner_Mongolia','power_mw'].values+output_technology_province.loc[output_technology_province.load_zone=='West_Inner_Mongolia','power_mw'].values,
        })
    
    output_technology_province=output_technology_province.append(Inner_Mongolia_output,ignore_index=True)
    output_technology_province=output_technology_province.drop(output_technology_province[output_technology_province['load_zone'].isin(['East_Inner_Mongolia','West_Inner_Mongolia'])].index,axis=0)
    output_technology_province=output_technology_province.pivot(index=['period','load_zone'],columns='technology',values='power_mw')
    output_technology_province.to_excel('data visualization/generation/generation_tech_'+test_id+'.xlsx',na_rep=0)

    
    output[test_id]=output_technology['power_mw']
            

#output_technology_province.to_csv('data_analysis/validation.csv')
    if output_gen=='yes':
        file_output='data_analysis/generation_mix_prm.csv'
        output.to_csv(file_output,index=False)

#%%
    #max_dispatch=dispatch.groupby(['period','load_zone','project','technology'])['power_mw'].max().reset_index()
    #ii=0
    #for i in max_dispatch['power_mw']:
    #    if i>0:
    #        max_dispatch.loc[ii,'id']=1
    #    else:
    #        max_dispatch.loc[ii,'id']=0
    #    ii=ii+1
    
    capacity=read_csv(capacity_path)
    capacity_technology=capacity.groupby(['period','technology'])['capacity_mw'].sum().reset_index()
    output_capacity[test_id]=capacity_technology['capacity_mw']
    if output_gen=='yes':
        output_capacity.to_csv('data_analysis/capacity_mix_prm.csv')
    #capacity_2040=capacity.loc[capacity.period==j,:]
    capacity_2040=capacity
    
    capacity_2040=capacity_2040.groupby(['period','load_zone','technology'])['capacity_mw'].sum().reset_index()
    
    Inner_Mongolia_load=DataFrame({
        'load_zone': 'Inner Mongolia',
        'period':capacity_2040.loc[capacity_2040.load_zone=='East_Inner_Mongolia','period'].values,
        'technology': capacity_2040.loc[capacity_2040.load_zone=='East_Inner_Mongolia','technology'].values,
        'capacity_mw':capacity_2040.loc[capacity_2040.load_zone=='East_Inner_Mongolia','capacity_mw'].values+capacity_2040.loc[capacity_2040.load_zone=='West_Inner_Mongolia','capacity_mw'].values,
        })
    
    capacity_2040=capacity_2040.append(Inner_Mongolia_load, ignore_index=True)
    capacity_2040=capacity_2040.drop(capacity_2040[capacity_2040['load_zone'].isin(['East_Inner_Mongolia','West_Inner_Mongolia'])].index,axis=0)
 
    
    capacity_2040=capacity_2040.pivot(index=['period','load_zone'],columns='technology',values='capacity_mw')
    capacity_2040.reset_index().to_excel('data visualization/generation/capacity_'+test_id+'.xlsx',na_rep=0,index=False)
    
    

