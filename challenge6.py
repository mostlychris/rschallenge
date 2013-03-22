import os
import pyrax
import pyrax.exceptions as e
import sys, getopt
import time
from time import sleep



def main():
	"""Takes cloud files container as argument and creates
	a CDN enabled container

	"""
	# Get container name from command line.
	container = ''
	try:
	 	opts, args = getopt.getopt(sys.argv[1:],"h:c:",["container="])
	except getopt.GetoptError as err:
	  	print 'Usage: challenge3.py -c <container>'
	  	sys.exit(2)
	if len(sys.argv) < 3:
	  	print 'Usage: challenge3.py -c <container>'
	  	sys.exit()
	for opt, arg in opts:
	  	if opt == '-h':
			print 'Usage: challenge3.py -c <container>'
			sys.exit()
	  	elif opt == "":
			print 'Usage: challenge3.py -c <container>'
			sys.exit()
	  	elif opt in ("-c", "--container"):
			container = arg


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
	cf = pyrax.cloudfiles

	# Do the upload
	try:
		print "Creating container %s" %  container
		cont = cf.create_container(container)
	except:
		print "ERROR: Problem creating container %s" % container
		sys.exit()

	try:
		print "Enabling container %s on the CDN" % container
		cf.make_container_public(container, ttl=900)
	except:
		print "ERROR: Problem enabling container %s on the CDN" % container
		sys.exit()

	print "Container creation completed"

if __name__ == "__main__":
	main()