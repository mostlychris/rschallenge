import os
import pyrax
import pyrax.exceptions as e
import time
from time import sleep
import sys
import datetime
import socket

def main():
	"""Takes 3 arguments and creates a server and an A record that points
	to the server.

	Input domain name, img_name and amount of RAM (flavor).  Creates a 
	domain if it doesn not exist.
	
	"""
	
	# Get input args	
	domain = ''
	img_name = ''
	flavor_ram = ''	

	domain = raw_input("Enter FQDN: ")
	img_name = raw_input("Enter image name you want to create: ")
	flavor_ram = raw_input("Enter amount of RAM to use (M): ")

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
	cs = pyrax.cloudservers

	# Getting image ID for image specified.  If we don't recognize the image name
	# we print out a listing of valid images.
	print "Getting image ID"
	try: 
		image_to_create = [img for img in cs.images.list() if img_name in img.name][0]
	except:
		print "ERROR getting image ID from specified image.  Check your image name."
		print
		print "Available Images"
		print
		imgs = cs.images.list()
		for img in imgs:
			print img.name
		sys.exit()

	# Getting flavor ID for flavor specified.  If we con't recognize the flavor
	# we print out a listing of valid flavors.
	print "Getting flavor ID"
	try:
		flavor_to_create = [flavor for flavor in cs.flavors.list() if flavor.ram == int(flavor_ram)][0]
	except:
		print "ERROR getting flavor ID for specified flavor.  Check your flavor."
		print
		print "Make sure you specify a RAM size from the below list."
		print
		flvs = cs.flavors.list()
		for flv in flvs:
			print "Name:", flv.name
			print "  RAM:", flv.ram
			print
 		sys.exit()
	
	print "Building Server %s with image %s and flavor %s" % (domain, image_to_create.name, flavor_to_create.name)
	new_server = cs.servers.create(domain, image_to_create.id, flavor_to_create.id)
	created_server = {'ID' : new_server.id, 'status' : new_server.status, 'admin_pass' : new_server.adminPass}
	print
	server = cs.servers.get(new_server.id)
	# We can't get network information until the server is complete
	# so we keep checking for Active status every 5 seconds
	while server.status != 'ACTIVE':
		sleep(5)
		server = cs.servers.get(new_server.id)
		#Output build progress information
		sys.stdout.write("\r" + "Server Status: " + server.status + ' ' + str(server.progress) + '%')
		sys.stdout.flush()
		if server.status == "ERROR" or server.status == "UNKNOWN":
			print "Server build failed. Current status %s" % server.status

	# Now that the server is active, get the network information and print out the goods
	# NOVA does not always return the ipv4 address in the same slot so we have to
	# determine which slot it is in.  I am using socket for this.
	network = server.networks
	try:
		ip = socket.inet_pton(socket.AF_INET, network['public'][1])
		ipv4_address = network['public'][1]
	except:
		ip = socket.inet_pton(socket.AF_INET, network['public'][0])
		ipv4_address = network['public'][0]
		
	print
	print "Server build complete"
	print "Admin Password: ", created_server['admin_pass']
	print "Public IPs: ", network['public'][0], " " , network['public'][1]
	print "Creating A Record for new FQDN %s and setting to server IP %s." % (domain, ipv4_address)
	
	dns = pyrax.cloud_dns
	try:
		dom = dns.find(name=domain)
	except e.NotFound as err:
		print "Domain %s not found.  Creating domain." % domain 
		dom = dns.create(name=domain, emailAddress="hostmaster@" + domain)
			
	print "Adding DNS record."
	record = [{
			"type": 'A',
			"name": domain,
			"data": ipv4_address,
			"ttl": 300,
	}]
	try:	
		new_record = dom.add_records(record)
	except e.DomainRecordAdditionFailed as err:
		print "ERROR: %s" % err
		sys.exit()

	print "Record added" 

if __name__ == "__main__":
		main()