# -*- coding: utf-8 -*-
"""
Created on Sun Jan 30 08:50:01 2022

@author: haozheyang
"""


from pandas import read_csv, read_excel,merge,concat, DataFrame
import numpy as np

output_tag="yes"
    
tech=['coal','gas','hydro','nuclear','solar','storage','wind']
output=DataFrame({
    'period': np.repeat([2020,2030,2040],7),
    'technology_TWh':np.tile(tech,3)
     })


year=np.arange(1,26,1)
discount_factor=(1/1.08)**year

discount_2020=1
discount_2030=1/1.08**10
discount_2040=1/1.08**20
'''
for i in discount_factor[0:5]:
    discount_2020=discount_2020+i

for i in discount_factor[5:15]:
    discount_2030=discount_2030+i
    
for i in discount_factor[15:25]:
    discount_2040=discount_2040+i   
'''
generation=DataFrame()
sector=DataFrame()
sector['technology']=['Coal','Gas','Hydro','Nuclear','Solar','Storage','Transmission','Wind','Total']
cost_technology=DataFrame()

new_cost_description='moderate'
capital_cost=read_excel('H:/electricity modeling/investment.xlsx',sheet_name=new_cost_description)
lifetime=read_excel('H:/electricity modeling/investment.xlsx',sheet_name='lifetime')
#offshore_sheet=new_cost_description+'_offshore'
#offshore=read_excel('C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/annualized_cost.xlsx',sheet_name=offshore_sheet)

cluster=read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/raw_data/cluster.csv')
technology=cluster.loc[cluster['gen_dbid']=="existing",'technology']
generator=cluster.loc[cluster['gen_dbid']=="existing",'project']
zone=cluster.loc[cluster['gen_dbid']=="existing",'zone']
project_cost=DataFrame()
for i in range(len(technology)):
   tech_tmp=technology.iloc[i].replace('_EP','')
   cost_tmp=capital_cost[tech_tmp]
   life_tmp=lifetime[tech_tmp]
   zone_tmp=zone.iloc[i]
   cost_tmp_energy=[0 for i in range(len(cost_tmp))]
#   if tech_tmp=='Offshore_Wind':
#      cost_tmp=offshore[zone_tmp]
       
   if tech_tmp=='Battery_Storage':
       cost_tmp_energy=capital_cost['Battery_Storage_energy']
       
   project_cost=project_cost.append(DataFrame({
            'project': [generator.iloc[i] for j in range(len(cost_tmp))],
            'period': capital_cost['Vintage'],  
            'lifetime': life_tmp,
            'investment': cost_tmp,
            'energy': cost_tmp_energy
            }))

project_existing=project_cost.loc[project_cost.period==2020,:]
crf=1.08**project_existing['lifetime']*0.08/(1.08**project_existing['lifetime']-1)
project_existing['annual_cost']=project_existing['investment']*crf
project_existing_cost=project_existing[['project','annual_cost']]
                 

for test_id in ['BAU_LBNL_5period','2C_LBNL_5period','1p5C_LBNL_5period']:
    
    path='H:/electricity modeling/data/'+test_id+'/results/'

    file1='dispatch_all.csv'
    file2='carbon_emissions_by_project.csv'
    file3='costs_capacity_all_projects.csv'
    file4='costs_operations.csv'
    file5='costs_transmission_capacity.csv'
    file6='capacity_all.csv'
    file7='npv.csv'
    file8='load_balance.csv'
    
    dispatch_path=path+file1
    capacity_path=path+file6
    carbon_path=path+file2
    capacity_cost_path=path+file3
    operation_cost_path=path+file4
    transmission_cost_path=path+file5
    npv_path=path+file7
    load_path=path+file8

    load=read_csv(load_path)
    load_total=load.groupby(['period'])['load_mw'].sum().reset_index()
    load_total['load_mw']=load_total['load_mw']*30.4167
    
    dispatch=read_csv(dispatch_path)
    mean_dispatch=dispatch.groupby(['period','load_zone','project','technology'])['power_mw'].mean().reset_index()
    def power_total(x):
        return sum(x)*8760/10**6

    capacity_technology=mean_dispatch.groupby(['period','technology'])['power_mw'].sum().reset_index()
    output_technology=mean_dispatch.groupby(['period','technology'])['power_mw'].apply(power_total).reset_index()
    output_technology_province=mean_dispatch.groupby(['period','load_zone'])['power_mw'].apply(power_total).reset_index()
    #output_technology_province=output_technology_province.pivot(index=['period','load_zone'],columns='technology',values='power_mw')
    
#%%
#cost
    #capacity
    capacity_cost=read_csv(capacity_cost_path)
    capacity_cost_region=capacity_cost.groupby(['period','technology','load_zone'])['capacity_cost'].sum().reset_index()
    #operation
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
    #transmission
    transmission_cost=read_csv(transmission_cost_path)
    transmission_cost_region=transmission_cost.groupby(['period','load_zone_to'])['capacity_cost'].sum().reset_index()
    transmission_cost_region['technology']='Transmission'
    transmission_cost_region['operation_cost']=0
    transmission_cost_region=transmission_cost_region.rename(columns={'load_zone_to':'load_zone'})
    #existing cost
    capacity=read_csv(capacity_path)
    capacity_existing=capacity.loc[capacity.capacity_type.isin(['store_spec','gen_spec']),:]
    capacity_existing=capacity_existing.merge(project_existing_cost,how='left')
    capacity_existing['existing_cost']=capacity_existing.annual_cost*capacity_existing.capacity_mw
    capacity_existing_region=capacity_existing.groupby(['period','load_zone','technology'])['existing_cost'].sum().reset_index()
    #%%
    npv=read_csv(npv_path)[['Total_Capacity_Costs','Total_Variable_OM_Cost','Total_Fuel_Cost','Total_Tx_Capacity_Costs']]
    
    cost_total=merge(capacity_cost_region,operation_cost_region[['period','technology','load_zone','operation_cost']],how='outer')
    cost_total=cost_total.merge(capacity_existing_region[['period','technology','load_zone','existing_cost']],how='left').fillna(0)
        
    validation_capacity=5*(cost_total.loc[cost_total.period==2020,'capacity_cost'].values*discount_2020+
                           cost_total.loc[cost_total.period==2030,'capacity_cost'].values*discount_2030+
                           cost_total.loc[cost_total.period==2040,'capacity_cost'].values*discount_2040)
    
    print(sum(validation_capacity)-npv['Total_Capacity_Costs'])
    
    validation_operation=5*(cost_total.loc[cost_total.period==2020,'operation_cost'].values*discount_2020+
                           cost_total.loc[cost_total.period==2030,'operation_cost'].values*discount_2030+
                           cost_total.loc[cost_total.period==2040,'operation_cost'].values*discount_2040)
        
    print(sum(validation_operation)-npv['Total_Fuel_Cost']-npv['Total_Variable_OM_Cost'])
    
    cost_total=cost_total.append(transmission_cost_region).fillna(0)
    
    validation_transmission=5*(transmission_cost_region.loc[transmission_cost_region.period==2020,'capacity_cost'].values*discount_2020+
                           transmission_cost_region.loc[transmission_cost_region.period==2030,'capacity_cost'].values*discount_2030+
                           transmission_cost_region.loc[transmission_cost_region.period==2040,'capacity_cost'].values*discount_2040)
     
    print(sum(validation_transmission)-npv['Total_Tx_Capacity_Costs'])
    
    cost_total['total']=cost_total['capacity_cost']+cost_total['operation_cost']+cost_total['existing_cost']
    cost_total['total_validation']=cost_total['capacity_cost']+cost_total['operation_cost']

    cost_sector=cost_total.groupby(['period','technology'])['total'].sum().reset_index()
    cost_sector=cost_sector.pivot(index=['technology'],columns='period',values='total')
    cost_sector_validation=cost_total.groupby(['period','technology'])['total_validation'].sum().reset_index()
    cost_sector_validation=cost_sector_validation.pivot(index=['technology'],columns='period',values='total_validation')
    cost_sector['NPV']=cost_sector.iloc[:,0]*discount_2020*5+cost_sector.iloc[:,1]*discount_2030*10+cost_sector.iloc[:,2]*discount_2040*10
    validation=(cost_sector_validation.iloc[:,0]*discount_2020+cost_sector_validation.iloc[:,1]*discount_2030+cost_sector_validation.iloc[:,2]*discount_2040)*5
    
    print(npv.sum(axis=1)-validation.sum())
    cost_sector.loc['total',:]=cost_sector.sum()
    if output_tag=="yes":
        cost_sector.to_excel('data visualization/cost_sector/cost_sector_'+test_id+'.xlsx')
    sector[test_id]=cost_sector['NPV'].values
    
    cost_sum=cost_total.groupby(['period','load_zone'])['total'].sum().reset_index()
    
    cost_average=cost_sum.merge(output_technology_province)
    cost_average['dollar_MWh']=cost_average['total']/cost_average['power_mw']/10**6
    Inner_Mongolia=DataFrame({
                             'period': [2020,2030,2040],
                             'load_zone':'Inner_Mongolia',
                             'total': cost_average.loc[cost_average['load_zone']=='East_Inner_Mongolia','total'].values+cost_average.loc[cost_average['load_zone']=='West_Inner_Mongolia','total'].values,
                             'power_mw':cost_average.loc[cost_average['load_zone']=='East_Inner_Mongolia','power_mw'].values+cost_average.loc[cost_average['load_zone']=='West_Inner_Mongolia','power_mw'].values
                             })
    Inner_Mongolia['dollar_MWh']=Inner_Mongolia['total']/Inner_Mongolia['power_mw']/10**6
    cost_average=cost_average.append(Inner_Mongolia)
    cost_average=cost_average.drop(cost_average[cost_average['load_zone'].isin(['East_Inner_Mongolia','West_Inner_Mongolia'])].index,axis=0) 
    cost_province_average=cost_average.pivot(index=['load_zone'],columns='period',values='dollar_MWh')
    
    cost_province_total=cost_average.pivot(index=['load_zone'],columns='period',values='total')
    cost_province_total['sum']=cost_province_total.sum(axis=1)
    cost_province_total.loc['country',:]=cost_province_total.sum(axis=0)
    
    cost_province_generation=cost_average.pivot(index=['load_zone'],columns='period',values='power_mw')
    cost_province_generation['sum']=5*cost_province_generation.iloc[:,0]+10*cost_province_generation.iloc[:,1]+10*cost_province_generation.iloc[:,2]
    cost_province_generation.loc['country',:]=cost_province_generation.sum(axis=0)
    
    generation_tmp=cost_province_generation['sum'].rename(test_id)
    generation=concat([generation,generation_tmp],axis=1)
    
    total_generation=cost_province_generation.loc['country',]
    cost_sector=cost_sector.append(total_generation.iloc[0:3,])
    cost_sector_technology=cost_sector.iloc[0:8,0:3]/cost_sector.iloc[-1,0:3]/10**6
    cost_sector_technology['average']=cost_sector_technology.mean(axis=1)
    cost_sector_technology['scenario']=test_id
    
    cost_technology=cost_technology.append(cost_sector_technology[['average','scenario']])
    
    cost_province_generation.iloc[31,0:3]=load_total.iloc[0:3,1]
    cost_province_average.loc['country',:]=cost_province_total.loc['country',:]/cost_province_generation.loc['country',:]
    cost_province_average['sum']=cost_province_total['sum']/cost_province_generation['sum']/10**6
    #cost_province_total=cost_province_total.sort_values(by='sum',axis=1)
    if output_tag=="yes":
        cost_province_total.to_csv('data visualization/cost_total/cost_total_'+test_id+'.csv')
        cost_province_average.to_csv('data visualization/cost_average/cost_average_'+test_id+'.csv')
        cost_province_generation.to_csv('data visualization/generation/generation_'+test_id+'.csv')

if output_tag=="yes":
    sector.to_excel('data visualization/cost_sector/sector.xlsx',index=False)    
    generation.to_excel('data visualization/generation/generation.xlsx')    
   
cost_tech_table=cost_technology.reset_index().pivot(index='scenario',columns='technology',values='average').sort_index(ascending=False)
if output_tag=="yes":
    cost_tech_table.to_excel('data visualization/cost_sector/sector_tech.xlsx')   
