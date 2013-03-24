import os
import pyrax
import pyrax.exceptions as e
import sys, getopt
import time
from time import sleep

def main():
	"""Creates a static webpage for cloud files. 

		Creates a new container, CDN enables it, creates an index file object 
		and creates a CNAME record pointing to the CDN URL of the container.

	"""
	# Set container, file object, object content and domain to create CNAME record on.
	container = "chal8cont2"
	object_name = "index2.html"
	content = "<!DOCTYPE html><head><title>Challenge8</title></head><body background='#000'>\
		<img src='http://www.rackspace.com/images/header/logo-rackspace.png'\
		<br><br><br>This is the content of the challenge 8 index file.\
		</body></html>"
	domain_name = "checkpointrms.com"

	# Check to make sure we have all the arguments we need to continue.
	if container == "" or object_name == "" or content == "" or domain_name == "":
		print "ERROR: Missing arguments.  You must supply all arguments in the script."
		sys.exit()

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
	dns = pyrax.cloud_dns

	# Create container and CDN enable it.
	try:
		print "Creating cloud files container %s" %  container
		cont = cf.create_container(container)
	except:
		print "ERROR: Problem creating container %s" % container
		sys.exit()

	try:
		print "Enabling container %s on the CDN" % container
		cf.make_container_public(container, ttl=600)
	except:
		print "ERROR: Problem enabling container %s on the CDN" % container
		sys.exit()

	print "Cloud files container %s creation completed" % container

	# Create an index.html object with value of 'content' in it.
	# Check the checksum of uploaded object to make sure it is valid.
	try:
		print "Uploading content to cloud files object."
		chksum = pyrax.utils.get_checksum(content)
		obj = cf.store_object(container, object_name, content, etag=chksum)
	except e.UploadFailed:
		print "Error uploading content to index file."
		sys.exit()

	print "Content succesfully uploaded into container %s." % container

	print "Creating CNAME record for new container on domain %s." % domain_name
	try:
		dom = dns.find(name=domain_name)
	except e.NotFound as err:
		print "ERROR: Domain not found. %s" % err
		sys.exit()

	# Build the CNAME record object.
	record = [{
		"type": 'CNAME',
		"name": 'challenge8.%s' % domain_name,
		"data": cont.cdn_uri,
		"ttl": 300,
		}]

	# Add the CNAME record.
	try:	
		new_record = dom.add_records(record)
	except e.DomainRecordAdditionFailed as err:
		print "ERROR: %s" % err
		sys.exit()

	print "CNAME record creation completed."

if __name__ == "__main__":
	main()
