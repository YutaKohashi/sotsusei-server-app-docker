#!/bin/sh
echo "******************************************************"
echo "first migrate"
echo "******************************************************"
docker-compose exec web python manage.py migrate
echo ""
echo ""
echo "******************************************************"
echo "copy static files"
echo "******************************************************"
docker-compose run web python manage.py collectstatic --noinput
echo ""
echo ""
echo "******************************************************"
echo "create user of django admin"
echo "******************************************************"
docker-compose exec web python manage.py createsuperuser
echo ""
echo ""
echo "******************************************************"
echo "create files of migration"
echo "******************************************************"
docker-compose exec web python manage.py makemigrations
echo ""
echo ""
echo "******************************************************"
echo "second migrate"
echo "******************************************************"
docker-compose exec web python manage.py migrate
echo ""
echo "finish"