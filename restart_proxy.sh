# Likely fruitless attempt at making the proxy sync up
# with the capacity and photoshow dockers.
#
cd /home/gis/docker/proxy

# Give the photoshow and capacity servers time to start
sleep 60

# Restart the proxy so it can find photoshow and capacity
docker-compose --file docker-compose.yml restart proxy

# Actually I think it's only photoshow that is problematic

