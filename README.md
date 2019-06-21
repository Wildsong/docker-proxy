# docker-proxy

This project uses jwilder/nginx-proxy to build a container that
will automatically add and remove reverse proxy setups using nginx
and jwilder's dockergen daemon.

It is set up to maintain and use Let's Encrypt certificates.

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
into it, so that the proxy and letsencrypt containers share the same
file and don't build a new one.

````
docker volume create proxy_dhparam
sudo cp dhparam.pem /home/docker/volumes/proxy_dhparam/_data/
docker volume create proxy_certs
sudo cp -r /etc/letsencrypt/* /home/docker/volumes/proxy_certs/_data/
````

Also I created the certs volume and copied my old /etc/letsencrypt
files into it.

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

   /home/docker/volumes/proxy_vhost/_data/
   
which is the volume mounted at /etc/nginx/vhost.d in the proxy docker.

Currently I have set up these files to accept CORS requests from ANYWHERE.


