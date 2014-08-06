# Reads tweets, stored in json format in compressed text files (one tweet per line) and creates a
# CSV file from the output. Data to be extracted can be chosen using the command-line, but if there
# are no arguments then default commonly-used fields will be extracted. THese are:
#
# Tweet_ID, User_ID, Screen_Name, Lat, Lon, Loc_Txt, Time, Text
#
# Note: for convenience some time columns are also added: Year, Month, Day, Hour, Minute, Seconds

import argparse # For parsing command line arguments
import gzip # For compressing files
import os
import json
import sys
import multiprocessing as mp # For executing in multiple threads

import pprint # For pretty-printing errors
pp = pprint.PrettyPrinter(depth=1)

import datetime as dt
# Can't use dt.strptime() to convert time string to date because %z isn't valid! Instead use this:
import email.utils 
# NOTE ABOUT TIME ZONES: I'm using local time, not UTC. So there will be two kinks in the data when
# UK changes time zone. Advantage is that work patterns are constant (e.g. 9am-5pm) so don't want to
# change these when the time zone changes.

def fix(text):
    """Encodes a string as unicode and replaces difficult characters. Also checks for and removes
    things that will break the csv file like newline characters.
    Also adds quote characters around strings.
    If the given 'text' doesn't have an encode method (e.g. it is a number) then it is just returned
    as a string (using str)."""
    try: 
        return '"'+text.encode(encoding='UTF-8', errors='xmlcharrefreplace').replace("\n"," ")+'"'
    except AttributeError:
        return str(text)



# A list to store the fields to retrieve from the json files. Start with some commonly used fields.
# Each dimension needs to be separated with commas
fields = [
        "id",                   # ID of the tweet
        "user,id",              # ID of the user
        "user,screen_name",     # Name of the user
        "geo,coordinates,0",    # Latitude (y)
        "geo,coordinates,1",    # Longitude (x)
        "place,full_name",      # Name of the location
        "created_at",           # Time created
        "text"                  # Message text
        ]

# Remember number of errors (e.g. unrecognisable fields)
error_fields = dict()
error_count = 0


def read_json((fname, of)):
    """Reads an input json file, specified by 'fname'. Writes output to an output file ('of') that is
    open and writeable (e.g. the result of open('out.csv','w').
    If 'of' is None, then the csv text is returned rather than written
    Argument must be a tuple to work with multiprocessing.Pool """
    
    global error_fields
    global error_count

    if not os.path.isfile(fname):
        print "File {f} doesn't look like a file, I wont attempt to read it.".format(f=fname)
        return ""

    csv_str = "" # Store the csv text in memory before writing

    # work out if it is a compressed file or plain text and then open as a file object called
    # 'f'. (gzip and normal files can be treated the same)
    with gzip.GzipFile(fname, mode="rb") if fname[-3:] == ".gz" else open(fname, "r") as f:

        for line in f:
            tweet = json.loads(line) # Create a dictionary from the tweet on the current line
            
            # For each field that we're interested in, extract the data and write to the file
            for field in fields:
                nodata = False # Set to true if there is no data for this field
                # Need to do a multi-dimensional dictionary lookup from the string field (Sam P
                # helped me with this). I.e. convert 's = "user,name,firstname" to 
                # tweet["user"]["name"]["firstname"]
                value = tweet
                #print "\n* FIELD: {f}\n".format(f=field)
                for key in field.split(","):
                    #print "KEY:",key, "\nVALUE",value
                    if value == None:# or key not in value:
                        # There is no data for this field in this tweet
                        #print "No data in tweet for field: {f}".format(f=field)
                        #print "Value: '{v}'. Key: '{k}'".format(v=value, k=key)
                        nodata = True
                        error_count += error_count
                        if field in error_fields:
                            error_fields[field] += 1
                        else:
                            error_fields[field] = 0
                        continue # Move onto the next field
                    try:
                        value = value[key]
                    except TypeError: 
                        # This happens if the key should be an integer. E.g. with coordinates,
                        # instead of being a dictionary they are a two-element list
                        value = value[int(key)]


                if nodata:
                    csv_str += " , "
                    #of.write(" , ") # Nothing to write for this field
                else:
                    csv_str += fix(value)+", "
                    #of.write(fix(value)+", ")

            if not args.no_time_columns:

                # Have added all the required fields, now add time columns for convenience.This is
                # much more complicated than it should be because the %z symbol in strftime()
                # doesn't work on my mac, might work on unix. Instead use email.util library (!)

                time_str = tweet['created_at']
                # Make a tuple from the time (e.g. (year,month,day,hour,minute,second)
                time_tpl = email.utils.parsedate_tz(time_str) 
                # Now use those indivdual components to make a datetime object
                t = dt.datetime(*[time_tpl[i] for i in range(7)]) 

                #of.write("{Yr}, {Mo}, {D}, {H}, {M}, {S}".format( 
                #    Yr=t.year, Mo=t.month, D=t.day, M=t.minute, H=t.hour, S=t.second )
                #)
                csv_str += ("{Yr}, {Mo}, {D}, {H}, {M}, {S}".format( 
                    Yr=t.year, Mo=t.month, D=t.day, M=t.minute, H=t.hour, S=t.second )
                )
            # Finished this message, on to next one
            #of.write("\n") 
            csv_str += "\n"

    # Finished reading, now write output (or just return it)
    if of == None:
        return csv_str
    else:
        of.write(csv_str)





# ****** Create the command-line parser ******
parser = argparse.ArgumentParser(description='Convert JSON tweets to CSV.')

# Filenames
parser.add_argument('files', nargs="+", metavar="FILE",
        help="List of input files (at least one must be specified")
parser.add_argument('-o', '--outfile', default="tweets.csv",
        help="Output file name (default tweets.csv")

# Specify fields to extract
parser.add_argument('-f', '--field', nargs=1,
        help="Add a field to the output, with each dimension separated by commas. \
                E.g. to get the ID of the user who posted the message, use 'user,id'.")

# Whether or not to clear all the defaults or add time columns
parser.add_argument('-nd', '--no_defaults', action="store_true", default=False,
        help="Don't add any of the default fields to the CSV output")
parser.add_argument('-ntc', '--no_time_columns', action="store_true", default=False,
        help="Don't add the extra time columns to the CSV output")

# Whether to run multi-threaded
parser.add_argument('-nmt', '--no_multi_thread', action="store_true", default=False,
        help="Don't do the analysis in multiple threads")

# Parse command-line arguments
args = parser.parse_args()

if args.no_defaults:
    print "-nd specified: not extracting the default fields"
    fields = {}

# XXXX add any specified columns to the fields that we're interested in

if len(fields)==0:
    print "No fields have been specified, you have probably set the '--no_defaults' flag "+\
            "but not specified any of your own fields.\n"+\
            "This is probably a mistake so I wont continue.\n"+\
            "If you want to add fields yourself use --field"
    sys.exit(1)

print "Will write output to: ",args.outfile

print "Will extract data in the following json fields: ",fields

print "Will {s} time columns".format(s="not add" if args.no_time_columns else "add")



# ****** Start interrogating the tweet files (one tweet per line, possibly compressed) ******

with open(args.outfile, 'w') as of:

    # Prepare the output file
    for field in fields:
        of.write(field.replace(",","-") +", ") # (note: no commas in fieldnames)
    # Also add the extra time columns (added for convenience)
    if not args.no_time_columns:
        of.write("Year, Month, Day, Hour, Minute, Second")
    of.write("\n")

    if args.no_multi_thread: # Run in a single thread
        for i, fname in enumerate(args.files):
            print "Interrogating file {i}/{num}: {f}".format(i=(i+1), num=len(args.files), f=fname)
            read_json((fname, of))
        print "Finished. There were a total of {e} fields that could not be extracted from the"+\
                "json file. These are: ".format(e=error_count)
        pp.pprint(error_fields)

    else:
        num_cores = mp.cpu_count()
        print "Running as multiple processes on {cores} cores".format(cores=num_cores)
        p = mp.Pool(num_cores) # A pool of worker processes
        # Need to construct a list of tuples to pass as arguments to the read_json function
        #args = [(f, of) for f in args.files]
        args = [(f, None) for f in args.files]
        csv = p.map(read_json, args)
        # NOTE: at the moment the whole result is stored in memory before being written. Could use
        # p.map_async and provide a callback function to write results as they come in.
        for item in csv: # Pool saves the result of each process in a list
            of.write(item)
        print "Finished. (Some fields might not have been written, but to see exactly which ones"+\
            "might not have been written you need to run this with the --no_multi_thread argument)."

       



