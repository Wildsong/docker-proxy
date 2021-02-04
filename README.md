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

Create the network, I use Docker Swarm so I use an overlay network.
I make it "attachable" so that it can be shared among different apps.

```bash
   docker network create --driver=overlay --attachable proxy_net
``` 

Example for pi-hole; in the docker-compose.yml for pi-hole I have

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


### Basic Auth

Create an htpasswd file and put it in the proxy_htpasswd volume
named for the virtual_host. In other words, do something like
"cp htpasswd proxy_htpasswd/_data/whoami.DOMAIN.COM"


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

* proxy_html -- letsencrypt uses this and needs to write files to it
* proxy_certs -- holds the letsencrypt certificates
* proxy_dhparam -- just holds the dhparam.pem file (this file gets copied to certs)

In the local space are more volumes,
* html/ -- static content for webserver
* network_internal.conf -- rules on who can access this server
* vhost.d -- holds per-virtualhost config files
* nginx.tmpl --

nginx.tmpl is a file from the github repository for docker-gen.
You can copy it like this:

```bash
curl -o nginx.tmpl https://raw.githubusercontent.com/jwilder/docker-gen/master/templates/nginx.tmpl
```

and then edit it. I changed it to return a 444 instead of 503.
444 = just cut off the connection 503 = return an error page

I wanted to just drop the connection when a request for
https://YourIpAddress/ comes in but you have to send a self-signed
certificate because it has to set up a connection first and then drop
it.

## Regarding this error

    $ docker logs proxy_letsencrypt.1.jx1ski4niofyam6vj95vyxn2t
    jq: error (at <stdin>:1): Cannot iterate over null (null)
    Error: can't get docker-gen container id !
    If you are running a three containers setup, check that you are doing one of the following :
        - Set the NGINX_DOCKER_GEN_CONTAINER env var on the letsencrypt-companion container to the name of the docker-gen container.
        - Label the docker-gen container to use with 'com.github.jrcs.letsencrypt_nginx_proxy_companion.docker_gen.'

NONE OF THE SUGGESTIONS IT GIVES HELP!!

I am not running a 3 container setup. This means the nginx instance is dying,
try removing default.conf file (it's generated automatically anyway)
and start again...

The other relevant red flag is in the nginx logs and it says this

    invalid number of arguments in "upstream" directive in /etc/nginx/conf.d/default.conf


## How to start the proxy

* Copy sample.env to .env
* Customize .env
* Launch it

```bash
docker stack deploy -c docker-compose.yml proxy
```

If it says it created a network called proxy_default you did something wrong.


### Some commands

Reload nginx reverse proxy without redeploy

    docker exec -it proxy_proxy* sh -c "nginx -s reload"

