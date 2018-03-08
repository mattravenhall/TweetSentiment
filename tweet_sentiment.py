#!/usr/bin/env python3

import os
import time
import datetime
import numpy as np
from tweepy import API
from tweepy import OAuthHandler
from textblob import TextBlob # for sentiment analysis

def printT(message, flush=True):
    print(datetime.datetime.now().strftime('\033[96m[%d-%b-%Y %H:%M:%S]\033[0m '+message),flush=flush)

#Variables that contains the user credentials to access Twitter API 
access_token = "YOUR-KEY-HERE"
access_token_secret = "YOUR-KEY-HERE"
consumer_key = "YOUR-KEY-HERE"
consumer_secret = "YOUR-KEY-HERE"

keyword = '#phdlife'

subjectivity_filter = 0.5
n_pulled = 1000

filterSubjectivity = False
excludeLinks = False

# Create output file
with open("sentiments.txt", "a") as myfile:
    myfile.write("Time,Sentiment,nTweets,Tweets,Users,Sentiments,Subjectivities\n")

os.system('touch deleteToStop')         # Create buffer file (for easier stopping)
while os.path.isfile('deleteToStop'):   # Check buffer file exists
    yesterday = datetime.datetime.now().date() # - datetime.timedelta(days=1)
    tweets_cleaned = []
    users = []

    printT('Authorising')
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = API(auth)

    printT('Searching for tweets...')
    tweets = api.search(keyword, count=n_pulled, tweet_mode='extended', lang='en')

    sentiments = []
    subjectivities = []
    n_fail_date = 0
    n_fail_subj = 0
    n_fail_http = 0
    n_fail_retweet = 0

    for index, tweetObj in enumerate(tweets):
        tweet = tweetObj._json['full_text'] # tweetObj.text

        # Only keep those from yesterday
        if not tweetObj.created_at.date() == yesterday:
            #print('Tweet from wrong date.')
            n_fail_date += 1
            continue

        # Remove tweets with high subjectivity
        if filterSubjectivity and not TextBlob(tweet).subjectivity < subjectivity_filter:
            #print('Tweet too subjective.')
            n_fail_subj += 1
            continue

        # Remove tweets containing links, as these are most likely spam
        if excludeLinks and 'http' in tweet or 'www.' in tweet or '.co' in tweet or '.org' in tweet or '.ac' in tweet:
            #print('Tweet contains a link.')
            n_fail_http += 1 
            continue

        if tweet[:2] == 'RT' or tweetObj.retweeted:
            n_fail_retweet += 1
            continue

        # Remove usernames, hashtags
        words = [word for word in tweet.split(' ') if word is not '']
        tweet = ' '.join([word for word in words if not word[0] in ['#','@']])
        tweets_cleaned.append(tweet)
        users.append(tweetObj.user.screen_name)

        #print('Tweet {0}: {1}'.format(index+1, tweet))

        # get tweet sentiment
        sentiment = TextBlob(tweet).polarity
        subjectivity = TextBlob(tweet).subjectivity
        #print('Sentiment: {0}, Subjectivity: {1}'.format(sentiment, subjectivity))
        sentiments.append(sentiment)
        subjectivities.append(subjectivity)

    n_failed = n_fail_date + n_fail_subj + n_fail_http
    n_passed = len(sentiments)
    printT('{0} tweets successfully collected.'.format(n_passed))
    if n_fail_date > 0:
        printT('{0} failed due to wrong date.'.format(n_fail_date))
    if filterSubjectivity and n_fail_subj > 0:
        printT('{0} failed due to high subjectivity.'.format(n_fail_subj))
    if excludeLinks and n_fail_http > 0:
        printT('{0} failed due to containing a link.'.format(n_fail_http))
    if n_fail_retweet > 0:
        printT('{0} retweets removed'.format(n_fail_retweet))

    if sentiments is not []:
        mean_sentiment = np.mean(sentiments)
        #print('Mean sentiment: {0}'.format(mean_sentiment))
        with open("sentiments.txt", "a") as f:
            f.write('{0},{1},{2},{3},{4},{5}\n'.format(datetime.datetime.now(), mean_sentiment, n_passed, tweets_cleaned, users, sentiments, subjectivities))  #datetime.datetime(2018, 2, 7, 12, 10, 22, 7386)
    print('=====================================')
    time.sleep(1800) # Wait 30 mins
printT('Script terminated.')
