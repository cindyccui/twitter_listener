from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import configparser # for reading the configuration file
import os
import sys
import json # For converting string into json object
import argparse # For parsing command-line arguments
import time # For adding a timestamp to files
import gzip # For compressing files
import traceback # For printing the traceback when errors occur
from multiprocessing import Process # For compressing files in separate threads


# add your details
consumer_key=""
consumer_secret=""
access_token=""
access_token_secret=""

# Global variables
credentials_file = "./credentials.ini" # Assume in local directory
TWEETS_PER_FILE = 500000 # Number of tweets to store before creating a new file
#TWEETS_PER_FILE = 5000 # Number of tweets to store before creating a new file

class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.

    """
    def on_data(self, data):
        print data
        return True

    def on_error(self, status):
        print status

class FileWriterListener(StreamListener):
    """
    A listener handles tweets are the received from the stream, writing them to a file.
    """

    def __init__(self, data_dir="data"):
        """Optional 'data_dir' argument specifies the data directory to store tweets in. This dir
        must exist - it is not added automatically because you will probably want to exclude it from
        the git project."""

        self.json_filename = ""  # Name of the file that tweets are being written to
        self.csv_filename = ""   # (will be tXX where XX is the timestamp in seconds)
        self.counter = 0 # Count the number of tweets
        self.delete_count = 0 # Count the nmber of 'delete' messages received (these aren't tweets)

        self.data_dir=data_dir # The directory to store tweet data in

    def compress_file(self, old_filename):
        """Compress the file with all twitter data in using gzip, deleting the original."""

        new_filename = old_filename+".gz" 
        print "Attempting to compres json file {f} and creating {f2}. (Counter={c})".format(\
                c=self.counter, f=old_filename, f2=new_filename)
        with open( old_filename, 'rb') as oldfile, gzip.open(new_filename, 'wb') as zipfile:
            zipfile.writelines(oldfile)
            os.remove(old_filename)
            print "\tFinished compressing file {f}, created file {f2}".format(\
                    f=oldfile.name,f2=zipfile.name)


    def on_data(self, raw_data):
        """Function called when the StreamReader (parent class) receives data from the stream. This
        function handles writing out the twitter data, compressing large files, etc"""

        # See if a new file needs to be created for these tweets
        if self.counter % TWEETS_PER_FILE == 0:

            old_filename = self.json_filename

            ts = str(int(time.time() * 1000) ) # Append timestamp to files
            #self.json_filename = "data/t"+ts+".json"
            #self.csv_filename = "data/t"+ts+".csv"
            self.json_filename = os.path.join(self.data_dir, "t"+ts+".json")
            self.csv_filename =  os.path.join(self.data_dir, "t"+ts+".csv")

            print "Writing to files:", self.json_filename, self.csv_filename

            # Compress the old filename (only to json, not csv) (and not when the script starts).
            # This is done in separate thread so as not to stop listenning in the meantime
            if self.counter > 0:
                p = Process(target=self.compress_file, args=(old_filename,))
                p.start()
                #self.compress_file(old_filename)

        # Call the parent (StreamReader) function which does some error checking, returning False if
        # this isn't a tweet.
        # if super(StreamListener, self).on_data(raw_data) == False:
        #    print "This doesn't look like a tweet"
        #    return False

        # 1 - use json library to create a python dictionary object from the raw data (a 
        # json-formatter string). This can be then be interrogated to find info. about the tweet.
        try:
            data = json.loads(raw_data)
        except ValueError as e:
            print "****\nCaught a ValueError:",str(e),"Wont try to parse the data."
            print "The raw_data is:**\n\t",raw_data,"**"
            print "The trackback is:"
            print traceback.format_exc()
            print "****"
            # Can't continue with this invalid data.
            return True

        # 2 - get the id (e.g. data['id'] )

        try:
            tweetid = str(data['id'])
            #print "read tweet",tweetid
            # 3 - write to a file (with filename of tweet id)
            f = open(self.json_filename,'a')
            try:
                f.write(raw_data) # 
            finally:
                f.close()

            self.counter += 1 # Increment tweet counter

            # 4 - TODO extract ueful info and write to a csv file

            # P.S. this is a nicer way to write to files using 'with' syntax:
            #with open('data/'+tweetid,'w') as f:
            #    f.write(str(data))

        except KeyError as e:
            # There is no ID field, so the data probably isn't a tweet. Need to decide what to do

            if 'delete' in data: # Looks like a 'delete' message. Ignore it
                self.delete_count += 1
                if self.delete_count % (TWEETS_PER_FILE/100) == 0:
                    print "For info: have received {num} delete messages. (These have been ignored).".format(num=self.delete_count)

            else: # Don't know what's wrong, write the message out to a separate file.
                print "Caught error receiving tweet: ", str(e) # Show what the error was
                # Call the file 'error<time>.json'
                fname = os.path.join(self.data_dir,"error"+str(int(time.time() * 1000) )+".json")
                print "\tNot sure what the problem is. Will write data to a different file called ",fname 
                f = open(fname,'w')
                try:
                    f.write(raw_data)
                finally:
                    f.close()

        return True

    def on_error(self, status):
        print "ERROR: ", str(status)



def check_locations(locs):
    """Checks that the locations input from the command line look OK. Exit if not."""
    # argparse will have turned the arguments into a 4-item list
    if locs[0] > locs[2]:
        print "Error with locations ({locs}), min x ({minx}) is greater than max x ({maxx})".format( \
                locs=locs, minx=locs[0], maxx=locs[2])
        sys.exit(1)
    if locs[1] > locs[3]:
        print "Error with locations ({locs}), min y ({miny}) is greater than max y ({maxy})".format( \
                locs=locs, miny=locs[1], maxy=locs[3])
        sys.exit(1)


def run():
    """Main munction: parses command-line options and starts the listener""" 
    global credentials_file
    
    # Parse command-line options
    parser = argparse.ArgumentParser()
#    (description='Usage %prog -l <locations> [-c <credentials_file]')

    # Can specify a bounding box
    parser.add_argument('-l', nargs=4, dest='locs', type=float, required=False, default=None, \
            help='specify min/max coordinates of bounding box (minx miny maxx maxy)')

    # The location of the credentials file
    parser.add_argument('-c', nargs=1, dest='cred', type=str, required=False, \
            help='specify location of credentials file', default=credentials_file)

    # Optionally get the sample of tweets from the firehose (not spatial)
    parser.add_argument('-s', '--sample', dest='sample', action="store_true", default=False,
        help="Get the 1% sample of tweets from the firehose (a random sample, no filtering)")

    args = parser.parse_args()

    # Check the location of the credentials file
    if not os.path.isfile(args.cred):
        print "Error",args.cred,"doesn't look like a file. See the README for details."
        sys.exit(1)
    credentials_file = args.cred

    # Choose a default directory to store messages in
    if args.locs != None:
        data_dir = "data"
    elif args.sample:
        data_dir = "firehose" 
    else:
        print "Error: no locations have been specified, nor has the 'sample' flag been set. So I "+\
            "don't know whether to filter tweets by location (-l) or just get a random sample from the"+\
            " firehose (-s)."
        sys.exit(0)


    # Read the twitter authentication stuff from the configuration file (see README for details).
    try:
        config = configparser.ConfigParser()
        config.read(credentials_file)

        consumer_key=str(config['CREDENTIALS']['consumer_key'])
        consumer_secret=str(config['CREDENTIALS']['consumer_secret'])
        access_token=str(config['CREDENTIALS']['access_token'])
        access_token_secret=str(config['CREDENTIALS']['access_token_secret'])

    except:
        print "Error reading credentials from", credentials_file
        sys.exit(0)

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    l = FileWriterListener(data_dir=data_dir)
    stream = Stream(auth, l)

    try: 

        if args.sample: # User specified get the random sample of tweets from firehose
            print "Starting firehose sample listener"
            if args.locs != None:
                print "Warning: both sample (-s) and locations (-l) have been specified. "+\
                        "I'm ignoring the locations and getting tweets from the firehose."
            stream.sample()

        else: # Assume we must be filtering on locaitons
            locations = args.locs
            check_locations(locations)
            print "Starting listener on locations:",locations

            #l = StdOutListener()

            stream.filter(locations=locations)
    finally:
        stream.disconnect()

if __name__=="__main__":
    run()
