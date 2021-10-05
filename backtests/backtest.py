#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

pd.set_option("display.max_columns", 100)


# In[2]:


df_opens = pd.read_csv(r"C:\Users\Cooper\Oppening_Odds.csv")
df_closes = pd.read_csv(r"C:\Users\Cooper\Closing_Odds.csv")


# In[3]:


df_opens


# In[4]:


df_opens = df_opens.rename(columns = {"Unnamed: 0": "a"})

#creating max_a column
max_as = df_opens.groupby(["Date", "Race"]).a.apply(max).reset_index().rename(columns = {"a": "max_a"})
df_opens = pd.merge(df_opens, max_as, how = "left", on = ["Date", "Race"])

#update BF
df_opens["BF_wcom"] = df_opens["BF"]*0.94

#bestest odds
df_opens["Bestest_odds"] = df_opens[["BB2", "BT", "BD", "BE", "BF_wcom", "LB2", "CB2", "SB2", "SB5", "N", "TB2", "TS2", "Q", "UB", "GT"]].max(axis=1)

#drop the reserve dogs
df_opens = df_opens[df_opens["a"]<8]

#overrounding
df_opens["1/Bestest_odds"] = df_opens["Bestest_odds"].apply(lambda x: 1/x if x>0 else 0)
race_overrounds = df_opens.groupby(["Date", "Race"])["1/Bestest_odds"].sum().reset_index().rename(columns = {"1/Bestest_odds": "Overround"})
df_opens = pd.merge(df_opens, race_overrounds, how = "left", on = ["Date", "Race"])

#drop arbs
df_opens = df_opens[df_opens["Overround"]>1]

#best odds with out bt
df_opens["Best_odds_woBT"] = df_opens[["BB2", "BD", "BE", "BF_wcom", "LB2", "CB2", "SB2", "SB5", "N", "TB2", "TS2", "Q", "UB", "GT"]].max(axis=1)
df_opens = df_opens[df_opens["Best_odds_woBT"] != 0]

#number of odds
df_opens = df_opens.reset_index()
df_opens["n_odds"] = 0
for i in range(len(df_opens["Race"])):
    for x in ["BB2", "BD", "BE", "BF", "LB2", "CB2", "SB2", "SB5", "N", "TB2", "TS2", "Q", "UB", "GT"]:
        if df_opens.loc[i, x] > 0:
            df_opens.loc[i, "n_odds"] += 1

#last dog number and name
last_dog = df_opens.groupby(["Date", "Race"])["Dog", "a"].last().reset_index().rename(columns = {"Dog": "ld_name", "a": "ld_a"})
df_opens = pd.merge(df_opens, last_dog, how = "left", on = ["Date", "Race"]).drop(columns = ["index"])


# In[5]:


df_opens


# In[ ]:





# In[6]:


df_closes


# In[7]:


df_closes = df_closes.rename(columns = {"Unnamed: 0": "a"})

#creating max_a column
max_as = df_closes.groupby(["Date", "Race"]).a.apply(max).reset_index().rename(columns = {"a": "max_a"})
df_closes = pd.merge(df_closes, max_as, how = "left", on = ["Date", "Race"])

#update BF
df_closes["BF_wcom"] = df_closes["BF"]*0.94

#bestest odds
df_closes["Bestest_odds"] = df_closes[["BB2", "BT", "BD", "BE", "BF_wcom", "LB2", "CB2", "SB2", "SB5", "N", "TB2", "TS2", "Q", "UB", "GT"]].max(axis=1)

#overrounding
df_closes["1/Bestest_odds"] = df_closes["Bestest_odds"].apply(lambda x: 1/x if x>0 else 0)
race_overrounds = df_closes.groupby(["Date", "Race"])["1/Bestest_odds"].sum().reset_index().rename(columns = {"1/Bestest_odds": "Overround"})
df_closes = pd.merge(df_closes, race_overrounds, how = "left", on = ["Date", "Race"])

#last dog number and name
last_dog = df_closes.groupby(["Date", "Race"])["Dog", "a"].last().reset_index().rename(columns = {"Dog": "ld_name", "a": "ld_a"})
df_closes = pd.merge(df_closes, last_dog, how = "left", on = ["Date", "Race"])


# In[8]:


df_closes


# In[ ]:





# In[ ]:





# In[ ]:





# In[9]:


#big daddy dataframe
df = pd.merge(df_opens, df_closes, how = "left", on = ["t", "Race", "Dog"], suffixes = ["_o", "_c"])
df

#BETTING STRATEGY
#1
n_books_hurdle1 = 1 ####
hurdle_for_bet1 = 1.5####
max_odds1 = 30 ####
df["will_bet_odds1"] = df["Overround_o"]*df["Best_odds_woBT"]*hurdle_for_bet1

#2
n_books_hurdle2 = 1 ####
hurdle_for_bet2 = 1.3 ####
max_odds2 = 10 ####
df["will_bet_odds2"] = df["Overround_o"]*df["Best_odds_woBT"]*hurdle_for_bet2

#3
n_books_hurdle3 = 2 ####
hurdle_for_bet3 = 1.3 ####
max_odds3 = 30 ####
df["will_bet_odds3"] = df["Overround_o"]*df["Best_odds_woBT"]*hurdle_for_bet3

#Select bets

df["bet"] = 0
for i in range(len(df)):
    if (df.loc[i, "BT_o"] > df.loc[i, "will_bet_odds1"]) & (df.loc[i, "n_odds"] > n_books_hurdle1) & (df.loc[i, "BT_o"] < max_odds1):
        df.loc[i, "bet"] += 1
    elif (df.loc[i, "BT_o"] > df.loc[i, "will_bet_odds2"]) & (df.loc[i, "n_odds"] > n_books_hurdle2) & (df.loc[i, "BT_o"] < max_odds2):
        df.loc[i, "bet"] += 1
    elif (df.loc[i, "BT_o"] > df.loc[i, "will_bet_odds3"]) & (df.loc[i, "n_odds"] > n_books_hurdle3) & (df.loc[i, "BT_o"] < max_odds3):
        df.loc[i, "bet"] += 1
    
        
bet_df = df[df["bet"]==1]

#If a no runner, take SP

NR_cond = ((bet_df["ld_name_o"] == bet_df["ld_name_c"]) & (bet_df["ld_a_o"] == bet_df["ld_a_c"]))
cond = [NR_cond, ~NR_cond]
val = [bet_df["BT_o"], bet_df["BT_c"]]
bet_df["BT_o"] = np.select(cond, val)

bet_df["NR"] = np.select(cond, [0,1])

#drop my non-runners
bet_df = bet_df[~bet_df["BT_c"].isna()]

#define value and probabilities

bet_df["fair_go"] = bet_df["Bestest_odds_c"]*bet_df["Overround_c"]

bet_df["value"] = bet_df["BT_o"]/bet_df["fair_go"]-1

bet_df = bet_df.reset_index()
bet_df

#Summary statistics

print("Total Value: " + str(bet_df["value"].sum()))
print("Average value per bet: " + str(bet_df["value"].mean()))
print( )
print("Number of bets: " + str(len(bet_df)))

days_to_bet = len(df_opens["Date"].unique())
print("Days to bet: " + str(days_to_bet))


# In[11]:


bet_df


# In[10]:





# In[ ]:




