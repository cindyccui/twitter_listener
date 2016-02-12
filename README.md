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

If neither of those work, you need to install the [setuptools](https://pypi.python.org/pypi/setuptools) package manager first (although I'm surprised that it didn't come with your Python distribution.

I'm not sure how to install Python libraries on Windows. It looks like [pip-Win](https://pypi.python.org/pypi/pip-Win/1.4) is what you need.

Once you have installed configparser, see if Python is ready to go by trying to run the ```streaming.py``` program that was part of the zip file you downloaded:

```
python streaming.py
```

If you get the following error: 
```Error ./credentials.ini doesn't look like a file. See the README for details. ``` 
then Python is working fine.

## Twitter API Key

Before you can access the Twitter API, you need a key. The details from the key need to be stored in a file called ```credentials.ini'''.





```{}
consumer_key=""
consumer_secret=""
access_token=""
access_token_secret=""
```

All four codes must be entered correctly between the quotation "" symbols.
Then the rest of the `streaming.py` file can be altered for your needs
A basic example is provided [here](https://github.com/Robinlovelace/tweepy/blob/master/streaming-leeds.py),
which contains the following line of code to filter the tweets by geographical
location:

```{}
    stream.filter(locations=[-2.17,53.52,-1.20,53.96])
```

This instructs the program to only stream those tweets with are
within the bounding box, which set as the extent of West Yorksire,
in lat/long coordinates. If the file is saved in the working directory
of a Linux terminal, it can be run simply by typing the following:

```{python}
python streaming-leeds.py
```

To see this in action, take a look at the stream of Tweets illustrated
in [this video](http://youtu.be/fqrVFReL7dY).

<iframe width="420" height="315" src="//www.youtube.com/embed/fqrVFReL7dY" frameborder="0" allowfullscreen></iframe>

Not that in the first stream, a mass of unreadable information was provided directly:
this is the '[firehose]', the raw mass of data eminating from Twitter.
The second stream used the following line of code to extract only the user name
and the text for each tweet (see
[here](http://runnable.com/Us9rrMiTWf9bAAW3/how-to-stream-data-from-twitter-with-tweepy-for-python) for the complete script):

```{python}
print '@%s: %s' % (decoded['user']['screen_name'], decoded['text'].encode('ascii', 'ignore'))
```

Now, saving this stream of information from the terminal output is quite simple
in Linux: just type `bash | tee /path/to/logfile` before running the streaming
command and all output will be sent to the logfile in text format.
Remember to type `exit` again in the terminal when you have finished streaming
and the data will be saved. After that, the challenge is to extract useful
information from that mass of raw data.

## Extracting the data into other formats

## Doing it in Java

## Other options

To install the python-twitter plugin ( http://code.google.com/p/python-twitter/ )
