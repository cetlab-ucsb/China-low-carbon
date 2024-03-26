function coal_emission = generate_coal_shape(limit,volume,TSP_parameter,ash_content,PM_fraction_50,PM_fraction_less_50,efficiency,power_coal,year)
    
    ton_GJ=20.908; %GJ/ton

    %mmbtu to GJ  1.055 GJ/mmbtu
    ton_mmbtu=ton_GJ/1.055;
    
    emiss_factor_2005=limit(1,:).*volume(:,2)/10^9; %ton/ton coal
    emiss_factor_2011=limit(2,:).*volume(:,2)/10^9; %ton/ton coal
    emiss_factor_2012=limit(3,:).*volume(:,2)/10^9; %ton/ton coal
    emiss_factor_BTH=limit(4,:).*volume(:,2)/10^9; %ton/ton coal
    emiss_factor_2020=limit(5,:).*volume(:,2)/10^9; %ton/ton coal

%removel rate of PM
    TSP_unabated=TSP_parameter(:,1)*ash_content+TSP_parameter(:,2);

    remove_rate_2005=1-emiss_factor_2005(:,1)*1000./TSP_unabated;
    remove_rate_2011=1-emiss_factor_2011(:,1)*1000./TSP_unabated;
    remove_rate_2012=1-emiss_factor_2012(:,1)*1000./TSP_unabated;
    remove_rate_BTH=1-emiss_factor_BTH(:,1)*1000./TSP_unabated;
    remove_rate_2020=1-emiss_factor_2020(:,1)*1000./TSP_unabated;

        
    efficiency_combine=1-(1-efficiency(1,:)/100).*(1-efficiency(2,:)/100);

    efficiency=[efficiency/100
                efficiency_combine];

%emiss_factor(:,1)=TSP_unabated/1000;


%%


    row=height(power_coal);

    pm_temp=zeros(row,1);
    so2_temp=zeros(row,1);
    nox_temp=zeros(row,1);
    tsp_temp=zeros(row,1);
 
    X=zeros(row,1);
    Y=zeros(row,1);

    for i=1:row
        p=power_coal(i,:);
        power=p.mean_power_mw;
        heat=p.gen_full_load_heat_rate;
        heat(isnan(heat)==1)=mean(heat,'omitnan');
        capacity=p.gen_capacity_limit_mw;
        
       if isnan(capacity)==1
        capacity=p.gen_min_build_capacity;
       end
       
       capacity(isnan(capacity)==1)=mean(capacity,'omitnan');
       
        coal_annual=power*8760*heat; %mmbtu
    
        CommissioningDate=p.build_year;
    
       if isnan(CommissioningDate)==1
         CommissioningDate=2020;
       end
       
       if year>=2030
          CommissioningDate=2020;
       end
    %compare TSP efficiency with the standard
        
        capacitycheck=(volume(:,1)-capacity)>0;
        n_tmp=sum(capacitycheck);      
        if capacity>=50
           PM_fraction=PM_fraction_50;%hard coal
        else
           PM_fraction=PM_fraction_less_50;%hard coal
        end
           TSP_efficiency=sum(PM_fraction.*efficiency,2);

        if capacity>=300 | CommissioningDate>=2016 | (contains(['captive','paper','chemical'],p.project,'IgnoreCase',true) & capacity>=100)
           
           standard=5;
          
           so2_temp(i)=coal_annual*limit(standard,2)*volume(n_tmp,2)/10^9/ton_mmbtu;
           nox_temp(i)=coal_annual*limit(standard,3)*volume(n_tmp,2)/10^9/ton_mmbtu; 
           tsp_temp(i)=coal_annual*limit(standard,1)*volume(n_tmp,2)/10^9/ton_mmbtu; 

           operation=remove_rate_2020'./TSP_efficiency;
           judge=max(operation,[],2)<1;
          
          if sum(judge)>0
            n=length(judge)-sum(judge)+1;
            PM25_efficiency=efficiency(n,3)*operation(n,n_tmp);
          else
            PM25_efficiency=efficiency(end,3);
          end
            pm_temp(i)=coal_annual*TSP_unabated(n_tmp)*PM_fraction(3)/1000*(1-PM25_efficiency)/ton_mmbtu;
           
        elseif ismember(p.load_zone,{'Beijing','Hebei','Tianjin','Shanghai','Jiangsu','Zhejiang','Guangdong','Shandong'})
          
           standard=4;
          
           so2_temp(i)=coal_annual*limit(standard,2)*volume(n_tmp,2)/10^9/ton_mmbtu;
           nox_temp(i)=coal_annual*limit(standard,3)*volume(n_tmp,2)/10^9/ton_mmbtu; 
           tsp_temp(i)=coal_annual*limit(standard,1)*volume(n_tmp,2)/10^9/ton_mmbtu; 

           operation=remove_rate_BTH'./TSP_efficiency;
           judge=max(operation,[],2)<1;
          
          if sum(judge)>0
            n=length(judge)-sum(judge)+1;
            PM25_efficiency=efficiency(n,3)*operation(n,n_tmp);
          else
            PM25_efficiency=efficiency(end,3);
          end
            
          pm_temp(i)=coal_annual*TSP_unabated(n_tmp)*PM_fraction(3)/1000*(1-PM25_efficiency)/ton_mmbtu;
        
        
        elseif CommissioningDate<=2011
          
          standard=2;
          
          so2_temp(i)=coal_annual*limit(standard,2)*volume(n_tmp,2)/10^9/ton_mmbtu;
          
          if ismember(p.load_zone,{'Guangxi','Chongqing','Sichuan','Guizhou'})  
            so2_temp(i)=coal_annual*limit(standard,2)*volume(n_tmp,2)/10^9/ton_mmbtu*2;
          end
       
            nox_temp(i)=coal_annual*limit(standard,3)*volume(n_tmp,2)/10^9/ton_mmbtu;
            
          if CommissioningDate<=2003
              nox_temp(i)=coal_annual*limit(standard,3)*volume(n_tmp,2)/10^9/ton_mmbtu*2;
          end
          
          tsp_temp(i)=coal_annual*limit(standard,1)*volume(n_tmp,2)/10^9/ton_mmbtu; 

          operation=remove_rate_2011'./TSP_efficiency;
          judge=max(operation,[],2)<1;

          if sum(judge)>0
            n=length(judge)-sum(judge)+1;
            PM25_efficiency=efficiency(n,3)*operation(n,n_tmp);
          else
            PM25_efficiency=efficiency(end,3);
          end
            
          pm_temp(i)=coal_annual*TSP_unabated(n_tmp)*PM_fraction(3)/1000*(1-PM25_efficiency)/ton_mmbtu;
  
        else      %new standard
          
          standard=3;        
          
          so2_temp(i)=coal_annual*limit(standard,2)*volume(n_tmp,2)/10^9/ton_mmbtu;
          nox_temp(i)=coal_annual*limit(standard,3)*volume(n_tmp,2)/10^9/ton_mmbtu;
          tsp_temp(i)=coal_annual*limit(standard,1)*volume(n_tmp,2)/10^9/ton_mmbtu; 
       
          operation=remove_rate_2012'./TSP_efficiency;
          judge=max(operation,[],2)<1;
          
          if sum(judge)>0
            n=length(judge)-sum(judge)+1;
            PM25_efficiency=efficiency(n,3)*operation(n,n_tmp);
          else
            PM25_efficiency=efficiency(end,3);
          end  
          
          pm_temp(i)=coal_annual*TSP_unabated(n_tmp)*PM_fraction(3)/1000*(1-PM25_efficiency)/ton_mmbtu;
          
        end
        
    
   % pm_temp2=pm_temp;
    %pm_temp(capacity>=50)=pm_temp2(capacity>=50)*PM_fraction_50(3);
    %pm_temp(capacity<50)=pm_temp2(capacity<50)*PM_fraction_less_50(3); 
    
    X(i)=p.lon;
    Y(i)=p.lat;
    end

    dataset=[X,Y,so2_temp,nox_temp,pm_temp];

    dataset(X==0 | isnan(so2_temp)==1,:)=[];

    template=shaperead('inmapv161_China/China/input/emis/20191217/elevated_power_base.shp');

    sum([template.SOx])
    sum(so2_temp,'omit','na')

    sum([template.NOx])
    sum(nox_temp,'omit','na')

    sum([template.PM2_5])
    sum(pm_temp,'omit','na')
    
    sum([template.PM10])
    sum(tsp_temp,'omit','na')

    clear data


    [data1(1:length(dataset)).Geometry]=deal('Point');

    for i=1:length(dataset)
     data1(i).X=dataset(i,1);
     data1(i).Y=dataset(i,2);
     data1(i).SOx=dataset(i,3);
     data1(i).NOx=dataset(i,4);
     data1(i).CO=0;
     data1(i).NH3=0;
     data1(i).VOC=0;
     data1(i).PM2_5=dataset(i,5);
     data1(i).PM10=0;
     data1(i).Height1=120;
     data1(i).Diam=4.7;
     data1(i).Temp=313;
     data1(i).Velocity=6;
    end
   coal_emission=data1;
end