# collect.py
# Collects image metadata from the "popular" section of 500px.com
#
# Collin Guarino
# The University of North Carolina Greensboro - Fall 2017
# License: MIT
# 
# To run this script you must obtain a consumer key from developer.500px.com
# and insert it into a file named "consumerkey.txt" in the current working directory.
# https://github.com/500px/api-documentation#checklist
# ^ "Register your application and get OAuth consumer key"
#
import urllib2
import os 
import json
import sys
from datetime import datetime

# Returns the consumer key string from the consumer key file
dir_path = os.path.dirname(os.path.realpath(__file__))
token_file_location = dir_path + "/consumerkey.txt" 
def get_key(): 
    try:
        with open(token_file_location) as f: 
            return f.read().rstrip() 
    except IOError:
        print "consumerkey.txt not found. Please view the source for instructions."
        sys.exit(1)

# Request all pages from 500px.com and dump the data in photos.dat
# See `Row` object for headers
def get_images():

    # Override previous data sets
    with open("photos.dat", "w") as f:
        f.truncate()

    # Format a GET /photos request for the 500px api site with arguments
    BASE_URL = "https://api.500px.com/v1/photos?"
    FEATURE_ARG = "feature=popular" # Look at the popular section only
    KEY_ARG = "&consumer_key=" + get_key()
    PAGE_STUB_ARG = "&page=" # An integer is appended to this 
    RESULTS_PER_PAGE = 100
    RESULTS_PER_PAGE_ARG = "&rpp=" + str(RESULTS_PER_PAGE)
    url = BASE_URL + FEATURE_ARG + KEY_ARG + RESULTS_PER_PAGE_ARG + PAGE_STUB_ARG
    print url

    # Make an initial request to see how many total pages and items are available
    request_url = url + str(1)
    response = urllib2.urlopen(request_url).read()
    response_content = json.loads(response)
    sample_size = response_content["total_items"]
    num_requests = response_content["total_pages"]
    print "Collecting %s total items... sending %s requests..." % (sample_size, num_requests)

    # Write column headers
    with open("photos.dat", "a") as f:
        f.write("URL Category Elapsed-Days\n")

    # Pagination handles "x" images per request. Increment this to go further back into past
    data = []
    for request_num in range(num_requests):
        # Request a page of photos
        request_url = url + str(request_num+1)
        response = urllib2.urlopen(request_url).read()
        response_content = json.loads(response)
        print "Fetching request content... %d/%d" % (request_num+1, num_requests)

        # Loop through each photo on each page
        total_sample = 0
        for photo in response_content["photos"]:
            # Read the response, parse the metadata, and add it to the data collection
            link = "500px.com/photo/" + str(photo["id"])

            category = get_category(photo["category"])
            if category == "NA":
                continue # Untracked category, skip it

            str_taken = photo["taken_at"]
            if str_taken == None:
                continue # Unavailable data, skip it
            str_taken = str_taken[:str_taken.rfind('-')] # Remove the UTC offset 
            datetime_taken = datetime.strptime(str_taken, "%Y-%m-%dT%H:%M:%S")

            str_uploaded = photo["created_at"]
            if str_uploaded == None:
                continue # Unavailable data, skip it
            str_uploaded = str_uploaded[:str_uploaded.rfind('-')] # Remove the UTC offset 
            datetime_uploaded = datetime.strptime(str_uploaded, "%Y-%m-%dT%H:%M:%S")

            # Calculate the elapsed time between when the photo was taken
            # and when it was uploaded to 500px. New property is days (double).
            elapsed = (datetime_uploaded - datetime_taken)
            elapsed_days = elapsed.days
            if elapsed_days < 0:
                continue # Data corrupt, skip it

            # Write each individual item to a .dat file
            row = Row(link, category, elapsed_days)
            with open("photos.dat", "a") as f:
                f.write(str(row) + "\n")
            total_sample += 1



# After all data is copied to photos.dat then write some info to status.txt
def write_status():
    # Track how many of each category we have
    sport_count = journalism_count = landscapes_count = travel_count = total = 0

    # Read each row and count them
    for line in open("photos.dat", "r"):
        columns = line.split(" ") 
        category = columns[1]
        if category == "Sport":
            sport_count += 1
        elif category == "Journalism":
            journalism_count += 1
        elif category == "Landscapes":
            landscapes_count += 1
        elif category == "Travel":
            travel_count += 1
        total += 1

    with open("status.txt", "w") as f:
        f.write("Category Count")
        f.write("\nSport " + str(sport_count))
        f.write("\nJournalism " + str(journalism_count))
        f.write("\nLandscapes " + str(landscapes_count))
        f.write("\nTravel " + str(travel_count))
        f.write("\nTotal " + str(total))
        f.write("\nData Captured On " + str(datetime.now()))
        f.write("\n")
            
# Represents one row in the data set (photos.dat)
class Row(object):
    def __init__(self, link, category, elapsed_days):
        self.link = link
        self.category = category
        self.elapsed_days = elapsed_days

    def __str__(self):
        return "%s %s %s" % (self.link, self.category, self.elapsed_days)
         


# Given the int category return the string value since the 500px 
# API returns categories as integers and we need categorical data.
# This will only return values for the categories tracked in this study:
# "People", "Sport", "Journalism", "Landscapes", "Nature", and "Travel".
def get_category(n):
    if n == 17:
        return "Sport"
    elif n == 3:
        return "Journalism"
    elif n == 8:
        return "Landscapes"
    elif n == 13:
        return "Travel"
    else:
        return "NA" # This category is untracked
    

if __name__ == "__main__":
    try:
        get_images()
    except KeyboardInterrupt:
        write_status()
        sys.exit(1)
    write_status()
