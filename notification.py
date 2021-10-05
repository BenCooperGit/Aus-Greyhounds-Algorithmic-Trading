#!/usr/bin/env python
# coding: utf-8

# In[2]:


#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import pandas as pd
import glob

pd.set_option("display.max_columns", 100)
BOOKIES_PLACE = ["Ubet_Place", "Ladbrokes_Place", "Neds_Place", 
                    "Sportsbet_Place", "SportsBetting_Place", "PointsBet_Place", 
                    "Bookmaker_Place", "Unibet_Place", "BlueBet_Place", 
                    "Palmerbet_Place", "Betstar_Place", "TopSport_Place", 
                    "Realbookie_Place"]

# In[2]:


#Load most recent file
most_recent_file = max(glob.glob("get-data/open-data/Open WinPlace Odds*"), key = os.path.getctime)

df = pd.read_csv(most_recent_file)

#Doing things
df.drop(columns = ["NSWTAB_Place","NSWTAB_Win", "STAB_Place", "STAB_Win"], inplace = True)
df["Best_odds_wo_Bet365"] = df[BOOKIES_PLACE].max(axis = 1)

df["1/Best_odds_wo_Bet365"] = 1/df["Best_odds_wo_Bet365"]
df["n_odds"] = 0
for i in range(len(df)):
    for x in BOOKIES_PLACE:
        if df.loc[i, x] > 0:
            df.loc[i, "n_odds"] += 1

#How many places are paid
Number_of_Runners = {}
for Race in df["Race"].unique():
    Runners = len(df[df["Race"] == Race])
    Number_of_Runners[Race] = Runners
df["Number of Runners"] = df["Race"].apply(lambda x: Number_of_Runners[x])
Runners_to_payout = {10: 3, 9: 3, 8: 3, 7: 2, 6: 2, 5: 2, 4: 1, 3: 1, 2: 1}
df["Places Paid"] = df["Number of Runners"].apply(lambda x: Runners_to_payout[x])

#Overrounding
df = df[df["Order"] <= 8]
race_overrounds = df.groupby(["Race"])["1/Best_odds_wo_Bet365"].sum()
overrounds = pd.DataFrame({'Race':race_overrounds.index, 'overround':race_overrounds.values})
df = pd.merge(df, overrounds)
df["Real Overround"] = df["overround"]/df["Places Paid"]

df = df.drop(columns = "Unnamed: 0")


# In[3]:


##df = df[df["overround"]>1].reset_index().drop(columns = ["index"]) ##New piece - I am not arbing, please don't gub m


# In[4]:


n_books_hurdle1 = 1 ####
hurdle_for_bet1 = 1.2 ####
max_odds1 = 30 ####
df["will_bet_odds1"] = df["Real Overround"]*df["Best_odds_wo_Bet365"]*hurdle_for_bet1


# In[5]:


df["Bet"] = 0
for i in range(len(df)):
    if (df.loc[i, "Bet365_Place"] > df.loc[i, "will_bet_odds1"]) & (df.loc[i, "n_odds"] > n_books_hurdle1) & (df.loc[i, "Bet365_Place"] < max_odds1):
        df.loc[i, "Bet"] += 1


# In[6]:


Bet_df = df[df["Bet"]==1]
print(Bet_df)

Bet_df[["Race", "Number", "Name", 
        "Order", "Number of Runners", 
        "will_bet_odds1", "Bet365_Place", 
        "Ubet_Place", "Ladbrokes_Place", "Neds_Place", 
        "Sportsbet_Place", "SportsBetting_Place", "PointsBet_Place", 
        "Bookmaker_Place", "Unibet_Place", "BlueBet_Place", 
        "Palmerbet_Place", "Betstar_Place", "TopSport_Place", 
        "Realbookie_Place", "Event ID", "Status", 
        "Best_odds_wo_Bet365", "1/Best_odds_wo_Bet365", "n_odds", 
        "Places Paid", "overround", "Real Overround", 
        "will_bet_odds1", "Bet", "Bet365_Win", 
        "Ubet_Win", "Ladbrokes_Win", "Neds_Win", 
        "Sportsbet_Win", "SportsBetting_Win", "PointsBet_Win", 
        "Bookmaker_Win", "Unibet_Win", "BlueBet_Win", 
        "Palmerbet_Win", "Betstar_Win", "TopSport_Win", 
        "Realbookie_Win"]]
        .to_csv("NOTI.csv")

file = "NOTI.csv"
os.startfile(file)


# In[ ]:


# In[ ]:




