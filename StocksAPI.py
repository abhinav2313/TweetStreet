
# coding: utf-8

# In[1]:


# Dependencies
import requests as req
import json
import tweepy
import pandas as pd
import time as t
import matplotlib.pyplot as plt
# from config import (consumer_key, consumer_secret, access_token, access_token_secret)
from datetime import datetime, date, time
import numpy as np
import os 

consumer_key = os.getenv("bot_consumer_key")
consumer_secret = os.getenv("bot_consumer_secret")
access_token = os.getenv("bot_access_token")
access_token_secret = os.getenv("bot_access_token_secret")


# Initialize sentiment analyzer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()
#Setup Tweepy API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())



# In[2]:


#Saving real time stock data in  file
stockHistory = 'stockHistory.csv'
# Base URL for GET requests to retrieve stock data
url = "https://api.iextrading.com/1.0/stock/"
#Opening file
file=open(stockHistory,'w')

#Stock ticker for collecting data
stocks = ['AAPL', 'V', 'AMZN', 'WMT', 'NFLX', 'NKE', 'M']
# Specify the companies
target_terms = ["@Apple", "@Visa", "@amazon", "@Walmart", "@netflix", "@Nike", "@Macys"]

# Loop through (can change the range if we need to)
def getSentimentAnalysis(handler):
    # Loop through all companies
    
   # Make a dictionary to hold each type of sentiment
        company_sentiment = {
            "compound_list": [], 
            "positive_list": [], 
            "negative_list": [], 
            "neutral_list": []
        }
        public_tweets = api.search(handler, count=100, result_type="recent")

        # Loop through all tweets
        for tweet in public_tweets["statuses"]:

            # Run Vader Analysis on each tweet
            results = analyzer.polarity_scores(tweet["text"])
            compound = results["compound"]
            pos = results["pos"]
            neu = results["neu"]
            neg = results["neg"]

            # Save all info to the corresponding lists
            company_sentiment["compound_list"].append(compound)
            company_sentiment["positive_list"].append(pos)
            company_sentiment["neutral_list"].append(neu)
            company_sentiment["negative_list"].append(neg)
        list_of_sentiment = [np.mean(company_sentiment["compound_list"]),np.mean(company_sentiment["positive_list"]),
                np.mean(company_sentiment["neutral_list"]),np.mean(company_sentiment["negative_list"])]
        return list_of_sentiment
print(str(datetime.now().time()))


# In[ ]:


stock_market_open_time = time(hour=8, minute=30, second=0, microsecond=0)
stock_market_close_time = time(hour=23, minute=0, second=0, microsecond=0)

def stockPriceCollectionWithSentiment():
    counter = 0;
    stock_tweet_df = pd.DataFrame()
    stock_tweet_data = []
    while((datetime.now().time() > stock_market_open_time) & (datetime.now().time() < stock_market_close_time) & counter < 50):
        counter = counter+1
        time_var = t.mktime(datetime.now().timetuple()) * 1000
        
        record = {}
        for stock in stocks:
            print(url+stock+"/quote")
            response = req.get(url+stock+"/quote")
            record.update({"Counter":counter})
            record.update({"Corporation":response.json()['companyName']})
            record.update({"Time":time_var})
            record.update({"Stock Ticker":response.json()['symbol']})
            record.update({"Stock Price":response.json()['latestPrice']})
            
            print("Counter::"+str(counter))
            print(response.json())
            sentiment_anal = getSentimentAnalysis(target_terms[stocks.index(stock)])
            record.update({"Compound":sentiment_anal[0]})
            record.update({"Positive":sentiment_anal[1]})
            record.update({"Neutral":sentiment_anal[2]})
            record.update({"Negative":sentiment_anal[3]})
            stock_tweet_data.append(record)
        stock_tweet_df = pd.DataFrame(stock_tweet_data)
        stock_tweet_df.to_csv("Stock_Tweet_Current.csv", mode="a")
        t.sleep(60)
try:
    stockPriceCollectionWithSentiment()
except KeyboardInterrupt:
    print('\n\nKeyboard exception received. Exiting.')
    file.close()
    exit()
file.close();



# In[ ]:




