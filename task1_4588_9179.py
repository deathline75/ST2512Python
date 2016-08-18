#!/usr/bin/env python
"""
Author: Neo Ken Hong, Kelvin (P1529179) & Ang Wei Xiang Darren (P1444588)
Class: DISM/FT/2A/02
Task: 1
"""
# Import necessary modules for the program to work
import re, time

print "Program started time:", time.strftime("%Y-%m-%d %H:%M:%S"), "\n" # Print the start time for program to track time taken

filename = 'access_log' # The file name to parse the log files from
hit_specific_ip = largest_file_size = highest_hit_file_count = 0 # Initialize to track total entries, amount of hits for 10.99.99.186, largest file size and current highest hit file count
highest_hit_file = largest_file = None # Initialize the highest hit file name and largest size file name
hit_page = {} # Initialize the dictionary to store all the pages and the hit counts

# Open the file for reading
with open(filename, 'r') as f:
	# Reads every line in the file
	for line in f:
		# Matches the line to the regular expression and puts it into a MatchObject object
		data = re.match(r'^(.*?) (.*?) (.*?) (\[.*?\]) \"\s?\w+ (.*?) .*?\s?\" (.*?) (.*?)$', line)

		# Check if the line has successfully matched the regular expression. If not, just cancel the whole operation
		if data is None:
			print "Error parsing:", line, "\n"
			break;

		
		# Strip away the starting urls if there are any
		weburl = data.group(5).replace("http://www.the-associates.co.uk", "")

		# Check if the url is already in the dictionary. If it exists, add one to the existing counter, otherwise insert a new key value as 1
		if weburl not in hit_page:
			hit_page[weburl] = 1
		else:
			hit_page[weburl] += 1
	
		# Check if the current page has more hits than the highest hit file count. If it is higher, re-assign it to the current page
		if hit_page[weburl] > highest_hit_file_count:
			highest_hit_file_count = hit_page[weburl]
			highest_hit_file = weburl
		
		# Check if the a specific IP has visited the page. If it has, add 1 to its counter
		if '10.99.99.186' == data.group(1):
			hit_specific_ip += 1
		
		# Check if the current page's file size is greater than the largest current file size, if it is, re-assign it to the current page
		if data.group(7) != '-' and int(data.group(7)) > largest_file_size:
			largest_file = weburl
			largest_file_size = int(data.group(7))
	f.close() # Close the file
	
print "Total entries were ", sum(hit_page.values()) # Take the total hits of all pages and sum them up
print "Total hits of '/assets/js/the-associates.js' were ", hit_page['/assets/js/the-associates.js'] # Take the total number of hits of '/assets/js/the-associates.js' and print it out
print "Total hits made by '10.99.99.186' were ", hit_specific_ip # Take the total vistitations from 10.99.99.186 and print it out
print "The largest page/object was ", largest_file, " with the size of ", largest_file_size, " bytes" # Take the largest file size and print it out along with the corresponding page
print "The highest number of hits was ", highest_hit_file_count, " for the page ", highest_hit_file, "\n" # Take the biggest hit page and print out the hit count and the page url.

print "Program completed time:", time.strftime("%Y-%m-%d %H:%M:%S"), "\n" # Print the end time for program to track time taken
