Installation
============

Like many Python packages, you can use several methods to install UpDoc!.
The following packages are required:

  * setuptools >= 3.0
  * djangofloor >= 0.18.0
  * elasticsearch>=2.0.0
  * requests
  * markdown
  * hiredis

Installing or Upgrading
-----------------------

Here is a simple tutorial to install UpDoc! on a basic Debian/Linux installation.
You should easily adapt it on a different Linux or Unix flavor.


Database
--------

PostgreSQL is often a good choice for Django sites:

.. code-block:: bash

   sudo apt-get install postgresql
   echo "CREATE USER updoc" | sudo -u postgres psql -d postgres
   echo "ALTER USER updoc WITH ENCRYPTED PASSWORD '5trongp4ssw0rd'" | sudo -u postgres psql -d postgres
   echo "ALTER ROLE updoc CREATEDB" | sudo -u postgres psql -d postgres
   echo "CREATE DATABASE updoc OWNER updoc" | sudo -u postgres psql -d postgres


UpDoc! also requires Redis:

.. code-block:: bash

    sudo apt-get install redis-server





Apache
------

I only present the installation with Apache, but an installation behind nginx should be similar.
You cannot use different server names for browsing your mirror. If you use `updoc.example.org`
in the configuration, you cannot use its IP address to access the website.

.. code-block:: bash

    SERVICE_NAME=updoc.example.org
    sudo apt-get install apache2 libapache2-mod-xsendfile
    sudo a2enmod headers proxy proxy_http
    sudo a2dissite 000-default.conf
    # sudo a2dissite 000-default on Debian7
    cat << EOF | sudo tee /etc/apache2/sites-available/updoc.conf
    <VirtualHost *:80>
        ServerName $SERVICE_NAME
        Alias /static/ /var/updoc/static/
        ProxyPass /static/ !
        <Location /static/>
            Order deny,allow
            Allow from all
            Satisfy any
        </Location>
        ProxyPass / http://localhost:8129/
        ProxyPassReverse / http://localhost:8129/
        DocumentRoot /var/updoc/static
        ServerSignature off
        XSendFile on
        XSendFilePath /var/updoc/data/media
        # in older versions of XSendFile (<= 0.9), use XSendFileAllowAbove On
    </VirtualHost>
    EOF
    sudo mkdir /var/updoc
    sudo chown -R www-data:www-data /var/updoc
    sudo a2ensite updoc.conf
    sudo apachectl -t
    sudo apachectl restart


If you want to use SSL:

.. code-block:: bash

    sudo apt-get install apache2 libapache2-mod-xsendfile
    PEM=/etc/apache2/`hostname -f`.pem
    # ok, I assume that you already have your certificate
    sudo a2enmod headers proxy proxy_http ssl
    openssl x509 -text -noout < $PEM
    sudo chown www-data $PEM
    sudo chmod 0400 $PEM

    sudo apt-get install libapache2-mod-auth-kerb
    KEYTAB=/etc/apache2/http.`hostname -f`.keytab
    # ok, I assume that you already have your keytab
    sudo a2enmod auth_kerb
    cat << EOF | sudo ktutil
    rkt $KEYTAB
    list
    quit
    EOF
    sudo chown www-data $KEYTAB
    sudo chmod 0400 $KEYTAB

    SERVICE_NAME=updoc.example.org
    cat << EOF | sudo tee /etc/apache2/sites-available/updoc.conf
    <VirtualHost *:80>
        ServerName $SERVICE_NAME
        RedirectPermanent / https://$SERVICE_NAME/
    </VirtualHost>
    <VirtualHost *:443>
        ServerName $SERVICE_NAME
        SSLCertificateFile $PEM
        SSLEngine on
        Alias /static/ /var/updoc/static/
        ProxyPass /static/ !
        <Location /static/>
            Order deny,allow
            Allow from all
            Satisfy any
        </Location>
        ProxyPass / http://localhost:8129/
        ProxyPassReverse / http://localhost:8129/
        DocumentRoot /var/updoc/static
        ServerSignature off
        RequestHeader set X_FORWARDED_PROTO https
        <Location />
            AuthType Kerberos
            AuthName "UpDoc!"
            KrbAuthRealms EXAMPLE.ORG example.org
            Krb5Keytab $KEYTAB
            KrbLocalUserMapping On
            KrbServiceName HTTP
            KrbMethodK5Passwd Off
            KrbMethodNegotiate On
            KrbSaveCredentials On
            Require valid-user
            RequestHeader set REMOTE_USER %{REMOTE_USER}s
        </Location>
        XSendFile on
        XSendFilePath /var/updoc/data/media
        # in older versions of XSendFile (<= 0.9), use XSendFileAllowAbove On
            <Location /updoc/show_alt/>
                Order deny,allow
                Allow from all
                Satisfy any
            </Location>
    </VirtualHost>
    EOF
    sudo mkdir /var/updoc
    sudo chown -R www-data:www-data /var/updoc
    sudo a2ensite updoc.conf
    sudo apachectl -t
    sudo apachectl restart



Elasticsearch
=============

UpDoc uses ElasticSearch to index documents.
If you have a recent Debian/Ubuntu distribution, you can directly install ElasticSearch.

.. code-block:: bash

    sudo apt-get install elasticsearch

Otherwise, you should install a more recent version from their official repository:

.. code-block:: bash

    wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
    echo "deb http://packages.elastic.co/elasticsearch/1.7/debian stable main" | sudo tee /etc/apt/sources.list.d/elasticsearch.list
    sudo apt-get update
    sudo apt-get install openjdk-7-jre-headless elasticsearch
    sudo /bin/systemctl daemon-reload
    sudo /bin/systemctl enable elasticsearch.service
    sudo service elasticsearch start


On Debian 7, you probably should use something like:

.. code-block:: bash

    sudo update-rc.d elasticsearch defaults 95 10
    sudo /etc/init.d/elasticsearch start


Application
-----------

Now, it's time to install UpDoc!:

.. code-block:: bash

    sudo mkdir -p /var/updoc
    sudo adduser --disabled-password updoc
    sudo chown updoc:www-data /var/updoc
    sudo apt-get install virtualenvwrapper python3.4 python3.4-dev build-essential postgresql-client libpq-dev
    # application
    sudo -u updoc -i
    mkvirtualenv updoc -p `which python3.4`
    workon updoc
    pip install setuptools --upgrade
    pip install pip --upgrade
    pip install updoc psycopg2
    mkdir -p $VIRTUAL_ENV/etc/updoc
    cat << EOF > $VIRTUAL_ENV/etc/updoc/settings.ini
    [database]
    engine = django.db.backends.postgresql_psycopg2
    host = localhost
    name = updoc
    password = 5trongp4ssw0rd
    port = 5432
    user = updoc
    [elasticsearch]
    hosts = localhost:9200
    index = updoc_index
    [global]
    admin_email = admin@updoc.example.org
    bind_address = localhost:8129
    data_path = /var/updoc
    debug = False
    default_group = Users
    language_code = fr-fr
    protocol = http
    public_bookmarks = True
    public_docs = True
    public_index = True
    public_proxies = True
    remote_user_header = HTTP_REMOTE_USER
    secret_key = 5I0zJQuHzqcACuzGIwTAC3cV6RlZpjV8MNUETYd5KZXg6UoI4G
    server_name = updoc.example.org
    time_zone = Europe/Paris
    x_accel_converter = False
    x_send_file = True
    [redis]
    broker_db = 13
    host = localhost
    port = 6379
    EOF
    updoc-manage migrate
    updoc-manage collectstatic --noinput
    updoc-manage createsuperuser
    echo "CACHES = {'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}}" > $VIRTUAL_ENV/etc/updoc/settings.py
    updoc-manage init_es



supervisor
----------

Supervisor is required to automatically launch updoc:

.. code-block:: bash


    sudo apt-get install supervisor
    cat << EOF | sudo tee /etc/supervisor/conf.d/updoc.conf
    [program:updoc_gunicorn]
    command = /home/updoc/.virtualenvs/updoc/bin/updoc-gunicorn
    user = updoc
    [program:updoc_celery]
    command = /home/updoc/.virtualenvs/updoc/bin/updoc-celery worker
    user = updoc
    EOF
    sudo service supervisor stop
    sudo service supervisor start

Now, Supervisor should start updoc after a reboot.


systemd
-------

You can also use systemd to launch updoc:

.. code-block:: bash

    cat << EOF | sudo tee /etc/systemd/system/updoc-gunicorn.service
    [Unit]
    Description=UpDoc! Gunicorn process
    After=network.target
    [Service]
    User=updoc
    Group=updoc
    WorkingDirectory=/var/updoc/
    ExecStart=/home/updoc/.virtualenvs/updoc/bin/updoc-gunicorn
    ExecReload=/bin/kill -s HUP $MAINPID
    ExecStop=/bin/kill -s TERM $MAINPID
    [Install]
    WantedBy=multi-user.target
    EOF
    systemctl enable updoc-gunicorn.service
    cat << EOF | sudo tee /etc/systemd/system/updoc-celery.service
    [Unit]
    Description=UpDoc! Celery process
    After=network.target
    [Service]
    User=updoc
    Group=updoc
    WorkingDirectory=/var/updoc/
    ExecStart=/home/updoc/.virtualenvs/updoc/bin/updoc-celery worker
    ExecReload=/bin/kill -s HUP $MAINPID
    ExecStop=/bin/kill -s TERM $MAINPID
    [Install]
    WantedBy=multi-user.target
    EOF
    systemctl enable updoc-celery.service



