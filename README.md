# Twitter Listener for Python

**PLease note:** this is a collection of scripts and libraries to use Python to connect to the Twitter Streaming API. Most of the work is done by the fantastic [tweepy](https://github.com/tweepy/tweepy) library ([http://www.tweepy.org/](http://www.tweepy.org/)) which I have had nothing to do with and can't take any credit for! It also contains work from Robin Lovelaces [tweepy fork](https://github.com/Robinlovelace/tweepy), particularly R stuff and some of the text in this README.

This README has some instructions about how to use the scripts here and start listenning to the Streaming API. It assumes a reasonable knowledge of how to use the command line and run Python programs.

## About Twitter data

_(Skip this section if you're not interested, it doesn't contain any instructions about how to use the software)_.

Twitter is admirably transparent and open about its data. Its [Terms of Service](https://twitter.com/tos?PHPSESSID=57a411f70b1964a2bc78b82638ba1843)
state that what you put up there is instantly publicly available and contain the 'tip' that "What you say on Twitter may be viewed all around the world instantly. You are what you Tweet!" This allows the company to offer open access methods for people to tap into the 'live stream' and use the information for 3rd party applications.

Twitter provides two APIs to access the data. The [REST API](https://dev.twitter.com/docs/api) (which is severly [rate limited](https://dev.twitter.com/docs/rate-limiting/1.1)) can be used to run searches on recent tweets. On the other hand, the
[Streaming API](https://dev.twitter.com/docs/api/streaming) provides tweets in real time that match some query. Queries are quite flexible and can be set up to listen for particular words/phrases, for messages from particular users, or for messages that originate in certain locations. We primarily use location as the search parameter below, but the tweepy library provides a mechanism to run any kind of query supported by the API.

## Pre-requisites

### Download this program!

Download all the ```twitter_listener``` files, by clicking on the 'download' link in GitHub, or following [this link](https://github.com/nickmalleson/twitter_listener/archive/master.zip). Unzip the files somewhere sensible, then navigate the directory using the command-line.

### Python

Before running the program, you need to get some software. Firstly, you'll need [Python](https://www.python.org/). On a mac or linux you probably have this already, but on Windows you'll probably need to download it. Follow the instructions on the [download page](https://www.python.org/downloads/).

### Python libraries

Once you have python, you need to install an extra library called <code>configparser</code>. Python has a package manager that you can use. On a Mac or Linux try:

```
sudo pip install configparser
```

and if that doesn't work, try:

```
sudo easy_install configparser
```

If neither of those work, you need to install the [setuptools](https://pypi.python.org/pypi/setuptools) package manager first (although I'm surprised that it didn't come with your Python distribution).

I'm not sure how to install Python libraries on Windows. It looks like [pip-Win](https://pypi.python.org/pypi/pip-Win/1.4) is what you need.

Once you have installed configparser, see if Python is ready to go by trying to run the ```streaming.py``` program that was part of the zip file you downloaded:

```
python streaming.py
```

If you get the following error: 
```Error ./credentials.ini doesn't look like a file. See the README for details. ``` 
then Python is working fine.

### Twitter API Key

Before you can access the Twitter API, you need a key (aka. 'Token'). This tells Twitter who is trying to acccess their API. The details from the key need to be stored in a file called ```credentials.ini``` that contains the following:

```{}
consumer_key=""
consumer_secret=""
access_token=""
access_token_secret=""
```

All four codes must be entered between the quotation "" symbols. To get these keys, follow the instructions below. You need to set up an 'application' on Twitter and then generate access tokens. 

[https://dev.twitter.com/oauth/overview/application-owner-access-tokens](https://dev.twitter.com/oauth/overview/application-owner-access-tokens)

Once you have those tokens, create your new ```credentials.ini``` file put the store the tokens using the format above. 


## Running the Program

You're now ready to run the program. The file ```streaming.py``` does most of the work. To see what options are avialable, type:

```{}
python streaming.py
```

The two most common uses are to listen to all tweets from the [public sample](https://dev.twitter.com/streaming/reference/get/statuses/sample) by using the ```-s``` flag:

```{}
python streaming.py -s
```

Or to listen to all tweets that come from a particular location using the ```-l``` flag entering the lat/loncoordinates of a bounding box to search in:

```{}
python streaming.py -l -10 50 2 60
```

(the above defines a bounding box approximately around the UK).


## The Output Data

The program writes all of the tweets that it receives to a file in the ```data``` directory called something like: ```t1452591943781.json``` ( the numbers are the [Unix epoch time](http://www.epochconverter.com/) when the program was started). In the file, each tweeet is written as a [JSON](http://www.json.org/) object (one per line). Once there are a certain number of tweets in the file (500,000 by default) it uses gzip to compress that file and starts a new one.

I've written a handy script to convert the files from JSON format into CSV. It's called ```json2csv.py```.

If you start it with the ```-h``` parameter it will tell you about the different options:

```{}
python json2csv.py -h
```

Basic useage is to pass in a directory that contains a load of ```.json``` and ```.json.gz``` files and tell it where to create a new csv file. E.g.:

```{}
python json2csv.py -o tweets.csv data/
```

You can specif exactly what attributes you want to extract if you want more/less than the defaults. E.g. to just get user ID and the message (and nothing else) you would do:

```{}
python json2csv.py -nd -f 'user,id' -f 'text' -o tweets.csv  data/
```

The other useful option is ```-nmt```. That runs the script in single-thread mode which will take a lot longer but gives you more useful output. 