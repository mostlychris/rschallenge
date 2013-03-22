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
	"""Creates a clound database (instance), database in that instance
	and a cloud database user.

	"""
	# Specify new instance name, new database name, password and new user 
	instance_name = ""
	database_name = ""
	user_val = ""
	password_val = ""  # Leave blank for random password generation

	if instance_name == "" or database_name == "" or user_val == "":
		print "\nYou need to fill in the instance_name, database_name and user_val before continuing."
		print "Add these at the top of this script.\n"
		sys.exit()
	
	# Path to credential file.
	credential_file = os.path.expanduser("~/.rackspace_cloud_credentials")
	
	print "Authenticating"
	try:
	    pyrax.set_credential_file(credential_file)
	except e.AuthenticationFailed:
	    print "Authentication Failed: The file does not contain valid credendials"
	    sys.exit()
	except e.FileNotFound:
		print "Authentication file %s not found" % credential_file
		sys.exit()
	print "Authenticated Successfully as %s" % pyrax.identity.username
	
	cdb = pyrax.cloud_databases

	print "Creating Instance %s." % instance_name
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
	print "Creating database %s." % database_name
	try:
		db = instance.create_database(database_name)
	except e:
		print "Error creating database" 
		sys.exit()
	
	# Generate random password if password value not specified
	if password_val:
		print "Using supplied password %s" % password_val
	else:
		print "Generating random password for instance user."
		password_val = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))

	print "Creating user %s with password %s" % (user_val, password_val)
	try:
		user = instance.create_user(name=user_val,password=password_val, database_names=[db])
	except:
		print "Error creating user."
		sys.exit()
	
	print "Instance and database created succesfully"
	print "User", user_val, "created with a password of", password_val
	
if __name__ == '__main__':
    main()