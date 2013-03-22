import os
import pyrax
import pyrax.exceptions as e
import sys, getopt



def main():
	"""Creates an 'A' record in cloud DNS for a domain.  Arguments
	are provided on the command line.

	"""
	# Get domain and ip address from command line.
	domain = ''
	ip_address = ''
	try:
	 	opts, args = getopt.getopt(sys.argv[1:],"hd:i:",["domain=","ip_address="])
	except getopt.GetoptError as err:
	  	print 'Usage: challenge.py -d <domain> -i <ip_address>'
	  	sys.exit(2)
	if len(sys.argv) < 3:
	  	print 'Usage: challenge.py -d <domain> -i <ip_address>'
	  	sys.exit()
	for opt, arg in opts:
	  	if opt == '-h':
			print 'Usage: challenge4.py -d <domain> -i <ip_address>'
			sys.exit()
	  	elif opt == "":
			print 'Usage: challenge4.py -d <domain> -i <ip_address>'
			sys.exit()
	  	elif opt in ("-d", "--domain"):
			domain_name = arg
	  	elif opt in ("-i", "--ip_address"):
			ip_address = arg

	# Path to credentials credentials credential file.
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
	dns = pyrax.cloud_dns
	
	try:
		dom = dns.find(name=domain_name)
	except e.NotFound as err:
		print "ERROR: Domain not found. %s" % err
		sys.exit()
	
	
	print "Adding DNS record."
	record = [{
				"type": 'A',
				"name": domain_name,
				"data": ip_address,
				"ttl": 300,
				}]
	try:			
		new_record = dom.add_records(record)
	except e.DomainRecordAdditionFailed as err:
		print "ERROR: %s" % err
		sys.exit()
	
	print "Record added" 
	print new_record 

if __name__ == "__main__":
	main()