# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 23:45:26 2022

@author: haozheyang
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Nov 20 18:10:04 2021

@author: haozheyang
"""

from pandas import read_csv,merge,concat, DataFrame, read_excel
import numpy as np
tech=['coal','gas','hydro','nuclear','solar','storage','wind']
output=DataFrame({
    'period': np.repeat([2020,2030,2040],7),
    'technology_TWh':np.tile(tech,3)
     })

output_capacity=DataFrame({
    'period': np.repeat([2020,2030,2040],7),
    'technology_MW':np.tile(tech,3)
     })


cluster=read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/raw_data/cluster.csv')
technology=cluster.loc[cluster['gen_dbid']=="new",'technology']
generator=cluster.loc[cluster['gen_dbid']=="new",'project']
zone=cluster.loc[cluster['gen_dbid']=="new",'zone']       

s1=['BAU_LBNL','2C_LBNL','1p5C_LBNL']
#s2=['_'.join([i,'low','demand']) for i in s1]
#s3=['_'.join([i,'high','demand']) for i in s1]
s4=['_'.join([i,'advance']) for i in s1]
s5=['_'.join([i,'conservative']) for i in s1]  
s6=['_'.join([i,'coal']) for i in s1]  
s7=[i.replace('LBNL','growth') for i in s1]
s8=['_'.join([i,'CCS']) for i in s1]
s9=['_'.join([i,'5period']) for i in s1]
s=s4+s5+s6+s7+s8
s=s9

for test_id in s:
    
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
    file10='capacity_gen_ccs_new.csv'

    dispatch_path=path+file1
    capacity_path=path+file6
    carbon_path=path+file2
    capacity_cost_path=path+file3
    operation_cost_path=path+file4
    transmission_cost_path=path+file5
    transmission_capacity_path=path+file7
    capacity_new_path=path+file8
    stor_new_path=path+file9
    ccs_new_path=path+file10
    
    new_cost_description_t=test_id.split('_')
    if len(new_cost_description_t)==2:
        new_cost_description='moderate'
    else: 
        new_cost_description=new_cost_description_t[2]
        if new_cost_description=='advance':
            new_cost_description='high'
        if new_cost_description=='coal':
            new_cost_description='moderate'
        if new_cost_description=='CCS':
            new_cost_description='moderate'
        if new_cost_description=='5period':
            new_cost_description='moderate'
            
    capital_cost=read_excel('C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/annualized_cost.xlsx',sheet_name=new_cost_description)
    #offshore_sheet=new_cost_description+'_offshore'
    #offshore=read_excel('C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/annualized_cost.xlsx',sheet_name=offshore_sheet)
    
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


    capacity=read_csv(capacity_path)
    capacity_technology=capacity.groupby(['period','technology'])['capacity_mw'].sum().reset_index()
  
    
    capacity.loc[capacity['period']==2020,'delta_capacity']=0
    for j in [2030,2040]:
        capacity.loc[capacity['period']==j,'delta_capacity']=capacity.loc[capacity['period']==j,'capacity_mw'].values-capacity.loc[capacity['period']==j-10,'capacity_mw'].values

    capacity['build_capacity']=0
    capacity.loc[capacity['delta_capacity']>0,'build_capacity']=capacity.loc[capacity['delta_capacity']>0,'delta_capacity']
    #capacity_dispatch=capacity.merge(max_dispatch,on=['period','project','load_zone','technology'])
    #capacity_dispatch['capacity_operation']=capacity_dispatch['capacity_mw']*capacity_dispatch['id']

    #dispatch_region=capacity_dispatch.groupby(['period','load_zone','technology'])['capacity_operation'].sum().reset_index()
    #dispatch_1=dispatch_region.loc[dispatch_region['period']==2020,['load_zone','technology','capacity_operation']].reset_index().drop('index',axis=1)
    #dispatch_2=dispatch_region.loc[dispatch_region['period']==2030,['load_zone','technology','capacity_operation']].reset_index().drop('index',axis=1)
    #dispatch_3=dispatch_region.loc[dispatch_region['period']==2040,['load_zone','technology','capacity_operation']].reset_index().drop('index',axis=1)

    #delta_dispatch=dispatch_1[['load_zone','technology']]
    #delta_dispatch['delta_capacity_2030']=(dispatch_2.iloc[:,2]-dispatch_1.iloc[:,2])
    #delta_dispatch['delta_capacity_2040']=(dispatch_3.iloc[:,2]-dispatch_1.iloc[:,2])

    #delta_dispatch.to_csv('labor/delta_capacity_'+test_id+'.csv',index=False)

#%%
#cost
    new_capacity=read_csv(capacity_new_path)
    new_storage=read_csv(stor_new_path)
    new_capacity=new_capacity.append(new_storage).fillna(0)
    try:
        new_ccs=read_csv(ccs_new_path)
        new_capacity=new_capacity.append(new_ccs).fillna(0)
    except:
        continue
    new_capacity=new_capacity.rename(columns={'vintage':'period'})
    #capacity_cost=read_csv(capacity_cost_path).merge(capacity)
    #capacity_cost=capacity_cost.merge(project_new_cost,how='left')
    capacity_cost=new_capacity.merge(project_new_cost,how='left')
    capacity_cost['capacity_cost']=capacity_cost['investment']*capacity_cost['new_build_mw']/10+capacity_cost['energy']*capacity_cost['new_build_mwh']/10
    capacity_cost_region=capacity_cost.groupby(['period','technology','load_zone'])['capacity_cost'].sum().reset_index()
    capacity_cost_region=capacity_cost_region.append(DataFrame({
                                      'period':capacity_cost_region.loc[capacity_cost_region.technology=='Solar','period'],
                                      'technology':'Hydro',
                                      'load_zone': capacity_cost_region.loc[capacity_cost_region.technology=='Solar','load_zone'],
                                      'capacity_cost':0
                                    })
        )
    
    operation_cost=read_csv(operation_cost_path)
    timeweight=operation_cost['timepoint_weight'][0]
    operation_cost_region=operation_cost.groupby(['period','technology','load_zone']).aggregate(
        {'variable_om_cost':'sum',
         'fuel_cost':'sum',
         'startup_cost':'sum',
         'shutdown_cost':'sum',
         'operational_violation_cost':'sum',
         'curtailment_cost':'sum',
         'timepoint_weight': 'mean'}
        ).reset_index()

    for i in [3,4,5,6,7,8]:
        tmp=operation_cost_region.iloc[:,i]*operation_cost_region['timepoint_weight'].to_numpy()
        operation_cost_region=concat([operation_cost_region,tmp],axis=1)
    
    operation_cost_region['operation_cost']=operation_cost_region.iloc[:,10:15].sum(axis=1)

    transmission_capacity=read_csv(transmission_capacity_path)   
    
    transmission_cost=read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/transmission/transmission_new_cost/1_transmission_new_cost_1.csv')
    transmission_capacity=transmission_capacity.merge(transmission_cost,how="left",left_on=['transmission_line','period'],right_on=['transmission_line',"vintage"])
    crf_t=((1+0.08)**20*0.08)/((1+0.08)**20-1)
    transmission_capacity['capacity_cost']=transmission_capacity['tx_annualized_real_cost_per_mw_yr']*transmission_capacity['new_build_transmission_capacity_mw']/crf_t*0.97/10
    transmission_capacity.loc[transmission_capacity.period==2020,'capacity_cost']=0
    
    transmission_cost_region=transmission_capacity.groupby(['period','load_zone_to'])['capacity_cost'].sum().reset_index()    
    transmission_cost_region['technology']='Transmission'
    transmission_cost_region['operation_cost']=0
    transmission_cost_region['capacity_cost']=transmission_cost_region['capacity_cost']/2
    transmission_cost_region=transmission_cost_region.rename(columns={'load_zone_to':'load_zone'})
    
    cost_total=merge(capacity_cost_region,operation_cost_region[['period','technology','load_zone','operation_cost']])
    cost_total['total']=cost_total['capacity_cost']
    cost_total.loc[cost_total['technology'].isin(['Coal','Gas']),'total']=cost_total.loc[cost_total['technology'].isin(['Coal','Gas']),'operation_cost']
    delta=cost_total;
    delta.to_csv('labor/delta/delta_cost_'+test_id+'.csv',index=False)
    
    cost_total=cost_total.append(transmission_cost_region)
    cost_investment=cost_total[['period','technology','load_zone','capacity_cost']]
    cost_operation=cost_total[['period','technology','load_zone','operation_cost']]
    #cost_total.loc[cost_total['technology'].isin(['Coal','Gas']),'total']=cost_total.loc[cost_total['technology'].isin(['Coal','Gas']),'operation_cost']
    #cost_total.to_csv('data visualization/cost_total_'+test_id+'.csv',index=False)
    
    #cost_1=cost_total.loc[cost_total['period']==2020,['load_zone','technology','total']].reset_index().drop('index',axis=1)
    #cost_2=cost_total.loc[cost_total['period']==2030,['load_zone','technology','total']].reset_index().drop('index',axis=1)
    #cost_3=cost_total.loc[cost_total['period']==2040,['load_zone','technology','total']].reset_index().drop('index',axis=1)

    #delta=cost_1[['load_zone','technology']]
    #delta['delta_cost_2030']=cost_2['total']-cost_1['total']
    #delta['delta_cost_2040']=cost_3.iloc[:,2]-cost_2.iloc[:,2]
    #delta.loc[delta['technology'].isin(['Coal','Gas']),'delta_cost_2030']=cost_total.loc[(cost_total['period']==2030) & (cost_total['technology'].isin(['Coal','Gas'])),'operation_cost'].values
    #delta.loc[delta['technology'].isin(['Coal','Gas']),'delta_cost_2040']=cost_total.loc[(cost_total['period']==2040) & (cost_total['technology'].isin(['Coal','Gas'])),'operation_cost'].values
    
    cost_investment.to_csv('labor/delta/sensitivity/capacity_cost_'+test_id+'.csv',index=False)
    cost_operation.to_csv('labor/delta/sensitivity/operation_cost_'+test_id+'.csv',index=False)
   # cost_trans_1=transmission_cost.loc[transmission_cost['period']==2020,['load_zone_from','load_zone_to','capacity_cost']]
   # cost_trans_2=transmission_cost.loc[transmission_cost['period']==2030,['load_zone_from','load_zone_to','capacity_cost']].reset_index().drop('index',axis=1)
   # delta_transmission_cost=cost_trans_1[['load_zone_from','load_zone_to']]
   # delta_transmission_cost['delta']=cost_trans_2.iloc[:,2]-cost_trans_1.iloc[:,2]
#%%%%%%%%%%%
#write carbon cap file
#project_zone=dispatch.loc[dispatch['technology'].isin(['Coal','Gas','Nuclear'])]
#project_zone=project_zone.loc[project_zone['timepoint']==2025012500,['project','load_zone']] 
#project_zone=project_zone.sort_values(by=['load_zone'])

#project_zone=project_zone.rename(columns={"load_zone": "carbon_cap_zone"})

#writepath='C:/Program Files/GRIDPATH/db/csvs_plexos_china/policy/carbon_cap/project_carbon_cap_zones/'
#scenario='2'
#description='project_carbon_cap_zones_china.csv'
#file_write=writepath+scenario+'_'+description
#project_zone.to_csv(file_write,index=False)