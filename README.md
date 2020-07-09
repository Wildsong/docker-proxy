# docker-proxy

This project uses jwilder/nginx-proxy to build a container that
will automatically add and remove reverse proxy setups using nginx
and jwilder's dockergen daemon.

It uses JrCs/docker-letsencrypt-nginx-proxy-companion to 
automatically set up to maintain and use Let's Encrypt certificates.
(2019-11-09 Updated to v1.12 to support ACME V2)

Each container that you want to proxy needs 3 things.

* It needs to define VIRTUAL_HOST with a unique name, because the proxy
uses that name to create its entry for the service.
* It needs to use proxy_net as its network so that the proxy can see the service.
* It needs to EXPOSE the port you want to proxy. 

For example I run pi-hole so in the docker-compose.yml for pi-hole I have

````
  networks:
    - proxy-net
  environment:
    VIRTUAL_HOST: pihole.wildsong.biz
    VIRTUAL_PORT: 80 # This is only needed if you run on a different port.
  expose:
    - "80"
````

If you want the proxy to set up an SSL certificate too then it needs more:

````
  environment:
    LETSENCRYPT_HOST: pihole.wildsong.biz
    LETSENCRYPT_MAIL: webmaster@wildsong.biz   (This line is optional but a good idea)
````

I created the dhparam volume and copied my old nginx dhparam.pem file
into it but you can let it create one for you and skip this.

````
docker volume create proxy_dhparam
sudo cp dhparam.pem /home/docker/volumes/proxy_dhparam/_data/
docker volume create proxy_certs
sudo cp -r /etc/letsencrypt/* /home/docker/volumes/proxy_certs/_data/
````

Also I created the certs volume and copied my old /etc/letsencrypt
files into it.

If you don't need to preserve old files you can just forget this and
let docker create new (empty) volumes for you.

## How to start the proxy

* Copy sample.env to .env
* Customize .env
* Launch it
````
docker-compose up
````

### CORS support

To the proxy I added the nginx configuration to generate the right
HTTP headers to avoid Cross Origin Scripting (CORS) error messages.

In theory this is done with the "default_location" file,
but it looks like I have created separate files for each virtual server
that I proxy. For example I have geoserver.wildsong.biz_location
and then put a copy of that file in

   /var/lib/docker/volumes/proxy_vhost/_data/
   
which is the volume mounted at /etc/nginx/vhost.d in the proxy docker.

Currently I have set up these files to accept CORS requests from ANYWHERE.

### Checking out what's going on

All output directed to STDOUT and STDERR from Docker containers is regarded as
log data. I especially want to be able to analyze web logs to see what interesting things
are going on, so the docker-compose file sets up logging.

You can check the contents of the volumes too, they are

* proxy_certs -- holds the letsencrypt certificates
* proxy_conf -- nginx configuration
* proxy_dhparam -- just holds the dhparam.pem file (this file gets copied to certs)
* proxy_vhost -- holds nginx virtual host files 
* proxy_html -- letsencrypt uses this and needs to write files to it

Anyway, logging. It's set to use syslog and that means it's going into
the logs on the host machine. It's up to you to make sure the logs
don't overflow.  I am going to be setting up log analysis as a
separate task. I wonder if I can do that in a Docker, too? Hmm.

