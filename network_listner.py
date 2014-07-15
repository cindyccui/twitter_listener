# File uses the Twitter API to find out about a twitter network (people who follow each other).

import sys
import os

import networkx as nx # Library to work with graphs
import matplotlib.pyplot as plt # G

import configparser # To parse the configuration file

import tweepy
from tweepy import OAuthHandler # For OAuthentication


# Global parameters

DEPTH = 3 # Only move include DEPTH steps from the initial set of nodes
credentials_file = "./credentials.ini" # File that holds twitter API credentials

# Define the names of people we want to follow initially

INITIAL = [ "nickmalleson"]
#INITIAL = [ "nickmalleson", "frogo", "NikLomax", "ajheppenstall", "adam_dennett" ]


def draw_graph(g):
    """Draw the given graph using matplotlib. E.g. see:
    http://networkx.github.io/documentation/latest/examples/drawing/weighted_graph.html
    http://networkx.github.io/documentation/networkx-1.9/reference/drawing.html"""

    pos=nx.spring_layout(g) #positions for all nodes
    nx.draw_networkx_nodes(g, pos)
    nx.draw_networkx_edges(g, pos)
    nx.draw_networkx_labels(g, pos)
    plt.axis('off')
    plt.show()


# Method that recursively builds up a graph

def build_graph(g, user, depth=0):
    """
    Recursively builds up a graph of followers.
    
    Parameters:

    g - the networkx graph to build up
    user - the user to search from (assume a User tweepy object)
    depth - counts the number of followers so far so we know when to stop (default 0)
    """
    XXXX HERE USE CODE BELOW TO IMPLEMENT THIS FUNCTION



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
    print "Getting user", name,
    user = api.get_user(name) # This returns a User object
    # Turn this into a dictionary
    print "Got",user.__dict__['screen_name']
    # Add the name as the node and also include user object as an additional attribute
    g.add_node(name, user=user) 
    print "Followers:"
    #followers = api.followers(user.id)
    followers = user.followers()
    for f in followers:
        # Get information about each follower and add them to the graph
        followername =f.__dict__['screen_name'] 
        print "\tGot",followername
        g.add_node(followername, user=f) # Again use the name as key and add additional attribute
        g.add_edge(name, f)
    print g
    break
    
