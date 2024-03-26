# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 18:32:41 2021

@author: haozheyang
"""
import os
os.chdir("//babylon/phd/haozheyang/electricity modeling/labor")

from IPython import get_ipython
get_ipython().magic('reset -sf')

import numpy
import pandas as pd

construction_time=pd.DataFrame({'Coal': 1,
                                'Gas':1,
                                'Hydro':1,
                                'Nuclear':1,
                                'Solar': 1,
                                'Storage':1,
                                'Transmission':1,
                                'Wind': 1},
                               index=[0])

employ_raw=pd.read_excel("employment_province.xlsx",sheet_name='all')
employ_class=pd.read_excel("employment_province.xlsx",sheet_name='match')

employ_mat=employ_raw.to_numpy()
row=employ_mat.shape[0]
col=employ_mat.shape[1]

employ_mat=employ_mat[1:row,2:col]

class_index=employ_class['index'].to_numpy()


province_employ=numpy.zeros([31,42])
wage_mrio=pd.read_excel('wage_mrio.xlsx',header=None)


for i in range(42):
    index=i+1
    matrix_id=class_index==index
    merge_matrix=employ_mat[:,matrix_id]
    province_employ[:,i]=numpy.nansum(merge_matrix,axis=1)
#check
check_province=numpy.nansum(employ_mat,axis=1)-province_employ.sum(axis=1)

province_employ=province_employ.flatten('C')

#load MRIO
MRIO=pd.read_excel("2017-MRIO.xlsx",sheet_name='Table_2017',skiprows=3,
                   nrows=1310,usecols=range(3,1465)).to_numpy()
A=MRIO[0:42*31,0:42*31]
numpy.linalg.det(A)

C=MRIO[0:42*31,42*31+1:42*31+5*31+1]
C_province=numpy.zeros([42*31,31])

C_allocation=numpy.zeros([42*31,31])

for i in range(31):
    C_province[:,i]=C[:,i*5:i*5+5].sum(axis=1)
sum(sum(C))-sum(sum(C_province))

for i in range(42):
    C_allocation[numpy.arange(i,42*31,42),:]=C_province[numpy.arange(i,42*31,42),:]/C_province[numpy.arange(i,42*31,42),:].sum(axis=0)

C_allocation[numpy.isnan(C_allocation)]=0

check_allocation=C_allocation.sum(axis=0)

output=MRIO[0:42*31,1461]
a=A/output.T
L=numpy.linalg.inv(numpy.identity(42*31)-a)
#L=numpy.identity(42*31)

province_employ[output<1]=0

    
e=province_employ/output
e[23::42]=0
e_wage=wage_mrio.values[:,0]*e

#load investment ratio
investment=pd.read_excel("employment_province.xlsx",sheet_name="operation")

province=pd.read_excel("2017-MRIO.xlsx",sheet_name="Province")
province.loc[26,'Province']='Shaanxi'

test_id=['BAU_LBNL','2C_LBNL','1p5C_LBNL']
for case in test_id:
    delta=pd.read_csv('delta/operation_cost_'+case+'.csv',index_col=0).reset_index()
    #delta=pd.read_csv('delta/delta_cost_'+case+'.csv',index_col=0).drop(['operation_cost','capacity_cost'],axis=1).reset_index()
    #delta_capacity=pd.read_csv('delta_capacity_'+case+'.csv',index_col=0)
    #delta=delta_cost.merge(delta_capacity,how='left',on=['load_zone','technology']).reset_index()

    for i in  numpy.unique(delta['technology']):
        delta_tmp=delta[delta['technology']==i]
        In_tmp_cost=delta_tmp.loc[delta_tmp['load_zone']=='West_Inner_Mongolia','operation_cost'].values+delta_tmp.loc[delta_tmp['load_zone']=='East_Inner_Mongolia','operation_cost'].values
        #  In_tmp_cost_2040=delta_tmp.loc[delta_tmp['load_zone']=='West_Inner_Mongolia','delta_cost_2040'].values+delta_tmp.loc[delta_tmp['load_zone']=='East_Inner_Mongolia','delta_cost_2040'].values    
        period_tmp=delta_tmp.loc[delta_tmp['load_zone']=='West_Inner_Mongolia','period']
     #  In_tmp_capacity_2030=delta_tmp.loc[delta_tmp['load_zone']=='West_Inner_Mongolia','delta_capacity_2030'].values+delta_tmp.loc[delta_tmp['load_zone']=='East_Inner_Mongolia','delta_capacity_2030'].values
     #   In_tmp_capacity_2040=delta_tmp.loc[delta_tmp['load_zone']=='West_Inner_Mongolia','delta_capacity_2040'].values+delta_tmp.loc[delta_tmp['load_zone']=='East_Inner_Mongolia','delta_capacity_2040'].values
    
        Inner=pd.DataFrame({'load_zone':'Inner Mongolia',
                            'technology':i,
                            'period': period_tmp,
                            'operation_cost': In_tmp_cost})
                            #'delta_cost_2030':In_tmp_cost_2030,
                            #'delta_cost_2040':In_tmp_cost_2040,
                            #'delta_capacity_2030':In_tmp_capacity_2030,
                           # 'delta_capacity_2040':In_tmp_capacity_2040},index=[0])
    
        delta=delta.append(Inner,ignore_index=True)

    delta=delta.drop(delta[delta['load_zone']=='East_Inner_Mongolia'].index)
    delta=delta.drop(delta[delta['load_zone']=='West_Inner_Mongolia'].index)

    delta2=pd.DataFrame()

    for i in province['Province']:
        delta_value=delta.loc[delta['load_zone']==i]
        for j in numpy.unique(delta['technology']):
            delta_value2=delta_value.loc[delta_value['technology']==j]
            for k in [2020,2030,2040]:
                #delta_value_cost_2030=delta_value.loc[delta_value['technology']==j,'delta_cost_2030']
                #delta_value_cost_2040=delta_value.loc[delta_value['technology']==j,'delta_cost_2040']
                delta_value_cost=delta_value2.loc[delta_value['period']==k,'operation_cost']
                #delta_value_capacity_2030=delta_value.loc[delta_value['technology']==j,'delta_capacity_2030']
                #delta_value_capacity_2040=delta_value.loc[delta_value['technology']==j,'delta_capacity_2040']

                if not delta_value_cost.to_numpy().size:
                    delta_value_cost=pd.Series(0)
               # delta_value_capacity_2030=pd.Series(0)
               #if not delta_value_cost_2040.to_numpy().size:
                #delta_value_cost_2040=pd.Series(0)
                #delta_value_capacity_2040=pd.Series(0)
                
                delta2_tmp=pd.DataFrame({'period': k,
                                         'load_zone':i,
                                         'technology':j,                      
                                         'total': delta_value_cost
                                    # 'delta_cost_2030':delta_value_cost_2030,
                                    # 'delta_cost_2040':delta_value_cost_2040,
                                    # 'delta_capacity_2030':delta_value_capacity_2030,
                                    # 'delta_capacity_2040':delta_value_capacity_2040
                                           })
                delta2=pd.concat([delta2,delta2_tmp],axis=0)
            
    delta2=delta2.fillna(0).reset_index().drop('index',axis=1)      
       
#province_order=pd.CategoricalDtype(province['Province'],ordered=True) 
#delta['load_zone'] = delta['load_zone'].astype(province_order)
#delta2=delta.sort_values(['load_zone','technology'])
   
#%%emoloyment
#O&M employment - long-term employment
    '''
    OM_job=pd.read_excel("employment_province.xlsx",sheet_name="OM")
    OM_employ=pd.merge(delta2,OM_job)
    OM_employ['job_2030']=OM_employ['delta_capacity_2030']*OM_employ['employment']/1000 # MW* job/GW /1000
    OM_employ['job_2040']=OM_employ['delta_capacity_2040']*OM_employ['employment']/1000 # MW* job/GW /1000

    OM_multiplier_2030=OM_employ[['load_zone','technology','job_2030']].pivot(index='load_zone',columns='technology',values='job_2030').reset_index()
    OM_multiplier_2040=OM_employ[['load_zone','technology','job_2040']].pivot(index='load_zone',columns='technology',values='job_2040').reset_index()

    long_job=OM_employ.groupby('load_zone')[['job_2030','job_2040']].sum().reset_index()

    province_order=pd.CategoricalDtype(province['Province'],ordered=True) 
    OM_multiplier_2030['load_zone'] = OM_multiplier_2030['load_zone'].astype(province_order)
    OM_multiplier_2030=OM_multiplier_2030.sort_values(['load_zone'])

    OM_multiplier_2040['load_zone'] = OM_multiplier_2040['load_zone'].astype(province_order)
    OM_multiplier_2040=OM_multiplier_2040.sort_values(['load_zone'])

    OM_multiplier_2030.to_excel('O&M_job_2030_'+case+'.xlsx',index=False)    
    OM_multiplier_2040.to_excel('O&M_job_2040_'+case+'.xlsx',index=False)
    '''

    #multiplier - short-term employment
    investment=investment.fillna(0)
    #technology=investment.columns[1:10]
    technology=numpy.unique(delta['technology'])
    #technology=technology[[0,1,2,3,4,6]]

    #multiplier
    multiplier_2020=pd.DataFrame(province['Province'])
    multiplier_2030=pd.DataFrame(province['Province'])
    multiplier_2040=pd.DataFrame(province['Province'])
    
    wage_2020=pd.DataFrame(province['Province'])
    wage_2030=pd.DataFrame(province['Province'])
    wage_2040=pd.DataFrame(province['Province'])
    
    province_multiplier_2020=numpy.zeros([31,31])
    province_multiplier_2030=numpy.zeros([31,31])
    province_multiplier_2040=numpy.zeros([31,31])
    
    multiplier_total=pd.DataFrame({'technology':numpy.tile(technology,3),
                                   'year': numpy.repeat([2020,2030,2040],len(technology))
                                                    })
    province_wage_2020=numpy.zeros([31,31])
    province_wage_2030=numpy.zeros([31,31])
    province_wage_2040=numpy.zeros([31,31])
    
    province_multiplier_matrix_2020=numpy.zeros([31,31])
    province_multiplier_matrix_2030=numpy.zeros([31,31])
    province_multiplier_matrix_2040=numpy.zeros([31,31])
    
    province_wage_matrix_2020=numpy.zeros([31,31])
    province_wage_matrix_2030=numpy.zeros([31,31])
    province_wage_matrix_2040=numpy.zeros([31,31])
    
    for i in technology:
        investment_province_2020=delta2.loc[(delta2['technology']==i) & (delta2['period']==2020),'total'].to_numpy()/10000*6.75*1.06
        investment_province_2030=delta2.loc[(delta2['technology']==i) & (delta2['period']==2030),'total'].to_numpy()/10000*6.75*1.06
        investment_province_2040=delta2.loc[(delta2['technology']==i) & (delta2['period']==2040),'total'].to_numpy()/10000*6.75*1.06
        
        try:
            tmp=investment[i].to_numpy()
        except:
            pd_tmp=pd.DataFrame(numpy.zeros([31,1]),columns=[i])
            multiplier_2020=pd.concat([multiplier_2020,pd_tmp],axis=1)
            multiplier_2030=pd.concat([multiplier_2030,pd_tmp],axis=1)
            multiplier_2040=pd.concat([multiplier_2040,pd_tmp],axis=1)
            continue
        investment_tmp=numpy.tile(tmp,31)
        investment_tmp=numpy.tile(investment_tmp,(31,1))
        province_investment_2020=investment_tmp.T*C_allocation*investment_province_2020.T 
        province_investment_2030=investment_tmp.T*C_allocation*investment_province_2030.T 
        province_investment_2040=investment_tmp.T*C_allocation*investment_province_2040.T 
        
        province_multiplier_sector_2020=numpy.diag(e)@L@province_investment_2020
        province_multiplier_sector_2030=numpy.diag(e)@L@province_investment_2030
        province_multiplier_sector_2040=numpy.diag(e)@L@province_investment_2040
        
        multiplier_total.loc[(multiplier_total.technology==i) & (multiplier_total.year==2020),'multiplier']=province_multiplier_sector_2020.sum()/province_investment_2020.sum()*100
        multiplier_total.loc[(multiplier_total.technology==i) & (multiplier_total.year==2030),'multiplier']=province_multiplier_sector_2030.sum()/province_investment_2030.sum()*100
        multiplier_total.loc[(multiplier_total.technology==i) & (multiplier_total.year==2040),'multiplier']=province_multiplier_sector_2040.sum()/province_investment_2040.sum()*100

        multiplier_total.to_excel('input_output_multiplier/dollar_multiplier_operation_'+case+'.xlsx',index=False)

    
        province_wage_sector_2020=numpy.diag(e_wage)@L@province_investment_2020
        province_wage_sector_2030=numpy.diag(e_wage)@L@province_investment_2030
        province_wage_sector_2040=numpy.diag(e_wage)@L@province_investment_2040

        for j in range(31):
            province_multiplier_2020[j,:]=province_multiplier_sector_2020[j*42:(j+1)*42,:].sum(axis=0)
            province_multiplier_matrix_2020=province_multiplier_matrix_2020+province_multiplier_2020
            
            province_multiplier_2030[j,:]=province_multiplier_sector_2030[j*42:(j+1)*42,:].sum(axis=0)
            province_multiplier_matrix_2030=province_multiplier_matrix_2030+province_multiplier_2030
            
            province_multiplier_2040[j,:]=province_multiplier_sector_2040[j*42:(j+1)*42,:].sum(axis=0)
            province_multiplier_matrix_2040=province_multiplier_matrix_2040+province_multiplier_2040 
            
            province_wage_2020[j,:]=province_wage_sector_2020[j*42:(j+1)*42,:].sum(axis=0)
            province_wage_matrix_2020=province_wage_matrix_2020+province_wage_2020
            
            province_wage_2030[j,:]=province_wage_sector_2030[j*42:(j+1)*42,:].sum(axis=0)
            province_wage_matrix_2030=province_wage_matrix_2030+province_wage_2030
            
            province_wage_2040[j,:]=province_wage_sector_2040[j*42:(j+1)*42,:].sum(axis=0)
            province_wage_matrix_2040=province_wage_matrix_2040+province_wage_2040 
        
        multiplier_total_2020=province_multiplier_2020.sum(axis=1)
        multiplier_total_2030=province_multiplier_2030.sum(axis=1)
        multiplier_total_2040=province_multiplier_2040.sum(axis=1)
        
        wage_total_2020=province_wage_2020.sum(axis=1)
        wage_total_2030=province_wage_2030.sum(axis=1)
        wage_total_2040=province_wage_2040.sum(axis=1)
        
        pd_tmp_2020=pd.DataFrame(multiplier_total_2020.T,columns=[i])
        multiplier_2020=pd.concat([multiplier_2020,pd_tmp_2020],axis=1)
        
        pd_tmp_2030=pd.DataFrame(multiplier_total_2030.T,columns=[i])
        multiplier_2030=pd.concat([multiplier_2030,pd_tmp_2030],axis=1)
        
        pd_tmp_2040=pd.DataFrame(multiplier_total_2040.T,columns=[i])
        multiplier_2040=pd.concat([multiplier_2040,pd_tmp_2040],axis=1)
        
        pd_wage_tmp_2020=pd.DataFrame(wage_total_2020.T,columns=[i])
        wage_2020=pd.concat([wage_2020,pd_wage_tmp_2020],axis=1)
        
        pd_wage_tmp_2030=pd.DataFrame(wage_total_2030.T,columns=[i])
        wage_2030=pd.concat([wage_2030,pd_wage_tmp_2030],axis=1)
        
        pd_wage_tmp_2040=pd.DataFrame(wage_total_2040.T,columns=[i])
        wage_2040=pd.concat([wage_2040,pd_wage_tmp_2040],axis=1)
#multiplier=multiplier.sort_index(by=multiplier.columns[1:],axis=1)
    multiplier_2020.iloc[:,1:]=multiplier_2020.iloc[:,1:]*construction_time.iloc[0,:]
    multiplier_2030.iloc[:,1:]=multiplier_2030.iloc[:,1:]*construction_time.iloc[0,:]
    multiplier_2040.iloc[:,1:]=multiplier_2040.iloc[:,1:]*construction_time.iloc[0,:]
    
    multiplier_2020.to_excel('input_output_multiplier/multiplier_operation_2020_'+case+'.xlsx',index=False)
    multiplier_2030.to_excel('input_output_multiplier/multiplier_operation_2030_'+case+'.xlsx',index=False)
    multiplier_2040.to_excel('input_output_multiplier/multiplier_operation_2040_'+case+'.xlsx',index=False)
    
    wage_2020.to_excel('input_output_multiplier/wage_operation_2020_'+case+'.xlsx',index=False)
    wage_2030.to_excel('input_output_multiplier/wage_operation_2030_'+case+'.xlsx',index=False)
    wage_2040.to_excel('input_output_multiplier/wage_operation_2040_'+case+'.xlsx',index=False)

    #total_2030=multiplier_2030.iloc[:,1:].to_numpy()+OM_multiplier_2030.iloc[:,1:].to_numpy()
    #total_2030=pd.DataFrame(total_2030,columns=multiplier_2030.columns[1:])
    #total_2030['total']=total_2030.sum(axis=1)
    
    #total_2040=pd.concat([multiplier_2030['Province'],total_2030],axis=1)
    #total_2040.to_excel('total_2030'+case+'.xlsx',index=False)

    #total_2040=multiplier_2040.iloc[:,1:].to_numpy()+OM_multiplier_2040.iloc[:,1:].to_numpy()
    #total_2040=pd.DataFrame(total_2040,columns=multiplier_2040.columns[1:])
    #total_2040['total']=total_2040.sum(axis=1)
    
    #total_2040=pd.concat([multiplier_2040['Province'],total_2040],axis=1)
    #total_2040.to_excel('total_2040'+case+'.xlsx',index=False)