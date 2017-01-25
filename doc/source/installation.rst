Installation
============

Like many Python packages, you can use several methods to install UpDoc!.
UpDoc! designed to run with python3.5.x+.
The following packages are also required:

  * setuptools >= 3.0,
  * djangofloor >= 1.0.0,
  * elasticsearch >= 2.0.0 (optional; not installable via `"pip"`),
  * requests,
  * markdown.


Of course you can install it from the source, but the preferred way is to install it as a standard Python package, via pip.


Installing or Upgrading
-----------------------

Here is a simple tutorial to install UpDoc! on a basic Debian/Linux installation.
You should easily adapt it on a different Linux or Unix flavor.

If you want to upgrade an existing installation, just install the new version (with the `--upgrade` flag for `pip`) and run
the `collectstatic` and `migrate` commands (for updating both static files and the database).



Preparing the environment
-------------------------

.. code-block:: bash

    sudo adduser --disabled-password updoc
    sudo chown updoc:www-data $VIRTUALENV/var/updoc
    sudo apt-get install virtualenvwrapper python3.5 python3.5-dev build-essential postgresql-client libpq-dev
    sudo -u updoc -H -i
    mkvirtualenv updoc -p `which python3.5`
    workon updoc


Database
--------

PostgreSQL is often a good choice for Django sites:

.. code-block:: bash

   sudo apt-get install postgresql
   echo "CREATE USER updoc" | sudo -u postgres psql -d postgres
   echo "ALTER USER updoc WITH ENCRYPTED PASSWORD '5trongp4ssw0rd'" | sudo -u postgres psql -d postgres
   echo "ALTER ROLE updoc CREATEDB" | sudo -u postgres psql -d postgres
   echo "CREATE DATABASE updoc OWNER updoc" | sudo -u postgres psql -d postgres

UpDoc! also requires Redis for websockets, background tasks, caching pages and storing sessions:


.. code-block:: bash

    sudo apt-get install redis-server





Apache
------

Only the Apache installation is presented, but an installation behind nginx should be similar.
Only the chosen server name (like `updoc.example.org`) can be used for accessing your site. For example, you cannot use its IP address.

.. code-block:: bash

    SERVICE_NAME=updoc.example.org
    sudo apt-get install apache2 libapache2-mod-xsendfile
    sudo a2enmod headers proxy proxy_http xsendfile
    sudo a2dissite 000-default.conf
    # sudo a2dissite 000-default on Debian7
    cat << EOF | sudo tee /etc/apache2/sites-available/updoc.conf
    <VirtualHost *:80>
        ServerName $SERVICE_NAME
        Alias /static/ $VIRTUALENV/var/updoc/static/
        ProxyPass /static/ !
        <Location /static/>
            Order deny,allow
            Allow from all
            Satisfy any
        </Location>
        ProxyPass / http://127.0.0.1:8129/
        ProxyPassReverse / http://127.0.0.1:8129/
        DocumentRoot $VIRTUALENV/var/updoc/static/
        ServerSignature off
        XSendFile on
        XSendFilePath $VIRTUALENV/var/updoc/media/
        # in older versions of XSendFile (<= 0.9), use XSendFileAllowAbove On
    </VirtualHost>
    EOF
    sudo mkdir $VIRTUALENV/var/updoc
    sudo chown -R www-data:www-data $VIRTUALENV/var/updoc
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
        Alias /static/ $VIRTUALENV/var/updoc/static/
        ProxyPass /static/ !
        <Location /static/>
            Order deny,allow
            Allow from all
            Satisfy any
        </Location>
        ProxyPass / http://127.0.0.1:8129/
        ProxyPassReverse / http://127.0.0.1:8129/
        DocumentRoot $VIRTUALENV/var/updoc/static/
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
        XSendFilePath $VIRTUALENV/var/updoc/media/
        # in older versions of XSendFile (<= 0.9), use XSendFileAllowAbove On
            <Location /updoc/show_alt/>
                Order deny,allow
                Allow from all
                Satisfy any
            </Location>
    </VirtualHost>
    EOF
    sudo mkdir $VIRTUALENV/var/updoc
    sudo chown -R www-data:www-data $VIRTUALENV/var/updoc
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

Once ElasticSearch is installed, you need to configure your Updoc installation and change the `elasticsearch` section. The `hosts` value should be a list of at least one server (like `"db-es01.example.org:9200,db-es02.example.org:9200,db-es03.example.org:9200`).
The ElasticSearch index must be initialized and existing documents indexed.
ElasticSearch indexing can be added at any time and allows to search words through all documents (instead of only looking to documents and keywords).

.. code-block:: bash

    updoc-manage init_es



Application
-----------

Now, it's time to install UpDoc!:

.. code-block:: bash

    pip install setuptools --upgrade
    pip install pip --upgrade
    pip install updoc psycopg2 gevent
    mkdir -p $VIRTUAL_ENV/etc/updoc
    cat << EOF > $VIRTUAL_ENV/etc/updoc/settings.ini
    [global]
    data = $HOME/updoc
    [database]
    db = updoc
    engine = postgresql
    host = localhost
    password = 5trongp4ssw0rd
    port = 5432
    user = updoc
    EOF
    chmod 0400 $VIRTUAL_ENV/etc/updoc/settings.ini
    # protect passwords in the config files from by being readable by everyone
    updoc-manage migrate
    updoc-manage collectstatic --noinput
    updoc-manage createsuperuser
    # initialize the ElasticSearch index
    updoc-manage init_es



supervisor
----------

Supervisor is required to automatically launch updoc:

.. code-block:: bash


    sudo apt-get install supervisor
    cat << EOF | sudo tee /etc/supervisor/conf.d/updoc.conf
    [program:updoc_aiohttp]
    command = $VIRTUAL_ENV/bin/updoc-aiohttp
    user = updoc
    [program:updoc_celery_celery]
    command = $VIRTUAL_ENV/bin/updoc-celery worker -Q celery
    user = updoc
    [program:updoc_celery_slow]
    command = $VIRTUAL_ENV/bin/updoc-celery worker -Q slow
    user = updoc
    EOF
    sudo service supervisor stop
    sudo service supervisor start

Now, Supervisor should start updoc after a reboot.


systemd
-------

You can also use systemd to launch updoc:

.. code-block:: bash

    cat << EOF | sudo tee /etc/systemd/system/updoc-aiohttp.service
    [Unit]
    Description=UpDoc! aIOHTTP process
    After=network.target
    [Service]
    User=updoc
    Group=updoc
    WorkingDirectory=$VIRTUALENV/var/updoc/
    ExecStart=/bin/updoc-aiohttp
    ExecReload=/bin/kill -s HUP \$MAINPID
    ExecStop=/bin/kill -s TERM \$MAINPID
    [Install]
    WantedBy=multi-user.target
    EOF
    systemctl enable updoc-aiohttp.service
    sudo service updoc-aiohttp start
    cat << EOF | sudo tee /etc/systemd/system/updoc-celery.service
    [Unit]
    Description=UpDoc! Celery process
    After=network.target
    [Service]
    User=updoc
    Group=updoc
    Type=forking
    WorkingDirectory=$VIRTUALENV/var/updoc/
    ExecStart=$VIRTUAL_ENV/bin/updoc-celery worker -Q celery
    ExecReload=/bin/kill -s HUP \$MAINPID
    ExecStop=/bin/kill -s TERM \$MAINPID
    [Install]
    WantedBy=multi-user.target
    EOF
    mkdir -p /run
    sudo systemctl enable updoc-celery.service
    sudo service updoc-celery start
    cat << EOF | sudo tee /etc/systemd/system/updoc-celery-slow.service
    [Unit]
    Description=UpDoc! Celery process
    After=network.target
    [Service]
    User=updoc
    Group=updoc
    Type=forking
    WorkingDirectory=$VIRTUALENV/var/updoc/
    ExecStart=$VIRTUAL_ENV/bin/updoc-celery worker -Q slow
    ExecReload=/bin/kill -s HUP \$MAINPID
    ExecStop=/bin/kill -s TERM \$MAINPID
    [Install]
    WantedBy=multi-user.target
    EOF
    mkdir -p /run
    sudo systemctl enable updoc-celery-slow.service
    sudo service updoc-celery-slow start



