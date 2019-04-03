# docker-proxy

This project uses jwilder/nginx-proxy to build a container that
will automatically add and remove reverse proxy setups using nginx
and jwilder's dockergen daemon.

It is set up to maintain and use Let's Encrypt certificates.

Each container to be proxied needs 3 things.

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

If you want it to use a certificate it needs more:

````
    environment:
      LETSENCRYPT_HOST: pihole.wildsong.biz
      LETSENCRYPT_MAIL: webmaster@wildsong.biz   (optional but a good idea)
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
HTTP headers to avoid Cross Origin Scripting (CORS) error messages,
see nginx/proxy.d/cors.conf It seems to be working with Chrome and
Firefox on Windows.

-----------THIS IS OLD I need to update it for nginx-proxy--------------

### SSL sort of works

Initially I set this project up to support SSL certificates but I've
decided not to worry about them. The way I implemented it was by
setting the certificates up on the proxy. This almost works but it
made the GeoServer layer preview feature fail. I have spent too much
time chasing down how to fix it (and similar problems caused by
proxies) so I've deactivated it for now.

If you want to try it anyway (for instance you don't care about layer
preview), copy your SSL certificates into the nginx/ directory and
uncomment the relevant lines in the nginx/Dockerfile and
nginx/virtualhost.conf.j2; it should be pretty obvious.

The certificates I used during testing were created by
certbot and live here as installed on the host:
````
/etc/letsencrypt/live/maps.wildsong.biz/fullchain.pem
/etc/letsencrypt/live/maps.wildsong.biz/privkey.pem
````
My certificates are not checked into github for obvious reasons.


