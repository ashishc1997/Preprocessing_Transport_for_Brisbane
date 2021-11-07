# %%
import numpy as np
import pandas as pd
import os
cur_path = os.getcwd()

# %%
#demand data is the OD data from the translink website (Hard coded for the November month of 2020)
demand_data_original = pd.read_csv(cur_path+'\\Demand Data\\demand_nov2019.csv',header=0,sep=',',dtype={'route':'str','origin_stop':'str','destination_stop':'str'})
#There are some routes that are under brisbane transport but are serving in the gold cost region so first removing those from the data set as the study are is of Brisbane city
route_in_gold_cost = ['700','704','710','713','715','718','722','731','735','736','740','746','748','760','767']
demand_data_filtered = demand_data_original.drop(demand_data_original.loc[demand_data_original.route.isin(route_in_gold_cost)].index)
#Now there are some routes that are served by hornibrook and Transport for Brisbane together we need to consider them as they are served by by Transport for Brisbane only (an assumption based on lack of field knowledge)
route_by_hornibrook = ['101','102','103','122','310','311','322','313','314','326','327']
for row in demand_data_filtered.loc[demand_data_filtered.route.isin(route_by_hornibrook)].index:
    demand_data_filtered.loc[row,'operator'] = 'Transport for Brisbane'
#Now as the paper tickets have no record of destination location, removing them from the data
demand_data_filtered = demand_data_filtered.loc[demand_data_filtered['ticket_type']!='Paper']
#Now we also do not wish for the weekend data too, hence removing that from the data
demand_data_filtered = demand_data_filtered.loc[demand_data_filtered['time']!='Weekend']
#Finally we are only looking for transport for brisbane records hence only keeping that operator
demand_data_filtered = demand_data_filtered.loc[demand_data_filtered['operator']=='Transport for Brisbane']

#####################################################################################################################
#now we also need to go into static data part to see how many of the route that we have in deamand data are actually recorded over there, without the static data analysis cannot be completed.
routes_original = pd.read_csv(cur_path+'\\Static_Nov_2019\\routes.txt',sep = ',',header = 0, dtype={'route_id':'str','route_short_name':'str'})
#now taking all the routes from demand data and finding them here in static data
routes_filtered = routes_original.loc[routes_original.route_short_name.isin(demand_data_filtered['route'])]
#There were some routes that were opearted by hornibrook and tranport for brisbane and they were considered as to be operarted only by transport for brisban, accrodingly doing the necessary changes in static data files
#creating a list whose route id indicate route not being BT route
route_id_not_BT = []
for i in routes_filtered['route_id']:
    a = i.split('-')
    if a[1] != '1354':
        route_id_not_BT.append(i)
#now we need to find these route and modify the DF accordingl
for row in routes_filtered.loc[routes_filtered.route_id.isin(route_id_not_BT)].index:
    a = routes_filtered.loc[row]
    route_id = a[0]
    b = route_id.split('-')
    #print(b[0])
    routes_filtered.loc[row,'route_id']=b[0]+'-'+'1354'
    b.clear()
routes_filtered=routes_filtered.drop_duplicates(subset=['route_id','route_short_name'])
#This is all the filtering needed in the routes file for static data, hence writing this file
routes_filtered.to_csv(cur_path+'\\Static_fil\\routes_fil.csv',index=False)
#Filtering the demand data based on the record found in static data routes file
demand_data_filtered = demand_data_filtered.loc[demand_data_filtered.route.isin(routes_filtered['route_short_name'])]
#Summary of demand data we will be using for the analysis
#number of routes
print('Number of routes taken in consideration for analysis:')
print(demand_data_filtered.route.nunique())
#number of stops considered for analysis
all_stops = list(demand_data_filtered.destination_stop.unique())
for i in list(demand_data_filtered.origin_stop.unique()):
    if i not in all_stops:
        all_stops.append(i)
print('Number of stops in the network are:')
print(len(all_stops))
#number of ppl using the network considered for the analysis
print('Number of trips made by people that are considered for analysis are:')
print(demand_data_filtered['quantity'].sum())
#Now that we have looked in routes df, let us look in trips df and make necessary changes there
trips_original = pd.read_csv(cur_path+'\\Static_Nov_2019\\trips.txt',header=0,sep=',')
#in the routes df we made some changes in route_id we need to do the same changes here too.
for row in trips_original.loc[trips_original.route_id.isin(route_id_not_BT)].index:
    a = trips_original.loc[row]
    route_id = a[0]
    b = route_id.split('-')
    #print(b[0])
    trips_original.loc[row,'route_id']=b[0]+'-'+'1354'
    b.clear()
#Getting only those routes that are in routes df
trips_filtered = trips_original.loc[trips_original.route_id.isin(routes_filtered['route_id'])]
#Now we can see there are some service id that need to be changed according to the day they serve we need to replace them BT services
#the service 'HTM 19_20-HTM_FUL-Weekday-00' and 'SWT 19_20-SWT_FUL-Weekday-00' has to be replaced by brisbane services as we are assuming only BT serves these routes and no other agnecy
#Now from all the BT services the services we will be considering are : <br>
#BT 19_20-AUG_HUNG-Weekday-01<br>
#BT 19_20-AUG_HUNG-Weekday-01-0000100<br>
#BT 19_20-AUG_HUNG-Weekday-01-1000000<br>
#BT 19_20-AUG_HUNG-Weekday-01-0111100<br>
#The HTM 19_20-HTM_FUL-Weekday-00 and SWT 19_20-SWT_FUL-Weekday-00 is replaced by BT 19_20-AUG_HUNG-Weekday-01 based on the calndar data
for row in trips_filtered.loc[trips_filtered.service_id=='HTM 19_20-HTM_FUL-Weekday-00'].index:
    trips_filtered.loc[row,'service_id'] = 'BT 19_20-AUG_HUNG-Weekday-01'
for row in trips_filtered.loc[trips_filtered.service_id=='SWT 19_20-SWT_FUL-Weekday-00'].index:
    trips_filtered.loc[row,'service_id'] = 'BT 19_20-AUG_HUNG-Weekday-01'
#now only filtering the required services from the trips df
req_service_id = ['BT 19_20-AUG_HUNG-Weekday-01','BT 19_20-AUG_HUNG-Weekday-01-0000100','BT 19_20-AUG_HUNG-Weekday-01-1000000','BT 19_20-AUG_HUNG-Weekday-01-0111100']
trips_filtered = trips_filtered.loc[trips_filtered.service_id.isin(req_service_id)]
#Now as we can see there are a lot of trips that are made according to time and all. But for our interest we want only one trip data in outbound direction and one trip in the inbound direction. And not only the trip id but also we want to know the stops and number of stops on that trip.
#Hence these are not the trips that we would need. We have to go to stop time data, there we need to first divide the dataframe in 4 dataframe according to time slot. Now from each time slot we need to pick up the trip that serves the most number of stops one in outbound and one in bound. <br> Then we will have a time slot in which there will be route and each route there would be two trips one in outbound and one in inbound and for those trips we would have a set of stops that it serves.<br> With this we will get the Sj value that we need for our analysis.
#Lets create a disctionary with route as key and trip_id and direction of trip as value
route_tripid_direc = dict()
for route in trips_filtered.route_id.unique():
    trip_list = []
    for row in trips_filtered.loc[trips_filtered.route_id==route].index:
        a = trips_filtered.loc[row]
        trip_list.append([a[2],a[4]])
    route_tripid_direc[route] = trip_list

stop_time_df = pd.read_csv(cur_path+'\\Static_Nov_2019\\stop_times.txt',sep=',',header=0,dtype={'stop_id':'str'})
#Now in the stop times we have details of trips and how these trips are carried out in the network. We only need the trips that are in our trips filtered df. So filtering the trips
stop_time_filtered = stop_time_df.loc[stop_time_df.trip_id.isin(trips_filtered['trip_id'])].reset_index()
stop_time_filtered.drop(columns=['index'],inplace=True)
#Now we know from the map that route 599 and 598 being a single long route there are many trips that are shown in static data, we need to combine these trips. Hence for that it would be convinent if we add a columns with route information in this data frame
stop_time_filtered = pd.merge(stop_time_filtered,trips_filtered[['trip_id','route_id']],on=['trip_id'])
#First we will split the data frame in time slot wise. For that we need to cahnge arrival time and departure times. There are some instances where arrival time or departure time are more than 24. So we will bring them down to 23.59.59
for row in stop_time_filtered.index:
    a = stop_time_filtered.loc[row]
    arrival = a[1].split(':')
    if int(arrival[0])>=24:
        a[1] = '23:59:59'
        stop_time_filtered.loc[row,'arrival_time'] = a[1]
    departure = a[2].split(':')
    if int(departure[0])>=24:
        a[2] = '23:59:59'
        stop_time_filtered.loc[row,'departure_time'] = a[2]
stop_time_filtered['arrival_time'] = pd.to_datetime(stop_time_filtered['arrival_time'],format='%H:%M:%S').dt.time
stop_time_filtered['departure_time'] = pd.to_datetime(stop_time_filtered['departure_time'],format='%H:%M:%S').dt.time
# Let us first see at route 598. <br>
# The route 598 is divided int0 three main trips the first and last stop of these trips are as follows <br>
# This data is obtained by manually checking the map of the routes <br>
# Trip A - 3955-2004 <br>
# Trip B - 2204 - 6515 <br>
# Trip C - 16505 - 3979 <br>
# It would be better if we create 3 routes. We need to change the demand data and the dictionary containg the information regarding the routes and the trips and trip direction
# In the following cell I have deletd the trips that do not have 3955, 2204, 16505 as their origin stop
to_drop_trip_id_598 = stop_time_filtered.loc[(stop_time_filtered.route_id=='598-1354')&(stop_time_filtered.stop_sequence==1)&(~stop_time_filtered.stop_id.isin(['3955','2204','16505']))]['trip_id']
stop_time_filtered.drop(stop_time_filtered.loc[stop_time_filtered.trip_id.isin(to_drop_trip_id_598)].index,inplace=True)
#Now we will rename the route 599 based on origin stop, if starts from 3955 it will be 598A-1354 if from 2204 then it will be 598B-1354 and if from 16505 it will be 598C-1354.
for row in stop_time_filtered.loc[stop_time_filtered.route_id=='598-1354'].index:
    a = stop_time_filtered.loc[row]
    if a[3] == '3955':
        stop_time_filtered.loc[(stop_time_filtered.trip_id==a[0]),'route_id'] = '598A-1354'
    if a[3] == '2204':
        stop_time_filtered.loc[(stop_time_filtered.trip_id==a[0]),'route_id'] = '598B-1354'
    if a[3] == '16505':
        stop_time_filtered.loc[(stop_time_filtered.trip_id==a[0]),'route_id'] = '598C-1354'
stops_598_A = list(stop_time_filtered.loc[stop_time_filtered.route_id=='598A-1354']['stop_id'].unique())
stops_598_B = list(stop_time_filtered.loc[stop_time_filtered.route_id=='598B-1354']['stop_id'].unique())
stops_598_C = list(stop_time_filtered.loc[stop_time_filtered.route_id=='598C-1354']['stop_id'].unique())
#Now that route 598 is take care of in trips file, we will make the necessary changes in routes trips dicrionary
temp_list = []
for row in stop_time_filtered.loc[stop_time_filtered.route_id=='598A-1354'].index:
    a = stop_time_filtered.loc[row]
    #a[0] is the trip id
    b = [a[0],1]
    #as the direction of route is only anticlockwise
    if b not in temp_list:
        temp_list.append(b)
    
route_tripid_direc['598A-1354'] = temp_list
    
temp_list = []
for row in stop_time_filtered.loc[stop_time_filtered.route_id=='598B-1354'].index:
    a = stop_time_filtered.loc[row]
    #a[0] is the trip id
    b = [a[0],1]
    #as the direction of route is only anticlockwise
    if b not in temp_list:
        temp_list.append(b)
    
route_tripid_direc['598B-1354'] = temp_list
    
temp_list = []
for row in stop_time_filtered.loc[stop_time_filtered.route_id=='598C-1354'].index:
    a = stop_time_filtered.loc[row]
    #a[0] is the trip id
    b = [a[0],1]
    #as the direction of route is only anticlockwise
    if b not in temp_list:
        temp_list.append(b)
    
route_tripid_direc['598C-1354'] = temp_list
#removing the origial route 598 from the dictionary 
route_tripid_direc.pop('598-1354')
#Now changing the demand data according to the new name of route 598
for row in demand_data_filtered.loc[demand_data_filtered.route=='598'].index:
    a = demand_data_filtered.loc[row]
    if a[6] in stops_598_A:
        demand_data_filtered.loc[row,'route'] = '598A'
    if a[6] in stops_598_B:
        demand_data_filtered.loc[row,'route'] = '598B'
    if a[6] in stops_598_C:
        demand_data_filtered.loc[row,'route'] = '598C'
# Now that we are done with route 598 looking at route 599 <br>
# The route 599 is divided into 3 three main trips the first and last stop of these trips are as follows <br>
# This data is obtained by manually checking the map of the routes <br>
# Trip A - 3996-2204 <br>
# Trip B - 2204 - 16504 <br>
# Trip C - 16504 - 3996 <br>
# It would be better if we create 3 routes. We need to change the demand data and the dictionary containg the information regarding the routes and the trips and trip direction
# In the following cell I have deletd the trips that do not have 3955, 2204, 16505 as their origin stop
to_drop_trip_id_599 = stop_time_filtered.loc[(stop_time_filtered.route_id=='599-1354')&(stop_time_filtered.stop_sequence==1)&(~stop_time_filtered.stop_id.isin(['3996','2204','16504']))]['trip_id']
stop_time_filtered.drop(stop_time_filtered.loc[stop_time_filtered.trip_id.isin(to_drop_trip_id_599)].index,inplace=True)
#Now we will rename the route 599 based on origin stop, if starts from 3996 it will be 599A-1354 if from 2204 then it will be 599B-1354 and if from 16504 it will be 599C-1354.
for row in stop_time_filtered.loc[stop_time_filtered.route_id=='599-1354'].index:
    a = stop_time_filtered.loc[row]
    if a[3] == '3996':
        stop_time_filtered.loc[(stop_time_filtered.trip_id==a[0]),'route_id'] = '599A-1354'
    if a[3] == '2204':
        stop_time_filtered.loc[(stop_time_filtered.trip_id==a[0]),'route_id'] = '599B-1354'
    if a[3] == '16504':
        stop_time_filtered.loc[(stop_time_filtered.trip_id==a[0]),'route_id'] = '599C-1354'
stops_599_A = list(stop_time_filtered.loc[stop_time_filtered.route_id=='599A-1354']['stop_id'].unique())
stops_599_B = list(stop_time_filtered.loc[stop_time_filtered.route_id=='599B-1354']['stop_id'].unique())
stops_599_C = list(stop_time_filtered.loc[stop_time_filtered.route_id=='599C-1354']['stop_id'].unique())
#Now that route 599 is take care of in trips file, we will make the necessary changes in routes trips dicrionary
temp_list = []
for row in stop_time_filtered.loc[stop_time_filtered.route_id=='599A-1354'].index:
    a = stop_time_filtered.loc[row]
    #a[0] is the trip id
    b = [a[0],0]
    #as the direction of route is only anticlockwise
    if b not in temp_list:
        temp_list.append(b)
    
route_tripid_direc['599A-1354'] = temp_list
temp_list = []
for row in stop_time_filtered.loc[stop_time_filtered.route_id=='599B-1354'].index:
    a = stop_time_filtered.loc[row]
    #a[0] is the trip id
    b = [a[0],0]
    #as the direction of route is only anticlockwise
    if b not in temp_list:
        temp_list.append(b)
    
route_tripid_direc['599B-1354'] = temp_list
temp_list = []
for row in stop_time_filtered.loc[stop_time_filtered.route_id=='599C-1354'].index:
    a = stop_time_filtered.loc[row]
    #a[0] is the trip id
    b = [a[0],0]
    #as the direction of route is only anticlockwise
    if b not in temp_list:
        temp_list.append(b)
    
route_tripid_direc['599C-1354'] = temp_list
#removing the origial route 599 from the dictionary 
route_tripid_direc.pop('599-1354')
#Now changing the demand data according to the new name of route 598
for row in demand_data_filtered.loc[demand_data_filtered.route=='599'].index:
    a = demand_data_filtered.loc[row]
    if a[6] in stops_599_A:
        demand_data_filtered.loc[row,'route'] = '599A'
    if a[6] in stops_599_B:
        demand_data_filtered.loc[row,'route'] = '599B'
    if a[6] in stops_599_C:
        demand_data_filtered.loc[row,'route'] = '599C'

####################################################################################################################################################################
# Creating lists of trip_id according to the time they serve in <br>
# Slot 1 : 00.00 - 8.29.59 <br>
# Slot 2 : 8.30.00 - 14.59.59  <br>
# Slot 3 : 15.00.00 -18.59.59 <br>
# Slot 4 : 19.00.00 - 23.59.59 <br>
trip_slot_1 = []
trip_slot_2 = []
trip_slot_3 = []
trip_slot_4 = []
for row in stop_time_filtered.loc[stop_time_filtered.stop_sequence==1].index:
    a = stop_time_filtered.loc[row]
    #print(a[4])
    if a[1]<= pd.to_datetime('08:29:59').time():
        trip_slot_1.append(a[0])
    elif (a[1]>= pd.to_datetime('08:30:00').time()) and (a[1] <= pd.to_datetime('14:59:59').time()):
        trip_slot_2.append(a[0])
    elif (a[1]>= pd.to_datetime('15:00:00').time()) and (a[1] <= pd.to_datetime('18:59:59').time()):
        trip_slot_3.append(a[0])
    elif (a[2]>= pd.to_datetime('19:00:00').time()) and (a[2] <= pd.to_datetime('23:59:59').time()):
        trip_slot_4.append(a[0])
#Now that we have trips in 4 time slots we can create 4 different stop time data frames
stop_time_slot_1 = stop_time_filtered.loc[stop_time_filtered.trip_id.isin(trip_slot_1)].reset_index()
stop_time_slot_1.drop(columns=['index'],inplace=True)
stop_time_slot_2 = stop_time_filtered.loc[stop_time_filtered.trip_id.isin(trip_slot_2)].reset_index()
stop_time_slot_2.drop(columns=['index'],inplace=True)
stop_time_slot_3 = stop_time_filtered.loc[stop_time_filtered.trip_id.isin(trip_slot_3)].reset_index()
stop_time_slot_3.drop(columns=['index'],inplace=True)
stop_time_slot_4 = stop_time_filtered.loc[stop_time_filtered.trip_id.isin(trip_slot_4)].reset_index()
stop_time_slot_4.drop(columns=['index'],inplace=True)
#Now that we have stop time in 4 slots, we will make the route trip direction dictionary divided into 4 slots
def slot_wise_ro_tr_di(all_route_trip_di_dict,stop_time_slot):
    route_tripid_direc_slot = dict()
    all_trip_sl = list(stop_time_slot['trip_id'].unique())
    for route in all_route_trip_di_dict.keys():
        new_info = []
        info_trip_direc = all_route_trip_di_dict[route]
        for i in info_trip_direc:
            if i[0] in all_trip_sl:
                new_info.append(i)
        if len(new_info)>0:
            route_tripid_direc_slot[route] = new_info
    return route_tripid_direc_slot

route_tripid_direc_slot1 = slot_wise_ro_tr_di(route_tripid_direc,stop_time_slot_1)
route_tripid_direc_slot2 = slot_wise_ro_tr_di(route_tripid_direc,stop_time_slot_2)
route_tripid_direc_slot3 = slot_wise_ro_tr_di(route_tripid_direc,stop_time_slot_3)
route_tripid_direc_slot4 = slot_wise_ro_tr_di(route_tripid_direc,stop_time_slot_4)
# Now we have route information, trips that run on that route and the direction of trips that run on the route information with us. Now we would like to create a dictionary that has route as key and a single trip in each direction and the stops that trips goes through.<br> The catch here being there are many trips and if we find the unique trips there might be cases where the route has a single unique trip but in some cases the trips are not half made and all. So we will take only those trips that are longest in nature.
#  And all this analysis would be time wise as we have separated the data according to the time slots now.
def create_ro_tr_di_st(dict_ro_tr_di,df_stop_time):
    route_trip_direc_stops_slot = dict()
    for route in dict_ro_tr_di.keys():
        if route in df_stop_time['route_id'].unique():
            #print(route)
            trip_direc_stop = []
            info_trip_direc = dict_ro_tr_di[route]
            directions= []
            for k in info_trip_direc:
                if k[1] not in directions:
                    directions.append(k[1])
            if len(directions) == 2:
                trip_direc_stop = []
                length_0 = 0
                trip_direc_stop_0 = []
                for i in info_trip_direc:
                #now will check if outbount or inbound
                    if i[1] == 0:
                        length_iter = len(df_stop_time.loc[df_stop_time.trip_id==i[0]])
                        if length_iter>length_0:
                            stops_in_trip = list(df_stop_time.loc[df_stop_time.trip_id==i[0]]['stop_id'])
                            trip_id = i[0]
                trip_direc_stop_0.append(trip_id)
                trip_direc_stop_0.append(0)
                trip_direc_stop_0.extend(stops_in_trip)
                trip_direc_stop.append(trip_direc_stop_0)
                length_1 = 0
                trip_direc_stop_1 = []
                for i in info_trip_direc:
                    if i[1] == 1:
                        length_iter = len(df_stop_time.loc[df_stop_time.trip_id==i[0]])
                        if length_iter>length_1:
                            stops_in_trip = list(df_stop_time.loc[df_stop_time.trip_id==i[0]]['stop_id'])
                            trip_id = i[0]
                trip_direc_stop_1.append(trip_id)
                trip_direc_stop_1.append(1)
                trip_direc_stop_1.extend(stops_in_trip)
                trip_direc_stop.append(trip_direc_stop_1)
                print(route)

            route_trip_direc_stops_slot[route] = trip_direc_stop

            if len(directions) ==1:
                direction = directions[0]
                trip_direc_stop_any = []
                length_any = 0
                for i in info_trip_direc:
                    length_iter = len(df_stop_time.loc[df_stop_time.trip_id==i[0]])
                    if length_iter>length_any:
                        stops_in_trip = list(df_stop_time.loc[df_stop_time.trip_id==i[0]]['stop_id'])
                        trip_id = i[0]
                trip_direc_stop_any.append(trip_id)
                trip_direc_stop_any.append(direction)
                trip_direc_stop_any.extend(stops_in_trip)
                trip_direc_stop.append(trip_direc_stop_any)
                print(route)
            route_trip_direc_stops_slot[route] = trip_direc_stop
    return route_trip_direc_stops_slot
route_trip_direc_stops_slot1 = create_ro_tr_di_st(route_tripid_direc_slot1,stop_time_slot_1) 
route_trip_direc_stops_slot2 = create_ro_tr_di_st(route_tripid_direc_slot2,stop_time_slot_2)
route_trip_direc_stops_slot3 = create_ro_tr_di_st(route_tripid_direc_slot3,stop_time_slot_3)
route_trip_direc_stops_slot4 = create_ro_tr_di_st(route_tripid_direc_slot4,stop_time_slot_4)

#Writing the newly created deamand data file and writing the route-trip-direc-stop of all 4 slots as a dictionary.
demand_data_filtered.to_csv(cur_path+'\\Demand_fil\\Demand_nov2019_fil.csv',index = False,)
import json
import numpy as np

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)
def new_dict_format(old_dict):
    new_dict = dict()
    for key in old_dict.keys():
        dict1 = dict()
        info = old_dict[key]
        direc_id = str(info[0][1])
        dict1[direc_id] = {
            'trip_id':info[0][0],
            'stop_id':info[0][2:]
        }
        try:
            direc_id = str(info[1][1])
            dict1[direc_id] = {
                'trip_id':info[1][0],
                'stop_id':info[1][2:] 
            }
        except:
            pass
        new_dict[key] = dict1
    return new_dict
ro_tr_di_st_sl1_new = new_dict_format(route_trip_direc_stops_slot1)
ro_tr_di_st_sl2_new = new_dict_format(route_trip_direc_stops_slot2)
ro_tr_di_st_sl3_new = new_dict_format(route_trip_direc_stops_slot3)
ro_tr_di_st_sl4_new = new_dict_format(route_trip_direc_stops_slot4)
with open(cur_path+'\\Static_fil\\ro_tr_di_st_sl1.json','w') as fp:
    json.dump(ro_tr_di_st_sl1_new,fp)
fp.close()

with open(cur_path+'\\Static_fil\\ro_tr_di_st_sl2.json','w') as fp:
    json.dump(ro_tr_di_st_sl2_new,fp,indent=4,cls=NpEncoder)
fp.close()

with open(cur_path+'\\Static_fil\\ro_tr_di_st_sl3.json','w') as fp:
    json.dump(ro_tr_di_st_sl3_new,fp,indent=4,cls=NpEncoder)
fp.close()

with open(cur_path+'\\Static_fil\\ro_tr_di_st_sl4.json','w') as fp:
    json.dump(ro_tr_di_st_sl4_new,fp,indent=4,cls=NpEncoder)
fp.close()
#if the route are to be found out direction wise one can follow the following fuction
def create_routedirec_stop(ro_tr_di_st):
    new_dict = dict()
    for route in ro_tr_di_st.keys():
        for direc in ro_tr_di_st[route].keys():
            for d in direc:
                if d == '0':
                    new_name = route+'_I'
                    new_dict[new_name] = ro_tr_di_st[route][d]['stop_id']
                if d == '1':
                    new_name = route+'_O'
                    new_dict[new_name] = ro_tr_di_st[route][d]['stop_id']
    return new_dict
                    
                    


