#!/bin/bash
set -e

# base packages
sudo apt-get update
sudo apt-get upgrade --yes
sudo apt-get install --yes vim dh-make ntp rsync liblzma-dev tree
sudo apt-get install --yes python3-all-dev virtualenvwrapper \
    python3-tz python3-setuptools \
    python3-oauthlib \
    apache2 libapr1 libaprutil1 libaprutil1-dbd-sqlite3 libaprutil1-ldap \
    python-medusa python-meld3 ssl-cert python3-msgpack
source /etc/bash_completion.d/virtualenvwrapper



# create the virtual env
set +e
mkvirtualenv -p `which python3` djangofloor3
set -e
workon djangofloor3
pip install setuptools --upgrade
pip install pip --upgrade
pip install debtools djangofloor
python setup.py install



# generate packages for all dependencies
multideb -r -v -x stdeb-debian-8.cfg

# creating package for updoc
rm -rf `find * | grep pyc$`
python setup.py bdist_deb_django -x stdeb-debian-8.cfg
deb-dep-tree deb_dist/*deb
mv deb_dist/*deb deb



# install all packages
sudo dpkg -i deb/python3-*.deb

# package configuration
IP=`/sbin/ifconfig | grep -Eo 'inet (addr:|adr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'`
sudo sed -i "s/localhost/$IP/g" /etc/apache2/sites-available/updoc.conf
sudo sed -i "s/localhost/$IP/g" /etc/updoc/settings.ini
sudo a2ensite updoc.conf
sudo a2dissite 000-default.conf
sudo -u updoc updoc-manage migrate
sudo service moneta-gunicorn start
sudo service moneta-celery start
sudo service apache2 restart

set -e
