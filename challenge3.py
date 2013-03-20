import os
import pyrax
import pyrax.exceptions as e
import sys, getopt
import time
from time import sleep



def main():
	"""Takes local directory and cloud files container as arguments.
	Uploads all files in the local directory to the container

	"""
	# Get domain and ip address from command line.
	local_dir = ''
	container = ''
	try:
	 	opts, args = getopt.getopt(sys.argv[1:],"hd:c:",["local_dir=","container="])
	except getopt.GetoptError as err:
	  	print 'Usage: challenge3.py -d <local_dir> -c <container>'
	  	sys.exit(2)
	if len(sys.argv) < 3:
	  	print 'Usage: challenge3.py -d <local_dir> -c <container>'
	  	sys.exit()
	for opt, arg in opts:
	  	if opt == '-h':
			print 'Usage: challenge3.py -d <local_dir> -c <container>'
			sys.exit()
	  	elif opt == "":
			print 'Usage: challenge3.py -d <local_dir> -c <container>'
			sys.exit()
	  	elif opt in ("-d", "--local_dir"):
			local_dir = arg
	  	elif opt in ("-c", "--container"):
			container = arg


	# Path to credentials credentials credential file.
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
	cf = pyrax.cloudfiles

	# Do the upload
	try:
		print "Uploading contents of %s to container %s" % (local_dir, container)
		upload_key, total_bytes = cf.upload_folder(local_dir, container=container)
	except e.FolderNotFound:
		print "ERROR: Local upload directory %s does not exist" % local_dir
		sys.exit()
	uploaded = 0
	while uploaded < total_bytes:
		uploaded = pyrax.cloudfiles.get_uploaded(upload_key)
		sys.stdout.write("\r" + " Progress: %4.2f%%" % ((uploaded * 100.0) / total_bytes))
		sys.stdout.flush()
		time.sleep(1)

	print
	print "Upload complete"


if __name__ == "__main__":
	main()