import os
import pyrax
import pyrax.exceptions as e
import sys

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

dns = pyrax.cloud_dns

dn = raw_input('Please enter domain name: ')
domain_name = dn

ip = raw_input('Enter IP address to set as A record: ')
ip_address = ip


try:
	dom = dns.find(name=domain_name)
except e.NotFound:
	print "The domain %s was not found." % domain_name
	sys.exit()


print "Adding DNS record."
record = [{
			"type": 'A',
			"name": domain_name,
			"data": ip_address,
			"ttl": 300,
			}]
new_record = dom.add_records(record)

print "Record added" 
print new_record 

