import os
import pyrax
import pyrax.exceptions as e
import time
from time import sleep
import sys
import datetime

#Input a list of server names you want to create
new_servers_list = ["chefplaygound"]

def main():
	"""Creates x number of 512M CentOS 6.3 cloud servers. The number and name of the 
	servers is specified in the 'new_servers_list' list above.

	"""

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
	
	# Use a CentOS 6.3 Image 
	image = "c195ef3b-9195-4474-b6f7-16e5bd86acd0"
	
	# Use a 512M Standard Flavor
	flavor = "2" 
	
	for server_name in new_servers_list:
		#Create new server
		new_server = cs.servers.create(server_name, image, flavor)
		created_server = {'ID' : new_server.id, 'status' : new_server.status, 'admin_pass' : new_server.adminPass}
		print
		print "Building Server", server_name
		server = cs.servers.get(new_server.id)
		# We can't get network information until the server is complete 
		# so we keep checking for Active status every 10 seconds
		while server.status != 'ACTIVE':
			sleep(10)
			server = cs.servers.get(new_server.id)
			#Output build progress information
			sys.stdout.write("\r" + "Server Status: " + server.status + ' ' + str(server.progress) + '%')
			sys.stdout.flush()
			if server.status == "ERROR" or server.status == "UNKNOWN":
				print "Server build failed. Current status %s" % server.status
		# Now that the server is active, get the network information and print out the goods
		network = server.networks
		print
		print "Server", server_name, "build complete"
		print "Admin Password: ", created_server['admin_pass']
		print "Public IPs: ", network['public'][0], " " , network['public'][1]
		print

if __name__ == '__main__':
    main()
