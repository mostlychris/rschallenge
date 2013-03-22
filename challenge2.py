import os
import pyrax
import pyrax.exceptions as e
import time
from time import sleep
from time import gmtime, strftime
import sys
import datetime

# Specify your values here
server_to_clone = ""
new_image_name = ""
new_server_name = ""

def main():
	"""Makes an image of a cloud server and creates a new server
	from that image.

	"""

	if server_to_clone == "" or new_image_name == "" or new_server_name == "":
		print "ERROR: You have not set all server or image values.  Set these inside the script."
		sys.exit()

	# Path to credential file.
	credential_file = os.path.expanduser("~/.rackspace_cloud_credentials")
	print "Authenticating"
	try:
	    pyrax.set_credential_file(credential_file)
	except e.AuthenticationFailed:
	    print "Authentication Failed: The file does not contain valid credendtials"
	    sys.exit()
	except e.FileNotFound:
		print "Authentication file %s not found" % credential_file
		sys.exit()
	print "Authenticated Successfully as %s" % pyrax.identity.username

	cs = pyrax.cloudservers
	
	# Get server object of server to be cloned
	try:
		existing_server = cs.servers.find(name=server_to_clone)
	except:
		print "ERROR: Error getting server to be cloned %s. Check that correct server is specified." % server_to_clone 
		sys.exit()

	
	# Create image of existing server
	print "Getting", server_to_clone, "server ID"
	server = cs.servers.get(existing_server.id)
	
	print "Creating Image", new_image_name
	new_img_id = server.create_image(new_image_name)
	img = cs.images.get(new_img_id)
	
	# Get min server size so we choose the correct flavor on new server creation
	flavor = [flavor for flavor in cs.flavors.list()
	        if flavor.ram == img.minRam][0]
	
	while img.status != 'ACTIVE':
		sleep(5)
		img = cs.images.get(new_img_id)
		now = strftime("%Y-%m-%d %H:%M:%S UTC", gmtime())
		# Output image creation progress information
		sys.stdout.write("\r" + "Image Status at " + str(now) + ": " + img.status + ' ' + str(img.progress) + '%')
		sys.stdout.flush()
	print
	print
	print "Image creation complete"
	
	# Create new server
	print
	print "Building Server", new_server_name
	new_server = cs.servers.create(new_server_name, img, flavor.id)
	created_server = {'ID' : new_server.id, 'status' : new_server.status, 'admin_pass' : new_server.adminPass}
	server = cs.servers.get(new_server.id)
	
	 
	# We can't get network information until the server is complete 
	# so we keep checking for Active status every 10 seconds 
	while server.status != 'ACTIVE':
		sleep(10)
		server = cs.servers.get(new_server.id)
		now = strftime("%Y-%m-%d %H:%M:%S UTC", gmtime())
		# Output build progress information
		sys.stdout.write("\r" + "Server Status at " + str(now) + ": " + server.status + ' ' + str(server.progress) + '%')
		sys.stdout.flush()
		if server.status == "ERROR" or server.status == "UNKNOWN":
				print "Server build failed. Current status %s" % server.status
	
	# Now that the server is active, get the network information and print out the goods
	network = server.networks
	print
	print "Server", new_server_name, "build complete"
	print "Admin Password: ", created_server['admin_pass']
	print "Public IPs: ", network['public'][0], " " , network['public'][1]
	print

if __name__ == '__main__':
    main()