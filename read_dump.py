#!/usr/bin/env python

################# Brief Explanation ##################
#
# Goal: This Python script is to see whether 
#       we can make prefetching proxy for the 
#       target application using dump file.
#
# Job : Check wheter an user application requests 
#       an URL which is from previous response
#
######################################################
#
# Code by Byungkwon Choi
#
######################################################

from libmproxy import flow
import sys
import json
import pdb

with open(sys.argv[1], "rb") as logfile:

	json_list = list()
	json_num_list = list()
	req_list = list()

	flow_c = 0
	req_c = 0
	js_c = 0
	found = 0

	freader = flow.FlowReader(logfile)

	try:
		# 1. Extract (1) request paths in requests and (2) JSON in responses from the dump file
		for f in freader.stream():
			if (hasattr(f.response,"headers")):
				flow_c = flow_c + 1

				# Append the request path to 'req_list'
				req_list.append(str(f.request.path))

				# Check whether the response is JSON
				if (str(f.response.headers["content-type"]).find("json") == -1):
					continue

				
				# Append the JSON to 'json_list'
				json_result = json.loads(str(f.response.content))
				json_list.append(json_result)

				# Record the sequence number of the response
				json_num_list.append(flow_c)

		# 2. Check whether request path(s) is/are from the response (JSON)
		for req in req_list:
			req_c = req_c + 1

			# Initialize the JSON sequence number
			js_c = 0
			for js in json_list:
				js_c = js_c + 1	
				for key ,value in js.iteritems():

					# Check whether the request path exists in the JSON or not
					if(str(value).find(req) != -1):

						# Check whether the request path appear after the response
						if(json_num_list[js_c-1] < req_c):
				
							# Print the information
							print '[FIND] An URL in the response exists in the successor request'
							print 'Response No.: ', json_num_list[js_c-1], ',  Request No.: ', req_c
							print 'The URL: ', req
							print 'JSON in the response: ', value
							print '\n'
							found = found + 1
						
				
		print 'Total number of flows: ', flow_c
		print 'Total number of JSONs in responses: ', len(json_list)
		print 'Total number of URLs detected: ', found

	except flow.FlowReadError as v:
		print "Flow file corrupted. Stopped loading."

