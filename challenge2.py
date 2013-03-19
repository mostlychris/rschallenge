import os
import pyrax
import pyrax.exceptions as e
import time
from time import sleep
import sys
import datetime

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

	#Set name of server to clone, name of new server and name of image
	server_to_clone = "ns2"
	new_image_name = "ns2testimg"
	new_server_name = "ns2newserver"
	
	cs = pyrax.cloudservers
	
	#Get server object of server to be cloned """
	#existing_server = [name for name in cs.servers.list()
	#	if server_to_clone in name.name][0]
	existing_server = cs.servers.find(name=server_to_clone)
	
	if existing_server == "":
		print "no server object returned for", server_to_clone, ".  check your server to clone variable."
		sys.exit()
	
	#Create image of existing server
	print "Getting", server_to_clone, "server ID"
	server = cs.servers.get(existing_server.id)
	
	print "Creating Image", new_image_name
	new_img_id = server.create_image(new_image_name)
	img = cs.images.get(new_img_id)
	
	#Get min server size so we choose the correct flavor on new server creation
	flavor = [flavor for flavor in cs.flavors.list()
	        if flavor.ram == img.minRam][0]
	
	while img.status != 'ACTIVE':
		sleep(10)
		img = cs.images.get(new_img_id)
		#Output image creation progress information
		sys.stdout.write("\r" + "Image Status: " + img.status + ' ' + str(img.progress) + '%')
		sys.stdout.flush()
	print
	print "Image creation complete"
	
	#Create new server
	print "Building Server", new_server_name
	new_server = cs.servers.create(new_server_name, img, flavor.id)
	created_server = {'ID' : new_server.id, 'status' : new_server.status, 'admin_pass' : new_server.adminPass}
	server = cs.servers.get(new_server.id)
	
	 
	### We can't get network information until the server is complete ###
	### so we keep checking for Active status every 10 seconds ###
	while server.status != 'ACTIVE':
		sleep(10)
		server = cs.servers.get(new_server.id)
		#Output build progress information
		sys.stdout.write("\r" + "Server Status: " + server.status + ' ' + str(server.progress) + '%')
		sys.stdout.flush()
	
	#Now that the server is active, get the network information and print out the goods
	network = server.networks
	print
	print "Server", new_server_name, "build complete"
	print "Admin Password: ", created_server['admin_pass']
	print "Public IPs: ", network['public'][0], " " , network['public'][1]
	print

if __name__ == '__main__':
    main()