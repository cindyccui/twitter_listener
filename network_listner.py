# File uses the Twitter API to find out about a twitter network (people who follow each other).

import sys
import os

import networkx as nx # Library to work with graphs

import configparser # To parse the configuration file

import tweepy
from tweepy import OAuthHandler # For OAuthentication

# Global parameters

DEPTH = 3 # Only move include DEPTH steps from the initial set of nodes
credentials_file = "./credentials.ini" # File that holds twitter API credentials

# Define the names of people we want to follow initially

INITIAL = [ "nickmalleson", "frogo", "NikLomax", "ajheppenstall", "adam_dennett" ]



# Build up the initial network

g = nx.Graph()


if __name__=='__main__':
    # Read the twitter authentication stuff from the configuration file (see README for details).
    if not os.path.isfile(credentials_file):
        print "Error",credentials_file,"doesn't look like a file. See the README for details."
        sys.exit(1)
    try:

        
        config = configparser.ConfigParser()
        config.read(credentials_file)

        consumer_key=str(config['CREDENTIALS']['consumer_key'])
        consumer_secret=str(config['CREDENTIALS']['consumer_secret'])
        access_token=str(config['CREDENTIALS']['access_token'])
        access_token_secret=str(config['CREDENTIALS']['access_token_secret'])

    except:
        print "Error reading credentials from", credentials_file
        print sys.exc_info()[0]
        raise
        
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    
    api = tweepy.API(auth) # Note: help(api) shows the avaiable methods - very useful
    
    for name in INITIAL:
        print "Getting user", name
        user = api.get_user(name)
        # Add the name as the node and also include user object as an additional attribute
        g.add_node(name, user=user) 
        print user, user.id
        print "Followers:"
        followers = api.followers(user.id)
        for f in followers:
            print f.name,
        print
        
        break
        
