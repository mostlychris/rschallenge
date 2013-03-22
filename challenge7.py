import os
import pyrax
import pyrax.exceptions as e
import time
from time import sleep
import sys
import datetime

def main():
	"""Creates two servers and adds them to a load balancer.

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
	clb = pyrax.cloud_loadbalancers
	
	# Use a CentOS 6.3 Image 
	image = "c195ef3b-9195-4474-b6f7-16e5bd86acd0"
	
	# Use a 512M Standard Flavor
	flavor = "2" 
	
	
	#Create new servers (and yes I got these code snippets from the SDK docs)
	print
	print "Creating Servers."
	try:
		server1 = cs.servers.create("server1b", image, flavor)
		s1_id = server1.id
	except:
		print "ERROR creating server 1."
		sys.ext()
	try:
		server2 = cs.servers.create("server2b", image, flavor)
		s2_id = server2.id
	except:
		print "ERROR creating server 2."
		sys.ext()


	# We can't get network information until the server is complete 
	# so we keep checking for network assignment which means they are ready. 
	while not (server1.networks and server2.networks):
		time.sleep(1)
		server1 = cs.servers.get(s1_id)
		server2 = cs.servers.get(s2_id)

    # Get the private network IPs for the servers
	server1_ip = server1.networks["private"][0]
	server2_ip = server2.networks["private"][0]

	# Use the IPs to create the nodes and set them to ENABLED
	try:
		print "Creating node1 and setting to ENABLED."
		node1 = clb.Node(address=server1_ip, port=80, condition="ENABLED")
	except:
		print "ERROR creating node1."
		sys.exit()
	try:
		print "Creating node2 and setting to ENABLED."
		node2 = clb.Node(address=server2_ip, port=80, condition="ENABLED")
	except:
		print "ERROR creating node2."
		sys.exit()

	# Create the Virtual IP for the load balancer
	try:
		print "Creating VIP."
		vip = clb.VirtualIP(type="PUBLIC")
	except:
		print "ERROR creating lb VIP."
		sys.exit()

	try:
		print "Creating load balancer."
		lb = clb.create("challenge7lb2", port=80, protocol="HTTP",
			nodes=[node1, node2], virtual_ips=[vip])
	except:
		print "ERROR creating load balancer."
		sys.exit()

	# The servers might still be in build state.  Watching them until done.
	print "Finishing up server builds..."
	server1 = cs.servers.get(s1_id)
	server2 = cs.servers.get(s2_id)
	s2_status = server2.status
	while server1.progress < 100 or server2.progress < 100:
			sleep(1)
			server1 = cs.servers.get(s1_id)
			server2 = cs.servers.get(s2_id)
			#Output build progress information
			sys.stdout.write("\r" + "Server1 %s percent / Server 2 %s percent" % (str(server1.progress),str(server2.progress)))
			sys.stdout.flush()
	
	print
	print "Servers and load balancer created."


if __name__ == '__main__':
    main()
