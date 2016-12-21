#!/usr/bin/python

import sys    
sys.path.insert(0, '/usr/lib/python2.7/bridge/')
from urllib2 import Request, urlopen, URLError, HTTPError
from urllib import urlencode
import json
import httplib

#this script was written in order to send a POST request to the server, and
#send back to arduino microcontroller the response of the server. This script 
#is called through arduino YUN Bridge library, therefore name of this script
#and the name of the script it is run in the arduino sketch must match.
#In order to execute the POST request two informations are needed
# the nfc_id retrieved by the nfc reader, which is passed by arduino
#microcontroller as command line argument, and the base url 
#which you can find here



#url of the server also, it is possible to edit /etc/hosts in order to mask ip 
baseurl='192.168.0.217:8443'

#taken from urls.py in labadmin repository on github
urls={'doorNFC':'/labadmin/labAdmin/opendoorbynfc/','userUpd':'/labadmin/labAdmin\updateUsers/','id':'/labadmin/labAdmin/user/identity/','nfcUs':'/labadmin/labAdmin/nfc/users/','cred':'labadmin/labAdmin/card/credits/'}

data={}
if len(sys.argv)!=2:
	#needed since arduino calls this script and passes as command line argument the nfc_id 
	print "False"
	print "uid code missing or corrupted"
else:
	current_uid=sys.argv[1]
	#formatting the post request                              
	data['nfc_id']=current_uid
	params = urlencode(data)
	headers={"Content-Type":"application/x-www-form-urlencoded"}
	#connecting to the server
	conn = httplib.HTTPSConnection(baseurl)
	try: 
		conn.request("POST", urls['doorNFC'], params, headers)
		response = conn.getresponse()	
	except HTTPError as e:
    		print 'False'
		print 'Error code:',e.code
	except URLError as e:
		print 'False'
    		print 'Reason:', e.reason
	else:
		rjson=response.read()
		rdata = json.loads(rjson)
		try:
			print rdata['open']
			for user in rdata['users']:
				print user['name']
#if the dictionary rdata is empty a TypeError will be raised		
		except TypeError:
			print "False"
			print "Card not associated to any user"
			
