# docker-proxy

I am using jwilder/nginx-proxy to automatically add and remove
reverse proxy setups in nginx.

Each participating container needs 3 things.

* It needs to define VIRTUAL_HOST with a unique name, because the proxy
uses that name to create its entry for the service.
* It needs to use proxy_net as its network so that the proxy can see the service
* It needs to EXPOSE the port you want to proxy.

For example I run pi-hole so in the docker-compose.yml for pi-hole I have


## Start the proxy with

docker-compose up



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
/etc/ssl/dhparams.pem
````
My certificates are not checked into github for obvious reasons.

### CORS support

I put the configuration to generate the right HTTP headers to avoid
Cross Origin Scripting (CORS) error messages into the nginx proxy, see
nginx/proxy.d/geoserver.conf It seems to be working with Chrome and
Firefox on Windows.
