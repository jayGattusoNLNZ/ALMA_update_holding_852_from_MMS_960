
import pymarc
from bs4 import BeautifulSoup as Soup
import requests
import configparser
import copy

config = configparser.ConfigParser()
secrets = r"c:/source/secrets"
config.read(secrets)
apikey = config.get("configuration", "PRODUCTION")

def get_960s_from_mms(mms):
	url = f"https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms}?apikey={apikey}"
	r = requests.get(url).text
	soup = Soup(r, 'lxml')
	bibs_items = []
	for my_960  in soup.find_all("datafield", {"tag":"960"}):
		my_h_field = my_960.find("subfield", {"code":"h"}).text
		my_j_field = my_960.find("subfield", {"code":"j"}).text
		if verbose:
			print (f"h field: {my_h_field}")
			print (f"j field: {my_j_field}")
		return my_h_field, my_j_field

def update_holding(mms_id, holding_id, my_xml):
	url = f"https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms_id}/holdings/{holding_id}?apikey={apikey}"
	headers = {'content-type':'application/xml'}
	print (f"Updating Holding: {holding_id}\n{url}")
	# r = requests.put(url, headers=headers, data=my_xml)
	# print ()
	# if r.status_code != 200:
	# 	print (f"Udpate seemed to go OK for {url}")
	# else:
	# 	print (f"Somthing went wrong with update for {url}")


def get_holdings_and_process(mms, do_change, verbose):

	"""
	finds both the associated holding IDs, and collects both the holding records. 
	insrts the previously discovered i subfield and h subfield into the 852 holding field
	updates both the holding records in ALMA
	"""
	new_holdings  = []
	url = f"https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms}/holdings?apikey={apikey}"
	r = requests.get(url).text
	holdings = Soup(r, 'lxml')

	for my_holding in holdings.find_all("holding"):
		my_holding_code = my_holding.find("library").text
		my_holding_id = my_holding.find("holding_id").text
		url = f"https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms}/holdings/{my_holding_id}?apikey={apikey}"
		r = requests.get(url).text
		holding = Soup(r, 'lxml')
		original_holding = copy.deepcopy(holding)

		my_852 = holding.find("datafield", {"tag":"852"})
		
		new_852_subfield_h = ""
		new_852_subfield_i = ""

		if 'code="h"' not in str(my_852):
			new_852_subfield_h = holding.new_tag('subfield', code="h")
			new_852_subfield_h.string = my_h_field
			my_852.insert(1, new_852_subfield_h)

		if 'code="i"' not in str(my_852):
			new_852_subfield_i = holding.new_tag('subfield', code="i")
			new_852_subfield_i.string = my_j_field
			my_852.insert(1, new_852_subfield_i)

		holding = str(holding).replace("</body></html>", "").replace("<html><body>", "")
		

		### shows changes on screen - does not mean records were updated! 
		if verbose:
			if pprint:
				print (f"Holding: {my_holding_id}\n")
				print (str(original_holding).prettify().replace("</body></html>", "").replace("<html><body>", "").replace('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', ""))
				print ("___")
				print (str(holding.prettify()).replace("</body></html>", "").replace("<html><body>", "").replace('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', ""))
				print ("\n")
			else:
				print (f"Holding: {my_holding_id}\n")
				print (str(original_holding).replace("</body></html>", "").replace("<html><body>", "").replace('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', ""))
				print ("___")
				print (str(holding).replace('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', ""))
				print ("\n")

		### do the the update to the holding ###
		if do_change:
			if (new_852_subfield_h != "" or new_852_subfield_i != ""):
				update_holding(mms, my_holding_id, holding)
			else:
				print (f"Holding record {my_holding_id} seems to be already updated. Make manual checks if this is unexpected.")




### put your list of MMS ids here
### e.g. [123, 234, 345, 456] 
my_mms_ids = []

### When True, this commits the changes to the assigned system. 
### Be careful! I've tried to catch double commits of the same data, but its not particually robust...
### Tt the moment, if the parent record already has any i or h field in the holding 852, it doesn't do anything to the record. It will let you know.   
do_change = True

### When True, this screen prints the changes that will be made to each record so they can be checked. 
verbose = False

### When True, this changes the print style to nicely laid out XML indenting etc.  
pprint = False


if len(my_mms_ids) == 0:
	print ("You need to supply at least one MMS ID") 
for mms in my_mms_ids:
	print (f"MMS: {mms}")
	my_h_field, my_j_field = get_960s_from_mms(mms)
	print ()
	holdings = get_holdings_and_process(mms, do_change=do_change, verbose=verbose)
	print ()
	print ("**************************")
	print ()
