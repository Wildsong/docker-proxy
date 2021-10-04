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

```
  networks:
    - proxy-net
  environment:
    VIRTUAL_HOST: pihole.wildsong.biz
    VIRTUAL_PORT: 80 # This is only needed if you run on a different port.
  expose:
    - "80"
```

If you want the proxy to set up an SSL certificate too then it needs more:

```
  environment:
    LETSENCRYPT_HOST: pihole.wildsong.biz
    LETSENCRYPT_MAIL: webmaster@wildsong.biz   (This line is optional but a good idea)
```

I created the dhparam volume and copied my old nginx dhparam.pem file
into it but you can let it create one for you and skip this.

```
docker volume create proxy_dhparam
sudo cp dhparam.pem /home/docker/volumes/proxy_dhparam/_data/
docker volume create proxy_certs
sudo cp -r /etc/letsencrypt/* /home/docker/volumes/proxy_certs/_data/
```

Also I created the certs volume and copied my old /etc/letsencrypt
files into it.

If you don't need to preserve old files you can just forget this and
let docker create new (empty) volumes for you.

### Swarm vs Compose

I have used Docker Compose in the testing phase for this project but I
find that the order in which containers start is important, and if I
run Docker Swarm instead then containers can die and restart a few
times until they all come online so order does not matter.

There are "depends_on" settings for Compose that will be ignored in Swarm.

2021-02-04 SWARM NOT WORKING -- because docker-gen needs to know the
containerId for nginx.  There is a PR to fix this, someday it will go
in and I can change over so FOR NOW IT'S DOCKER-COMPOSE or nothing. :-(


### Static content

My feeling currently is that there should be no attempt at serving
static content from the nginx instance here, it should only do the
reverse proxy. If you want to serve any content, manage it as a
separate project, just as you would any other application server.


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

All output directed to STDOUT and STDERR from Docker containers is
regarded as log data. I especially want to be able to analyze web logs
to see what interesting things are going on, so the docker-compose
file sets up logging.

You can check the contents of the volumes too, they are

* proxy_html -- letsencrypt uses this and needs to write files to it
* proxy_certs -- holds the letsencrypt certificates
* proxy_dhparam -- just holds the dhparam.pem file (this file gets copied to certs)

In the local space are more volumes,
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
certificate because it has to set up a connection first and then drop it.

## How to start the proxy

* Copy sample.env to .env
* Customize .env
* Launch it

```bash
SEE NOTE ABOVE on Stack VS Compose
docker stack deploy -c docker-compose.yml proxy
```

I tend to run Docker Compose in testing because it dumps out tons of
debug messages on my console.

```bash
docker-compose up
```

If it says it created a network called proxy_default you did something wrong.

### Some commands

Reload nginx reverse proxy without redeploy

    docker exec -it proxy_proxy* sh -c "nginx -s reload"

