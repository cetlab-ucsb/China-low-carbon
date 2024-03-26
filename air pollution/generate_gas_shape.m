function [gas_emission_layer1,gas_emission_layer2,gas_emission_layer3]...
=generate_gas_shape(limit,volume_gas, unabated,X,Y,SO2,NOx,PM25,province,power_gas,gas_layer_base)


emiss_factor=limit*volume_gas/10^9; %ton/m3 gas

%m3_mmbtu   36,643.11 btu
m3_mmbtu=0.0366;  %mmbtu/m3
%remove_rate=1-emiss_factor*10^9./unabated;

%row=height(power_gas);

p=power_gas;
power=p.mean_power_mw;
heat=p.gen_full_load_heat_rate;
%capacity=p.gen_capacity_limit_mw;
region_tmp=p.load_zone;
gas_annual=power*8760.*heat; %mmbtu
        
nox_tmp=gas_annual*emiss_factor(3)/m3_mmbtu; 
        
pm_tmp=gas_annual*unabated(1)/10^9/m3_mmbtu;

so2_tmp=gas_annual*unabated(2)/10^9/m3_mmbtu;
       
gas_table=table(region_tmp,so2_tmp,nox_tmp,pm_tmp,...
                'VariableNames',{'region','so2','nox','pm'});
gas_table_region=grpstats(gas_table,'region','sum');


x_re=transpose(reshape(X,[5,length(X)/5]));
y_re=transpose(reshape(Y,[5,length(Y)/5]));

x_center=mean(x_re,2,'omitnan');
y_center=mean(y_re,2,'omitnan');

province_SO2=zeros(length(province),1);
province_NOx=zeros(length(province),1);
province_PM=zeros(length(province),1);
province_in=zeros(length(x_center),length(province));;

for i=1:length(province)
    boundary_x=province(i).X;
    boundary_y=province(i).Y;
    in=inpolygon(x_center,y_center,boundary_x,boundary_y);
    province_SO2(i)=sum(SO2(in));
    province_NOx(i)=sum(NOx(in));
    province_PM(i)=sum(PM25(in));
    province_in(:,i)=in;
    i
end

sum(province_SO2)
sum(so2_tmp)
sum(province_PM)
sum(pm_tmp)
sum(province_NOx)
sum(nox_tmp)

gas_table_region2=gas_table_region;
if ismember({'East_Inner_Mongolia','West_Inner_Mongolia'},gas_table_region2.region)
  gas_table_region2{end+1,2:end}=gas_table_region2{gas_table_region2.region=="East_Inner_Mongolia",2:end}+...
                           gas_table_region2{gas_table_region2.region=="West_Inner_Mongolia",2:end};

  gas_table_region2.region{end}='Nei_Mongol';

  gas_table_region2.Properties.RowNames{end}='Inner_Mongolia';

  gas_table_region2(gas_table_region2.region=="West_Inner_Mongolia",:)=[];
  gas_table_region2(gas_table_region2.region=="East_Inner_Mongolia",:)=[];
end
if ismember('Tibet',gas_table_region2.region)
    gas_table_region2(gas_table_region2.region=="Tibet",'region')={'Xizang'};
end 

so2_real=zeros(length(province_SO2),1);
nox_real=zeros(length(province_SO2),1);
pm_real=zeros(length(province_SO2),1);

for i=1:length(province_SO2)
    region_tmp=province(i).NAME_1;
    id=ismember(gas_table_region2.region,region_tmp);
    if sum(id)==0
       so2_real(i)=0;
       nox_real(i)=0;
       pm_real(i)=0;
       continue
    end
    so2_real(i)=gas_table_region2.sum_so2(id);
    nox_real(i)=gas_table_region2.sum_nox(id);
    pm_real(i)=gas_table_region2.sum_pm(id);
end

scale_SO2_ratio=so2_real./province_SO2;
scale_NOx_ratio=nox_real./province_NOx;
scale_PM_ratio=pm_real./province_PM;


province_scale_ratio=zeros(3,length(x_center));

for i=1:length(province)
    province_scale_ratio(1,logical(province_in(:,i)))=scale_SO2_ratio(i);
    province_scale_ratio(2,logical(province_in(:,i)))=scale_NOx_ratio(i);
    province_scale_ratio(3,logical(province_in(:,i)))=scale_PM_ratio(i);
end

for i=1:length(x_center)
    for j=1:3
     gas_layer_base{j}(i).SOx=gas_layer_base{j}(i).SOx*province_scale_ratio(1,i);
     gas_layer_base{j}(i).NOx=gas_layer_base{j}(i).NOx*province_scale_ratio(2,i);
     gas_layer_base{j}(i).PM2_5=gas_layer_base{j}(i).PM2_5*province_scale_ratio(3,i);
    end
end
gas_emission_layer1=gas_layer_base{1};
gas_emission_layer2=gas_layer_base{2};
gas_emission_layer3=gas_layer_base{3};
[gas_emission_layer2.Height1]=deal(244);
[gas_emission_layer3.Height1]=deal(317);
end