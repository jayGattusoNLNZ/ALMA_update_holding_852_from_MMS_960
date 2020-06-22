This script takes a list of MMS IDs. 

For each MMS ID it gets the h and j subfields from the first MARC 960 tag it encounters. 
It gets the two holdings for that MMS ID
For each holding:
  If the holding has a h or i subfield in its 852, it doesn't add a new one.  
  It adds the h subfield as a new h subfield in the holding 852 tag
  It adds the j subfield as a new i subfield in the holding 852 tag
  If either an h or i subfield hav ebeen added to the 852, the holding record is updated in ALMA

How to use:

Get your list of MMSids that you want to process. 

Make them the list variable in the code 

    my_mms_ids = []

Do a dry run - and visually make sure you're seeing what you expect:
    do_change = False
    verbose = True
    pprint  = False

If you're happy what the response looks like, do a a commit run 

    do_change = True
    verbose = False
    pprint = False


Thats all... 


 -  When True, this commits the changes to the assigned system. 
 - Be careful! I've tried to catch double commits of the same data, but its not particually robust...
 - At the moment, if the parent record already has any i or h field in the holding 852, it doesn't do anything to the record. It will let you know.   
    
     do_change = True

 - When True, this screen prints the changes that will be made to each record so they can be checked.
 
     verbose = False

 - When True, this changes the print style to nicely laid out XML indenting etc.  
    
     pprint = False


******

Uncomment the section to use...              
[the script is hobbled by design without this being done]                            

	# r = requests.put(url, headers=headers, data=my_xml)
	# print ()
	# if r.status_code != 200:
	# 	print (f"Udpate seemed to go OK for {url}")
	# else:
	# 	print (f"Somthing went wrong with update for {url}")
