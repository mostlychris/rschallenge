import os
import pyrax
import pyrax.exceptions as e
import time
from time import sleep
import sys
import datetime
import re

def main():
	"""Creates a cloud configuration with Rackspace Cloud products.

	1.  Creates two 512M Ubuntu servers and adds an ssh key to both.
	2.  Creates a load balancer and adds server to the LB.
	3.  Sets up monitoring on the LB with a custom error page.
	4.  Creates a DNS entry based on the FQDN of the LB VIP.
	5.  Creates the error page in cloud files for backup.

	"""

	# Set key file source, destination, content for load balancer
	# custom error page and domain name to set the LB VIP
	key_file = "/path/to/.public_key_file" 
	destination_path = "/root/.ssh/authorized_keys"	
	lb_custom_error = "<html><body>One or more of your nodes is offline</body></html>"
	domain_name = "my.domain.com"
	server1_name = "challenge10server1"
	server2_name = "challenge10server2"
	lb_name = "challenge10lb1"

	# Cloud files container to store backup of error page
	container = "challenge10_error_page_cont"

	try:
		with file(key_file) as f:
			contents = f.read() 
	except:
		print "ERROR reading key file."
		sys.exit()

	files = {destination_path : contents}

	# Path to credential file.
	credential_file = os.path.expanduser("~/.rackspace_cloud_credentials")
	print "-Authenticating"
	try:
	    pyrax.set_credential_file(credential_file)
	except e.AuthenticationFailed:
	    print "Authentication Failed: The file does not contain valid credendials"
	    sys.exit()
	except e.FileNotFound:
		print "Authentication file %s not found" % credential_file
		sys.exit()
	print "-Authenticated Successfully as %s" % pyrax.identity.username
	cs = pyrax.cloudservers
	clb = pyrax.cloud_loadbalancers
	dns = pyrax.cloud_dns
	cf = pyrax.cloudfiles
	
	ubu_image = [img for img in cs.images.list()
        if "12.04" in img.name][0]
	
	flavor_512 = [flavor for flavor in cs.flavors.list()
        if flavor.ram == 512][0]
	
	
	# Create new servers
	print "-Creating Servers."
	try:
		server1 = cs.servers.create(server1_name, ubu_image, flavor_512, files=files)
		s1_id = server1.id
		s1_pass = server1.adminPass
	except:
		print "***ERROR creating server 1."
		sys.exit()
	try:
		server2 = cs.servers.create(server2_name, ubu_image, flavor_512, files=files)
		s2_id = server2.id
		s2_pass = server2.adminPass
	except:
		print "***ERROR creating server 2."
		sys.exit()


	# We can't get network information until the server is complete 
	# so we keep checking for private network assignment which means they are *mostly* ready. 
	while not (server1.networks and server2.networks):
		time.sleep(3)
		server1 = cs.servers.get(s1_id)
		server2 = cs.servers.get(s2_id)

    # Get the private network IPs for the servers
	server1_ip = server1.networks["private"][0]
	server2_ip = server2.networks["private"][0]

	# Use the IPs to create the nodes and set them to ENABLED
	try:
		print "-Creating node1 and setting to ENABLED."
		node1 = clb.Node(address=server1_ip, port=80, condition="ENABLED")
	except:
		print "***ERROR creating node1."
		sys.exit()
	try:
		print "-Creating node2 and setting to ENABLED."
		node2 = clb.Node(address=server2_ip, port=80, condition="ENABLED")
	except:
		print "***ERROR creating node2."
		sys.exit()

	# Create the Virtual IP for the load balancer
	try:
		print "-Creating VIP."
		vip = clb.VirtualIP(type="PUBLIC")
	except:
		print "ERROR creating lb VIP."
		sys.exit()

	try:
		print "-Creating load balancer."
		lb = clb.create(lb_name, port=80, protocol="HTTP",
			nodes=[node1, node2], virtual_ips=[vip])
	except:
		print "***ERROR creating load balancer."
		sys.exit()

	# Wait for LB to finish building before adding monitor
	lb_status = lb.status
	while lb.status != 'ACTIVE':
		sleep(3)
		lb = clb.get(lb.id)
	
	lb_ip = lb.virtual_ips[0].address

	# Add DNS record for LB VIP.
	print "-Adding DNS record."
	dom = ''
	try:
		dom = dns.find(name=domain_name)
	except e.NotFound as err:
		print "***ERROR: Domain %s not found.  You will need to manually configure DNS." % domain_name
		print "-Continuing...."
	record = [{
			"type": 'A',
			"name": lb_name + '.' + domain_name,
			"data": lb_ip,
			"ttl": 300,
	}]

	try:	
		if dom:
			new_record = dom.add_records(record)
	except e as err:
		print "***ERROR adding DNS record.  You will need to manually configure DNS." % err
		print "-Continuing...."


	# The servers might still be in build state.  Watching them until done.
	print "-Finishing up server builds..."
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
	print "Server 1 IP: %s. Server 1 admin pass: %s. " % (str(server1.networks["public"]), str(s1_pass))
	print "Server 2 IP: %s. Server 2 admin pass: %s. " % (str(server2.networks["public"]), str(s2_pass))

	# Add a TCP monitor to the load balancer
	#try:
	print "-Adding TCP health check to LB"
	try:
		lb.add_health_monitor(type="CONNECT", delay=10, timeout=10,
			attemptsBeforeDeactivation=3)
	except e as err:
		print "***ERROR creating health check. %s Manual intervention required." % err
		print "-Continuing...."

	# Set custom error page for the load balancer
	# Wait five seconds to prevent immutable error
	sleep(5)
	print "-Adding custom error page to LB"
	try:
		lb_new = clb.list()[0]
		lb_new.set_error_page(lb_custom_error)
	except e as err:
		print "***ERROR adding custom error page. %s. Manual intervention required.", err
		print "-Continuing...."

	try:
		print "-Creating cloud files container %s" % container
		cont = cf.create_container(container)
	except:
		print "***ERROR: Problem creating container %s" % container
		sys.exit()

	print "-Storing error page in cloud files"
	try:
		obj = cf.store_object(container, "c10_error_page.html", lb_custom_error)
	except e as err:
		print "***ERROR storing error page in cloud files."
		sys.exit()

	print "-All done!  Celebrate as you wish."


if __name__ == '__main__':
    main()
