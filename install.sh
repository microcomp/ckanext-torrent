#!/bin/bash

yum install -y transmission
yum install -y supervisor
cp celery-supervisor.ini /etc/supervisord.d/
service supervisord start
/usr/lib/ckan/default/bin/paster --plugin=ckanext-torrent torrent-cmd createAll --config=/etc/ckan/default/development.ini