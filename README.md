## The Rackspace Challenge  
   
This challenge uses the Rackspace cloud API to do a number of different tasks.  I am using the Rackspace SDK 'pyrax' for the bulk of this challenge.  
  

#### Challenge 1
***
Creates x number of 512M CentOS 6.3 cloud servers.  You specify the server names to create in the script.  

  
  
#### Challenge 2
***
Makes an image of a cloud server and creates a new server
from that image.  Specify your values in the script.  

  
  
#### Challenge 3
***
Takes local directory and cloud files container as arguments.  Uploads all files in the local directory to the container.

	Usage: challenge3.py -d <local_dir> -c <container>  

  
  
#### Challenge 4
***
Creates an 'A' record in cloud DNS for a domain. 

	Usage: challenge.py -d <domain> -i <ip_address> 

  
  
#### Challenge 5
***
Creates a clound database (instance), database in that instance and a cloud database user.  Arguments are specified in the script.    


  
  
#### Challenge 6
***
Takes cloud files container as argument and creates
a CDN enabled container.

	Usage: challenge3.py -c <container>  
	



#### Challenge 7
***
Creates two servers and adds them to a load balancer.  No arguments required.  
  
  

#### Challenge 8
***
Creates a new container, CDN enables it, creates an index file object and creates a CNAME record pointing to the CDN URL of the container. 
  
   
The URL of the CDN container will be "challenge8.\<domain_name\>".  Specify all arguments in the script.


#### Challenge 9
***
Creates a new server based on the input of a FQDN, image name and RAM size (flavor).  The server is named the same as the FQDN.  A new domain is created in DNS that corresponds to the provided FQDN and an A record of the server's public IP is added to that domain. 



#### Challenge 10
***

Creates a cloud configuration with Rackspace Cloud products.

1.  Creates two 512M Ubuntu servers and adds an ssh key to both.
2.  Creates a load balancer and adds server to the LB.
3.  Sets up monitoring on the LB with a custom error page.
4.  Creates a DNS entry based on the FQDN of the LB VIP.
5.  Creates the error page in cloud files for backup.

All configuration options are inside script.


#### Challenge 11
***

Not Done Yet.


#### Challenge 12
***

Creates or lists mailgun routes.

Supply the match_recipient when calling function 'create_route'.
The create_route function sets the action as a forward to 
'http//cldsrvr.com/challenge1'

The function 'get_routes' takes no arguments.

REQUIRES requests, werkzeug and the werkzeug.MultiDict
