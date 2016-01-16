Installation
============

Like many Python packages, you can use several methods to install UpDoc!.
The following packages are required:

  * setuptools >= 3.0
  * djangofloor >= 0.17.0  * elasticsearch>=2.0.0
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

    sudo apt-get install apache2 libapache2-mod-xsendfile
    sudo a2enmod headers proxy proxy_http
    sudo a2dissite 000-default.conf
    # sudo a2dissite 000-default on Debian7
    SERVICE_NAME=updoc.example.org
    PROJECT_NAME=updoc
    BIND_ADRESS=localhost:8129
    cat << EOF | sudo tee /etc/apache2/sites-available/updoc.conf
    <VirtualHost *:80>
        ServerName $SERVICE_NAME
        Alias /static/ /var/updoc/static/
        ProxyPass /static/ !
        Alias /media/ /var/updoc/media/
        ProxyPass /media/ !
        ProxyPass / http://localhost:8129/
        ProxyPassReverse / http://localhost:8129/
        DocumentRoot /var/updoc/static
        ServerSignature off
        XSendFile on
        XSendFilePath /var/updoc/media/
        # in older versions of XSendFile (<= 0.9), use XSendFileAllowAbove On
    </VirtualHost>
    EOF
    sudo mkdir /var/updoc/
    sudo chown -R www-data:www-data /var/updoc/
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
    PROJECT_NAME=updoc
    BIND_ADRESS=localhost:8129
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
        Alias /media/ /var/updoc/media/
        ProxyPass /media/ !
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
        <Location /static/>
            Order deny,allow
            Allow from all
            Satisfy any
        </Location>
        XSendFile on
        XSendFilePath /var/updoc/media/
        # in older versions of XSendFile (<= 0.9), use XSendFileAllowAbove On
            <Location /updoc/show_alt/>
                Order deny,allow
                Allow from all
                Satisfy any
            </Location>
    </VirtualHost>
    EOF
    sudo mkdir /var/updoc/
    sudo chown -R www-data:www-data /var/updoc/
    sudo a2ensite updoc.conf
    sudo apachectl -t
    sudo apachectl restart



Elasticsearch
=============

UpDoc uses ElasticSearch to index documents.
If you have a recent Debian/Ubuntu distribution, you can directly install ElasticSearch.

.. code-block:: bash

    sudo apt-get install elasticsearch


.. code-block:: bash

    cat << EOF | sudo apt-key add -
    -----BEGIN PGP PUBLIC KEY BLOCK-----
    Version: GnuPG v2.0.14 (GNU/Linux)

    mQENBFI3HsoBCADXDtbNJnxbPqB1vDNtCsqhe49vFYsZN9IOZsZXgp7aHjh6CJBD
    A+bGFOwyhbd7at35jQjWAw1O3cfYsKAmFy+Ar3LHCMkV3oZspJACTIgCrwnkic/9
    CUliQe324qvObU2QRtP4Fl0zWcfb/S8UYzWXWIFuJqMvE9MaRY1bwUBvzoqavLGZ
    j3SF1SPO+TB5QrHkrQHBsmX+Jda6d4Ylt8/t6CvMwgQNlrlzIO9WT+YN6zS+sqHd
    1YK/aY5qhoLNhp9G/HxhcSVCkLq8SStj1ZZ1S9juBPoXV1ZWNbxFNGwOh/NYGldD
    2kmBf3YgCqeLzHahsAEpvAm8TBa7Q9W21C8vABEBAAG0RUVsYXN0aWNzZWFyY2gg
    KEVsYXN0aWNzZWFyY2ggU2lnbmluZyBLZXkpIDxkZXZfb3BzQGVsYXN0aWNzZWFy
    Y2gub3JnPokBOAQTAQIAIgUCUjceygIbAwYLCQgHAwIGFQgCCQoLBBYCAwECHgEC
    F4AACgkQ0n1mbNiOQrRzjAgAlTUQ1mgo3nK6BGXbj4XAJvuZDG0HILiUt+pPnz75
    nsf0NWhqR4yGFlmpuctgCmTD+HzYtV9fp9qW/bwVuJCNtKXk3sdzYABY+Yl0Cez/
    7C2GuGCOlbn0luCNT9BxJnh4mC9h/cKI3y5jvZ7wavwe41teqG14V+EoFSn3NPKm
    TxcDTFrV7SmVPxCBcQze00cJhprKxkuZMPPVqpBS+JfDQtzUQD/LSFfhHj9eD+Xe
    8d7sw+XvxB2aN4gnTlRzjL1nTRp0h2/IOGkqYfIG9rWmSLNlxhB2t+c0RsjdGM4/
    eRlPWylFbVMc5pmDpItrkWSnzBfkmXL3vO2X3WvwmSFiQbkBDQRSNx7KAQgA5JUl
    zcMW5/cuyZR8alSacKqhSbvoSqqbzHKcUQZmlzNMKGTABFG1yRx9r+wa/fvqP6OT
    RzRDvVS/cycws8YX7Ddum7x8uI95b9ye1/Xy5noPEm8cD+hplnpU+PBQZJ5XJ2I+
    1l9Nixx47wPGXeClLqcdn0ayd+v+Rwf3/XUJrvccG2YZUiQ4jWZkoxsA07xx7Bj+
    Lt8/FKG7sHRFvePFU0ZS6JFx9GJqjSBbHRRkam+4emW3uWgVfZxuwcUCn1ayNgRt
    KiFv9jQrg2TIWEvzYx9tywTCxc+FFMWAlbCzi+m4WD+QUWWfDQ009U/WM0ks0Kww
    EwSk/UDuToxGnKU2dQARAQABiQEfBBgBAgAJBQJSNx7KAhsMAAoJENJ9ZmzYjkK0
    c3MIAIE9hAR20mqJWLcsxLtrRs6uNF1VrpB+4n/55QU7oxA1iVBO6IFu4qgsF12J
    TavnJ5MLaETlggXY+zDef9syTPXoQctpzcaNVDmedwo1SiL03uMoblOvWpMR/Y0j
    6rm7IgrMWUDXDPvoPGjMl2q1iTeyHkMZEyUJ8SKsaHh4jV9wp9KmC8C+9CwMukL7
    vM5w8cgvJoAwsp3Fn59AxWthN3XJYcnMfStkIuWgR7U2r+a210W6vnUxU4oN0PmM
    cursYPyeV0NX/KQeUeNMwGTFB6QHS/anRaGQewijkrYYoTNtfllxIu9XYmiBERQ/
    qPDlGRlOgVTd9xUfHFkzB52c70E=
    =92oX
    -----END PGP PUBLIC KEY BLOCK-----
    EOF
    echo "deb http://packages.elastic.co/elasticsearch/1.5/debian stable main" | sudo tee /etc/apt/sources.list.d/elasticsearch.list
    sudo apt-get update
    sudo apt-get install openjdk-7-jre-headless elasticsearch
    sudo chown elasticsearch:elasticsearch /usr/share/elasticsearch
    sudo sed -i -s 's%#LOG_DIR=/var/log/elasticsearch%LOG_DIR=/var/log/elasticsearch%' /etc/default/elasticsearch
    sudo sed -i -s 's%#DATA_DIR=/var/lib/elasticsearch%DATA_DIR=/var/lib/elasticsearch%' /etc/default/elasticsearch
    sudo sed -i -s 's%#WORK_DIR=/tmp/elasticsearch%WORK_DIR=/tmp/elasticsearch%' /etc/default/elasticsearch
    sudo sed -i -s 's%#CONF_DIR=/etc/elasticsearch%CONF_DIR=/etc/elasticsearch%' /etc/default/elasticsearch
    sudo sed -i -s 's%#CONF_FILE=/etc/elasticsearch/elasticsearch.yml%CONF_FILE=/etc/elasticsearch/elasticsearch.yml%' /etc/default/elasticsearch
    sudo sed -i -s 's%#network.bind_host: 192.168.0.1%network.bind_host: 127.0.0.1%' /etc/elasticsearch/elasticsearch.yml
    # if you still use IP v.4
    echo 'JAVA_OPTS="$JAVA_OPTS -Djava.net.preferIPv4Stack=true"' | sudo tee -a /usr/share/elasticsearch/bin/elasticsearch.in.sh

    sudo /bin/systemctl daemon-reload
    sudo /bin/systemctl enable elasticsearch.service
    sudo /bin/systemctl start elasticsearch.service


On Debian 7, you probably should use something like::

.. code-block:: bash

    sudo update-rc.d elasticsearch defaults 95 10
    sudo /etc/init.d/elasticsearch start


Application
-----------

Now, it's time to install UpDoc!:

.. code-block:: bash

    SERVICE_NAME=updoc.example.org
    PROJECT_NAME=updoc
    BIND_ADRESS=localhost:8129
    sudo mkdir -p /var/updoc
    sudo adduser --disabled-password updoc
    sudo chown updoc:www-data /var/updoc
    sudo apt-get install virtualenvwrapper python3.4 python3.4-dev build-essential postgresql-client libpq-dev
    # application
    sudo -u updoc -i
    SERVICE_NAME=updoc.example.org
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
    name = $PROJECT_NAME
    password = 5trongp4ssw0rd
    port = 5432
    user = $PROJECT_NAME
    [elasticsearch]
    hosts = localhost:9200
    index = updoc_index
    [global]
    admin_email = admin@$SERVICE_NAME
    bind_address = $BIND_ADDRESS
    data_path = /var/$PROJECT_NAME
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
    server_name = $SERVICE_NAME
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
    moneta-manage createsuperuser
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
    sudo /etc/init.d/supervisor restart

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



