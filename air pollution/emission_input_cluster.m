clear

coal=zeros(3*6,3);
period=[2020,2025,2030,2035,2040];

path_share='H:\electricity modeling\data\';
scenario={'BAU_LBNL_5period','2C_LBNL_5period','1p5C_LBNL_5period'};
          %'3period_NDC_high','3period_2C_high','3period_1p5C_high' };

heat_rate=readtable('C:\Program Files\GRIDPATH\db\csvs_plexos_new_china\raw_data\all_projects.csv','TreatAsEmpty',{'.'});
coal_power_plant=heat_rate((heat_rate.capacity_group=="group_coal")&(heat_rate.gen_dbid=="existing"),:);

cluster=readtable('C:\Program Files\GRIDPATH\db\csvs_plexos_new_china\raw_data\cluster.csv');

plant_original=unique(coal_power_plant.project);
search=readtable('output\manual_search.xlsx');

coordinates=search_location(plant_original,search);

lat_long=table(plant_original,coordinates(:,1),coordinates(:,2),'VariableNames',{'project','lat','lon'});
%writetable(lat_long,'output/search.xlsx');
coal_power_plant=join(coal_power_plant,lat_long);
coal_power_plant.Properties.VariableNames{'gen_load_zone'}='load_zone';

%load basemap
file=dir('inmapv161_China\China\input\emis\20191217\meic_ground_annual_2017_nocoalpower_layer*.shp');
SO2=0;
NOx=0;
PM25=0;

for i=1:2:length(file)
  folder=file(i).folder;
  path=strcat(folder,'\',file(i).name);
  layer=shaperead(path);
  SO2=SO2+[layer.SOx];
  NOx=NOx+[layer.NOx]; 
  PM25=PM25+[layer.PM2_5];
end
X=[layer.X];
Y=[layer.Y];

%create a new emission inventory for natural gas
gas_layer1_base=shaperead('inmapv161_China\China\input\emis\20191217\meic_ground_annual_2017_nocoalpower_layer1.shp');
gas_layer2_base=shaperead('inmapv161_China\China\input\emis\20191217\meic_ground_annual_2017_nocoalpower_layer3.shp');
gas_layer3_base=shaperead('inmapv161_China\China\input\emis\20191217\meic_ground_annual_2017_nocoalpower_layer5.shp');

gas_layer_base={gas_layer1_base,gas_layer2_base,gas_layer3_base};
%layer2: 244m
%layer3: 317m

province=shaperead('CHN_adm1.shp');


for k=1:length(scenario)
 
  data_path = [path_share,scenario{k},'\results\dispatch_all.csv'];
  data=readtable(data_path);
  
  data_capacity_path=[path_share,scenario{k},'\results\capacity_all.csv'];
  data_capacity=readtable(data_capacity_path);
  
  data_summary=grpstats(data,{'project','load_zone','period'},'mean','DataVars',{'power_mw'});
  cluster_plant=join(data_summary,cluster);
  cluster_plant=join(cluster_plant,data_capacity,'Keys',{'project','period'},'RightVariables','capacity_mw');
  
  fossil_fuel=cluster_plant(ismember(cluster_plant.capacity_group,{'group_coal'})&cluster_plant.gen_dbid=="existing",:);
  %fossil_fuel2=grpstats(fossil_fuel,{'load_zone','technology','period'},'sum','DataVars',{'mean_power_mw','capacity'});
  %fossil_fuel2.factor=fossil_fuel2.sum_mean_power_mw./fossil_fuel2.sum_capacity;

  fossil_fuel_total=cluster_plant(ismember(cluster_plant.capacity_group,{'group_coal'}),:);
  fossil_fuel_total2=grpstats(fossil_fuel_total,{'load_zone','period'},'sum','DataVars',{'mean_power_mw','capacity_mw'});
  %adjust existing capacity to total capacity
  fossil_fuel3=grpstats(fossil_fuel,{'load_zone','period'},'sum','DataVars',{'mean_power_mw','capacity'});
  fossil_fuel3.adjust=fossil_fuel_total2.sum_capacity_mw./fossil_fuel3.sum_capacity;
  fossil_fuel3.adjust(isnan(fossil_fuel3.adjust)==1)=1;
  %calculate capacity factor
  fossil_fuel2=grpstats(fossil_fuel_total,{'load_zone','technology','period'},'sum','DataVars',{'mean_power_mw','capacity_mw'});
  fossil_fuel2.factor=fossil_fuel2.sum_mean_power_mw./fossil_fuel2.sum_capacity_mw;
  
  fossil_fuel2=join(fossil_fuel2,fossil_fuel3,'Keys',{'load_zone','period'},'RightVariables',{'adjust'});
  %fossil_fuel2.sum_capacity=fossil_fuel2.sum_capacity.*fossil_fuel2.adjust;
  
for j=1:length(period)
    coal_power=coal_power_plant;
    year=period(j);
    fossil_fuel_tmp=fossil_fuel2(fossil_fuel2.period==year,:);

    for i=1:length(fossil_fuel_tmp.load_zone)
        index=coal_power.technology==string(fossil_fuel_tmp.technology(i)) & coal_power.load_zone==string(fossil_fuel_tmp.load_zone(i));
        coal_power.mean_power_mw(index)=coal_power.gen_capacity_limit_mw(index)*fossil_fuel_tmp.factor(i)*fossil_fuel_tmp.adjust(i);
        coal_power.gen_capacity_limit_mw(index)=coal_power.gen_capacity_limit_mw(index)*fossil_fuel_tmp.adjust(i);
    end

%%
%coal
    power_coal=coal_power;

%the transition,new and special emission limit mg/m3
    limit=[50,400,450     %old standard
           30,200,100     %existing power plants built before 2012
           30,100,100     %new power plants built after 2012
            20,50,100
            10,35,50];    %special limit for the controlled areas



%volume of smoke gas
% format: [capacity in MW, smoke gas in (m3/ton fuel)]
volume=[99999,8271 
        750,10150
        450,9713
        250,9305
        150,8178];

%calculate PM25 emission factor    
TSP_parameter=[9.23,8.76
               9.2,9.33
               9.21,11.13
               9.33,7.77
               9.31,9.18];


ash_content=26.8; %High-resolution inventory of technologies, activities, and emissions of coal-fired power plants in China from 1990 to 2010
                  %Weighted average of coal production and ash content

%Fabric filter and ESP
efficiency=[
            99.9 99 96         %ESP field
            99.98 99.9 99     %Fabric filter     
            ];       
 
%efficiency=[99.5 97 92.5           %ESP field
%            99.95 99.7 99.3];       %Fabric filter


%20908kJ/ kg ton raw coal    China energy statistics yearbook
ton_GJ=20.908; %GJ/ton

%mmbtu to GJ  1.055 GJ/mmbtu
ton_mmbut=ton_GJ/1.055;

%pm25 fraction in tsp
tsp_pm_mass_hardcoal_50MW=0.06;%for coal power plant, hard coal
tsp_pm_mass_browncoal_50MW=0.1;
tsp_pm_mass_coal_less_50MW=0.14;
tsp_pm_mass_gas=1;
tsp_pm_mass_IGCC=0.625;

PM_fraction_50=[0.77 0.17 0.06];%hard coal
PM_fraction_less_50=[0.63 0.23 0.14];%hard coal


coal_emission = generate_coal_shape(limit,volume,TSP_parameter,ash_content,PM_fraction_50,PM_fraction_less_50,efficiency,power_coal,year);

coal((k-1)*length(period)+j,1)=sum([coal_emission.SOx]);
coal((k-1)*length(period)+j,2)=sum([coal_emission.NOx]);
coal((k-1)*length(period)+j,3)=sum([coal_emission.PM2_5]);


path_write=['emission inventory/',int2str(year)];
shapewrite(coal_emission, strcat(path_write,'/coal_power_',scenario{k},'_',string(year),'.shp'));

%%
%natural gas

power_gas=cluster_plant(cluster_plant.capacity_group=="group_gas" & cluster_plant.period==year,:);

limit=[5,35,50];

volume_gas=24.55;%m3/m3 gas

PM_gas_fraction=[0.15 0.25 0.6];%

unabated=[30 70.7 9820];%mg/m3


[gas_emission_layer1,gas_emission_layer2,gas_emission_layer3]...
 =generate_gas_shape(limit,volume_gas, unabated,X,Y,SO2,NOx,PM25,province,power_gas,gas_layer_base);
sum([gas_emission_layer1.PM2_5])+sum([gas_emission_layer2.PM2_5])+sum([gas_emission_layer3.PM2_5])

path_write=['emission inventory/',int2str(year)];   
shapewrite(gas_emission_layer1, strcat(path_write,'/gas_power_layer1_',scenario{k},'_',string(year),'.shp'));
shapewrite(gas_emission_layer2, strcat(path_write,'/gas_power_layer2_',scenario{k},'_',string(year),'.shp'));
shapewrite(gas_emission_layer3, strcat(path_write,'/gas_power_layer3_',scenario{k},'_',string(year),'.shp'));
end
end