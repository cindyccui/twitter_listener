# File uses the Twitter API to find out about a twitter network (people who follow each other).

import sys
import os
import time # To allow for waiting to stop going over rate limits

import networkx as nx # Library to work with graphs
import matplotlib.pyplot as plt # G

import configparser # To parse the configuration file

import tweepy
from tweepy import OAuthHandler # For OAuthentication
from tweepy import TweepError 


# Global parameters

DEPTH = 3 # Only move include DEPTH steps from the initial set of nodes
credentials_file = "./credentials.ini" # File that holds twitter API credentials

# Define the names of people we want to follow initially

INITIAL = [ "nickmalleson"]
#INITIAL = [ "nickmalleson", "frogo", "NikLomax", "ajheppenstall", "adam_dennett" ]


def draw_graph(g,  pos=None):
    """Draw the given graph using matplotlib. E.g. see:
    http://networkx.github.io/documentation/latest/examples/drawing/weighted_graph.html
    http://networkx.github.io/documentation/networkx-1.9/reference/drawing.html
    
    Parameters:
        g - the graph to draw
        pos - the layout to use (default is nx.spring_layout). For help, see nx.layout documentation
    """
    if pos == None:
        pos = nx.spring_layout(g)

    nx.draw_networkx_nodes(g, pos)
    nx.draw_networkx_edges(g, pos)
    nx.draw_networkx_labels(g, pos)
    plt.axis('off')
    plt.show()


# Method that recursively builds up a graph

def build_graph(g, user, parent, depth=0):
    """
    Recursively builds up a graph of followers.
    
    Parameters:

    g - the networkx graph to build up
    user - the user to search from (assume a User tweepy object)
    parent - the person who is friends with this user (could be None)
    depth - counts the number of followers so far so we know when to stop (default 0)
    """
    
    # First get the names of the users from the User objects (User provides a dict which allows
    # access to all parameters
    username = user.__dict__['screen_name']
    parentname = ""
    if parent!=None:
        parentname = parent.__dict__['screen_name']

    print "Analysing user ",username,"whose parent is",\
            parentname if parent!=None else "none"

    # Add nodes and edges to the graph
    g.add_node(username, user=user)

    if parent != None:
        g.add_edge(username, parentname)

    # Now do recurse over all the user's followers, unless we've reached the maximum depth
    if depth > 0:
        # To get followers requires a call to the Twitter API. Check and catch rate limitting
        # problems
        fail = True # Assume failure of api call and loop undil it doesn't fail
        followers = None
        while (fail):
            try:
                followers = user.followers()
                fail = False # If get here then the api call succeeded
            except TweepError as e:
                print "Caught error:",str(e)
                print "Assuming it is a rate limitting problem, waiting 5 mins"
                time.sleep(300)# 5 mins = 300 seconds
        for f in followers:
            build_graph(g, f, user, depth-1)




# Build up the initial network

g = nx.Graph()

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
    user = api.get_user(name) # This returns a User object
    build_graph(g, user=user, parent=None, depth=DEPTH)
