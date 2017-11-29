Installation
============

Here is a simple tutorial to install UpDoc! on a basic Debian/Linux installation.
You should easily adapt it on a different Linux or Unix flavor.

Like many Python packages, you can use several methods to install UpDoc!.
Of course you can install it from source, but the preferred way is to install it as a standard Python package, via pip.


Upgrading
---------

If you want to upgrade an existing installation, just install the new version (with the `--upgrade` flag for `pip`) and run
the `collectstatic` and `migrate` commands (for updating both static files and the database).



Preparing the environment
-------------------------

.. code-block:: bash

    sudo adduser --disabled-password updoc
    sudo chown updoc:www-data $DATA_ROOT
    sudo apt-get install virtualenvwrapper python3.6 python3.6-dev build-essential postgresql-client libpq-dev
    sudo -u updoc -H -i
    mkvirtualenv updoc -p `which python3.6`
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
        Alias /static/ $DATA_ROOT/static/
        ProxyPass /static/ !
        <Location /static/>
            Order deny,allow
            Allow from all
            Satisfy any
        </Location>
        # CAUTION: THE FOLLOWING LINES ALLOW PUBLIC ACCESS TO ANY UPLOADED CONTENT
        Alias /media/ $DATA_ROOT/media/
        # the right value is provided by "updoc-ctl config python | grep MEDIA_ROOT"
        ProxyPass /media/ !
        <Location /media/>
            Order deny,allow
            Allow from all
            Satisfy any
        </Location>
        ProxyPass / http://localhost:8139/
        ProxyPassReverse / http://localhost:8139/
        DocumentRoot $DATA_ROOT/static/
        # the right value is provided by "updoc-ctl config python | grep STATIC_ROOT"
        ServerSignature off
        # the optional two following lines are useful
        # for keeping uploaded content  private with good performance
        XSendFile on
        XSendFilePath $DATA_ROOT/media/
        # the right value is provided by "updoc-ctl config python | grep MEDIA_ROOT"
        # in older versions of XSendFile (<= 0.9), use XSendFileAllowAbove On
    </VirtualHost>
    EOF
    sudo mkdir $DATA_ROOT
    sudo chown -R www-data:www-data $DATA_ROOT
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
        Alias /static/ $DATA_ROOT/static/
        ProxyPass /static/ !
        <Location /static/>
            Order deny,allow
            Allow from all
            Satisfy any
        </Location>
        # CAUTION: THE FOLLOWING LINES ALLOW PUBLIC ACCESS TO ANY UPLOADED CONTENT
        Alias /media/ $DATA_ROOT/media/
        # the right value is provided by "updoc-ctl config python | grep MEDIA_ROOT"
        ProxyPass /media/ !
        <Location /media/>
            Order deny,allow
            Allow from all
            Satisfy any
        </Location>
        ProxyPass / http://localhost:8139/
        ProxyPassReverse / http://localhost:8139/
        DocumentRoot $DATA_ROOT/static/
        # the right value is provided by "updoc-ctl config python | grep STATIC_ROOT"
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
        # the optional two following lines are useful
        # for private uploaded content and good performance
        XSendFile on
        XSendFilePath $DATA_ROOT/media/
        # the right value is provided by "updoc-ctl config python | grep MEDIA_ROOT"
        # in older versions of XSendFile (<= 0.9), use XSendFileAllowAbove On
            <Location /updoc/show_alt/>
            # this extra configuration is to display docs without being
            # authenticated.
                Order deny,allow
                Allow from all
                Satisfy any
            </Location>
    </VirtualHost>
    EOF
    sudo mkdir $DATA_ROOT
    sudo chown -R www-data:www-data $DATA_ROOT
    sudo a2ensite updoc.conf
    sudo apachectl -t
    sudo apachectl restart



Elasticsearch
=============

UpDoc knows how to use ElasticSearch for indexing documents.
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
The ElasticSearch index must be initialized (and existing documents indexed if you already added some documents).
ElasticSearch can be added at any time and allows to search words through all documents (instead of only looking to documents and keywords).

.. code-block:: bash

    updoc-ctl init_es



Application
-----------

Now, it's time to install UpDoc!:

.. code-block:: bash

    pip install setuptools --upgrade
    pip install pip --upgrade
    pip install updoc psycopg2
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
    updoc-ctl collectstatic --noinput
    updoc-ctl migrate
    updoc-ctl createsuperuser
    # initialize the ElasticSearch index
    updoc-ctl init_es





supervisor
----------

Supervisor can be used to automatically launch updoc:

.. code-block:: bash


    sudo apt-get install supervisor
    cat << EOF | sudo tee /etc/supervisor/conf.d/updoc.conf
    [program:updoc_aiohttp]
    command = $VIRTUAL_ENV/bin/updoc-ctl server
    user = updoc
    [program:updoc_celery_celery]
    command = $VIRTUAL_ENV/bin/updoc-ctl worker -Q celery
    user = updoc
    [program:updoc_celery_slow]
    command = $VIRTUAL_ENV/bin/updoc-ctl worker -Q slow
    user = updoc
    EOF
    sudo service supervisor stop
    sudo service supervisor start

Now, Supervisor should start updoc after a reboot.


systemd
-------

You can also use systemd (present in many modern Linux distributions) to launch updoc:

.. code-block:: bash

    cat << EOF | sudo tee /etc/systemd/system/updoc-ctl.service
    [Unit]
    Description=UpDoc! HTTP process
    After=network.target
    [Service]
    User=updoc
    Group=updoc
    WorkingDirectory=$DATA_ROOT/
    ExecStart=$VIRTUAL_ENV/bin/updoc-ctl server
    ExecReload=/bin/kill -s HUP \$MAINPID
    ExecStop=/bin/kill -s TERM \$MAINPID
    [Install]
    WantedBy=multi-user.target
    EOF
    systemctl enable updoc-ctl.service
    sudo service updoc-ctl start
    cat << EOF | sudo tee /etc/systemd/system/updoc-ctl-celery.service
    [Unit]
    Description=UpDoc! Celery process
    After=network.target
    [Service]
    User=updoc
    Group=updoc
    Type=forking
    WorkingDirectory=$DATA_ROOT/
    ExecStart=$VIRTUAL_ENV/bin/updoc-ctl worker -Q celery
    ExecReload=/bin/kill -s HUP \$MAINPID
    ExecStop=/bin/kill -s TERM \$MAINPID
    [Install]
    WantedBy=multi-user.target
    EOF
    mkdir -p /run
    sudo systemctl enable updoc-ctl.service
    sudo service updoc-ctl start
    cat << EOF | sudo tee /etc/systemd/system/updoc-ctl-slow.service
    [Unit]
    Description=UpDoc! Celery process
    After=network.target
    [Service]
    User=updoc
    Group=updoc
    Type=forking
    WorkingDirectory=$DATA_ROOT/
    ExecStart=$VIRTUAL_ENV/bin/updoc-ctl worker -Q slow
    ExecReload=/bin/kill -s HUP \$MAINPID
    ExecStop=/bin/kill -s TERM \$MAINPID
    [Install]
    WantedBy=multi-user.target
    EOF
    mkdir -p /run
    sudo systemctl enable updoc-ctl-slow.service
    sudo service updoc-ctl-slow start



