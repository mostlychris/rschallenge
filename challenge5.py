import os
import pyrax
import pyrax.exceptions as e
import sys
import time
from time import sleep
from time import gmtime, strftime
import string
import random


def main():
	# Path to credentials credentials credential file.
	credendials = "~/.rackspace_cloud_credentials"
	credential_file = os.path.expanduser("~/.rackspace_cloud_credentials")
	
	print "Authenticating"
	try:
	    pyrax.set_credential_file(credential_file)
	except e.AuthenticationFailed:
	    print "Authentication Failed: The file does not contain valid credendials" % credenditials
	    sys.exit()
	except e.FileNotFound:
		print "Authentication file %s not found" % credential_file
		sys.exit()
	print "Authenticated Successfully as %s" % pyrax.identity.username
	
	cdb = pyrax.cloud_databases
	instance_name = "challenge5dbinst7"
	database_name = "challenge5db"
	user_val = "testdbuser"
	password = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))
	
	print "Creating Instance."
	try:
		instance = cdb.create(instance_name, flavor="m1.tiny", volume=1)
	except e:
		print "Error creating instance."
		sys.exit()
	
	inc = cdb.get(instance.id)
	while inc.status != 'ACTIVE':
			sleep(10)
			now = strftime("%Y-%m-%d %H:%M:%S UTC", gmtime())
			inc = cdb.get(instance.id)
			sys.stdout.write("\r" + "Instance Status at " + str(now) +  ": " + inc.status)
			sys.stdout.flush()
	
	print
	print "Creating database."
	try:
		db = instance.create_database(database_name)
	except e:
		print "Error creating database" 
		sys.exit()
	
	print "Creating user."
	try:
		user = instance.create_user(name=user_val,password=password, database_names=[db])
	except:
		print "Error creating user."
		sys.exit()
	
	print "Instance and database created succesfully"
	print "User", user_val, "created with a password of", password
	
if __name__ == '__main__':
    main()