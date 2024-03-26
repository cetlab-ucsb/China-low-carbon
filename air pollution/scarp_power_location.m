clear
files=dir('PLEXOS_gen_files_v20\');
ch=[files.bytes];
files(ch==0,:)=[];
province=cell(length(files),1);
provincename=cell(length(files),1);

for i=1:length(files)
    path=[files(i).folder,'\',files(i).name];
    tmp=readtable(path);
    province{i}=tmp(:,1:37);
    provincename{i}=extractBetween(files(i).name,'_','.csv');
end
clear tmp

lat_lon=cell(length(files),1);
searchlist=cell(length(files),1);

for i=1:length(province)
   plant_original=province{i}.Generator;
   if isempty(plant_original)==1
       i
       continue
   end
  % plant=extractBefore(plant,'_Unit');
   plant=regexp(plant_original,'\S+(station|complex|Station|station-2|Plant|station|station_B)','match');
      
   coordinates=zeros(length(plant),2);
   
   searchlist_tmp=[];
    
  for j=1:length(plant)
     name_tmp=plant{j};
     
     if isempty(name_tmp)==1
        searchlist_tmp=[searchlist_tmp
                        string(plant_original{j})];
         continue
     end
     
     link=['https://www.gem.wiki/',urlencode(name_tmp{1})];
     
     try
     
        web=urlread(link);
     catch
         cooridnates=[nan,nan];
         searchlist_tmp=[searchlist_tmp
                         string(name_tmp)];
         continue
     end
     
        %coord=regexp(web,'<b>Coordinates(:</b>|</b>:) (\d*\.\d*)(,|, )(\d*\.\d*)','match');
            
        coord=regexp(web,'<b>Coordinates+(\S)+(\s*\d*\.\d*)+(\s*.\s*)+(\d*\.\d*)','match');

    % if isempty(coord)==1
    %    coord=regexp(web,'<b>Coordinates:</b> (\d*\.\d*), (\d*\.\d*)','match');
    % end
     
     if isempty(coord)==1
         searchlist_tmp=[searchlist_tmp
                         string(name_tmp)];
         continue
     end
     
     tmp=regexp(coord,'(\d*\.\d*)','match');
     tmp2=tmp{1};
     lat=str2double(tmp2{1});
     lon=str2double(tmp2{2});
     coordinates(j,1)=lat;
     coordinates(j,2)=lon;
  end
     lat_lon{i}=coordinates;
     searchlist{i}=searchlist_tmp;
     i
end


for i=1:length(files)
    table_old=province{i};
    table_new=[table_old array2table(lat_lon{i})];
    table_new.Properties.VariableNames{end-1}='Latitude';
    table_new.Properties.VariableNames{end}='Longitude';
    path=[files(i).folder,'\',files(i).name];
    writetable(table_new,path);
end

delete manual_search.xlsx
for i=1:length(files)
   writematrix(searchlist{i},'manual_search.xlsx','Sheet',string(provincename{i}));
end
