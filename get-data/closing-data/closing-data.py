#!/usr/bin/env python
# coding: utf-8

# In[2]:


#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import bs4
import pandas as pd
from datetime import datetime, timedelta, date, time
from pytz import timezone
import http.client
http.client._MAXHEADERS = 1000


# In[2]:


def GetStartANDEndDateStr():
    NZ_datetime_now = timezone('Pacific/Auckland').localize(datetime.now())
    
    #Start Date
    NZ_start_date = NZ_datetime_now.date() - timedelta(days = 1)
    NZ_start_time = time(7)
    NZ_start_datetime = datetime.combine(NZ_start_date, NZ_start_time)
    
    UTC_start_datetime = NZ_start_datetime.astimezone(timezone('UTC'))
    UTC_start_string = UTC_start_datetime.strftime("%Y-%m-%d"+"T"+"%H:%M:%S")
    
    
    #End Date
    NZ_end_date = NZ_datetime_now.date()
    NZ_end_time = time(6, 59, 59)
    NZ_end_datetime = datetime.combine(NZ_end_date, NZ_end_time)
    
    UTC_end_datetime = NZ_end_datetime.astimezone(timezone('UTC'))
    UTC_end_string = UTC_end_datetime.strftime("%Y-%m-%d"+"T"+"%H:%M:%S")
    
    return UTC_start_string, UTC_end_string


# In[3]:


def GetRaceIds(UTC_start_string, UTC_end_str):
    
    Home_Url = "https://www.odds.com.au/api/web/public/Meetings/getDataByRangeCacheable/?filter=events,regions,meetings&APIKey=65d5a3e79fcd603b3845f0dc7c2437f0&sportId=21&regionId[]=75&regionId[]=112&rangeStart={}&rangeEnd={}".format(UTC_start_string, UTC_end_str)
    headers = {
  'authority': 'www.odds.com.au',
  'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
  'accept': 'application/json, text/plain, */*',
  'dnt': '1',
  'sec-ch-ua-mobile': '?0',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-mode': 'cors',
  'sec-fetch-dest': 'empty',
  'referer': 'https://www.odds.com.au/greyhounds/',
  'accept-language': 'en-US,en;q=0.9',
  'cookie': '_ga=GA1.3.1723301145.1614836903; _gid=GA1.3.121255346.1614836904; _hjid=59c950ae-3e9c-4173-ac0d-7935e98db205; _ncg_id_=17336dafe97-3e09efd8-c15b-4e0c-b9c9-bf051bcfc797; nk=c367c4f3755cea8006f851839ee4761d; nc_aam_segs=asgmnt%3D16675898; _gat=1; utag_main=v_id:0177fbc7b12a00170cba7c6438a103073002306b00ac2$_sn:4$_se:1$_ss:1$_st:1614993640078$ses_id:1614991840078%3Bexp-session$_pn:1%3Bexp-session; __atuvc=21%7C9; __atuvs=6042d1de127afc36000; _ncg_sp_ses.cab8=*; AMCVS_5FE61C8B533204850A490D4D%40AdobeOrg=1; AMCV_5FE61C8B533204850A490D4D%40AdobeOrg=1585540135%7CMCIDTS%7C18693%7CMCMID%7C59190957356989207301799330543783425400%7CMCAAMLH-1615596641%7C8%7CMCAAMB-1615596641%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1614999041s%7CNONE%7CMCSYNCSOP%7C411-18698%7CvVersion%7C4.4.0; _ncg_sp_id.cab8=bdd3fed2-236b-4c55-a8cd-edd0af8e040c.1614836905.4.1614991842.1614915856.fc59d95f-a560-4a5f-9fb5-7548b5ece054'
}
    response = requests.get(Home_Url, headers=headers)
    Data_with_events = response.json()

    Race_Ids = [event_dicti['id'] for event_dicti in Data_with_events['events']]
    
    return Race_Ids


# In[4]:


def GetRaceDF(Race_ID, BetType):
    Race_Url = "https://www.punters.com.au/api/web/public/Odds/getOddsComparisonCacheable/?allowGet=true&APIKey=65d5a3e79fcd603b3845f0dc7c2437f0&eventId={}&betType=Fixed{}".format(Race_ID, BetType)

    headers = {
      'authority': 'www.punters.com.au',
      'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
      'accept': 'application/json, text/plain, */*',
      'dnt': '1',
      'sec-ch-ua-mobile': '?0',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
      'origin': 'https://www.odds.com.au',
      'sec-fetch-site': 'cross-site',
      'sec-fetch-mode': 'cors',
      'sec-fetch-dest': 'empty',
      'referer': 'https://www.odds.com.au/',
      'accept-language': 'en-US,en;q=0.9'
    }
    r = requests.get(Race_Url, headers = headers)
    Race_data = r.json()
    
    
    List_of_Racer_dfs = []
    for Racer in Race_data["selections"]:

        Name = Racer['name']
        Number = Racer['competitorNumber']
        Place_Result = Racer['result']
        Odds_collection = pd.DataFrame({"Name": [Name], "Number": [Number], "Place Result": [Place_Result]})
        for Odds_dicti in Racer['prices']:
            Bookmaker = Odds_dicti['bookmaker']
            if Odds_dicti["hasOdds"] == True:
                try:
                    Odds = Odds_dicti['odds']
                except KeyError:
                    continue
            else:
                Odds = 0
            Odds_collection[Bookmaker] = [Odds]

        List_of_Racer_dfs.append(Odds_collection)
        
    Race_df = pd.concat(List_of_Racer_dfs)
    Race_df["Race"] = Race_data["eventName"]
    Race_df["Event ID"] = Race_data["eventId"]
    Race_df["Status"] = Race_data["status"]
    Race_df['Order'] = range(1, len(Race_df)+1)
    
    return Race_df


# In[ ]:





# In[ ]:





# In[5]:


#Main
UTC_start_string, UTC_end_string = GetStartANDEndDateStr()

Race_Ids = GetRaceIds(UTC_start_string, UTC_end_string)

All_Races_dfs = []
for Race_ID in Race_Ids:
    Place_df = GetRaceDF(Race_ID, "Place")
    Win_df = GetRaceDF(Race_ID, "Win")
    Race_df = pd.merge(Place_df, Win_df, on = ["Name", "Number", "Place Result", "Race", "Event ID", "Status", "Order"], suffixes = ["_Place", "_Win"])
    All_Races_dfs.append(Race_df)
    
DF = pd.concat(All_Races_dfs)

DF["Start Date NZ"] = datetime.now().date() - timedelta(days = 1)


# In[6]:


DF.to_csv("Close WinPlace Odds {}.csv".format(datetime.now().strftime("%d-%m-%Y %H-%M-%S")))


# In[ ]:





# In[ ]:





# In[ ]:





# In[7]:


#STEPS

#Get start and end Times used to get corresponding event IDs 
##Get list of race IDs 
###For each of these race Ids...
####Create Dataframe from merging win and place frames
#####Concatonate all dfs and apply save

