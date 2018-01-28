#!/bin/sh
echo "******************************************************"
echo "remove all containers and images and other data"
echo "******************************************************"
docker system prune -a
echo ""
echo ""
echo "******************************************************"
echo "stop docker service"
echo "******************************************************"
sudo systemctl stop docker
echo ""
echo ""
echo "******************************************************"
echo "remove files of docker settings"
echo "******************************************************"
sudo rm -rf /var/lib/docker/
echo ""
echo ""
echo "******************************************************"
echo "enable start up service"
echo "******************************************************"
sudo systemctl enable docker
echo ""
echo ""
echo "******************************************************"
echo "start docker services"
echo "******************************************************"
sudo systemctl start docker
echo ""
echo "finish"