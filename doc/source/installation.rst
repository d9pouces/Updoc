Installing / Upgrading
======================

Here is a simple tutorial to install Updoc on a basic Debian/Linux installation.
You should easily adapt it on a different Linux or Unix flavor.

Let's start by defining some variables::

        SERVICE_NAME=updoc.example.com

Database
--------

PostgreSQL is traditionnaly a good choice for Django::

        sudo apt-get install postgresql libpq-dev
        echo "CREATE USER updoc" | sudo -u postgres psql -d postgres
        echo "ALTER USER updoc WITH ENCRYPTED PASSWORD 'upd0c-5trongp4ssw0rd'" | sudo -u postgres psql -d postgres
        echo "ALTER ROLE updoc CREATEDB" | sudo -u postgres psql -d postgres
        echo "CREATE DATABASE updoc OWNER updoc" | sudo -u postgres psql -d postgres

Updoc also requires Redis::

        sudo apt-get install redis-server

Apache
------

I only present the installation with Apache, but an installation behind nginx should be similar.::

        sudo apt-get install apache2 libapache2-mod-xsendfile
        sudo a2enmod headers proxy proxy_http
        SERVICE_NAME=updoc.example.com
        cat << EOF | sudo tee /etc/apache2/sites-available/updoc.conf
        <VirtualHost *:80>
            ServerName $SERVICE_NAME
            Alias /static/ /var/updoc/static/
            Alias /media/ /var/updoc/media/
            ProxyPass /static/ !
            ProxyPass /media/ !
            ProxyPass / http://localhost:8129/
            ProxyPassReverse / http://localhost:8129/
            DocumentRoot /var/updoc/
            ProxyIOBufferSize 65536
            ServerSignature off
            XSendFile on
            XSendFilePath /var/updoc/media/
            # in older versions of XSendFile (<= 0.9), use XSendFileAllowAbove On
            <Location /static/>
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

If you want Kerberos authentication and SSL::

        sudo apt-get install apache2 libapache2-mod-xsendfile libapache2-mod-auth-kerb
        PEM=/etc/apache2/`hostname -f`.pem
        KEYTAB=/etc/apache2/http.`hostname -f`.keytab
        # ok, I assume that you already have your certificate and your keytab
        sudo a2enmod auth_kerb headers proxy proxy_http ssl
        openssl x509 -text -noout < $PEM
        cat << EOF | sudo ktutil
        rkt $KEYTAB
        list
        quit
        EOF
        sudo chown www-data $PEM $KEYTAB
        sudo chmod 0400 $PEM $KEYTAB

        cat << EOF | sudo tee /etc/apache2/sites-available/updoc.conf
        <VirtualHost *:80>
            ServerName $SERVICE_NAME
            RedirectPermanent / https://$SERVICE_NAME/
        </VirtualHost>
        <VirtualHost *:80>
            ServerName $SERVICE_NAME
            SSLCertificateFile $PEM
            SSLEngine on
            Alias /static/ /var/updoc/static/
            Alias /media/ /var/updoc/media/
            ProxyPass /static/ !
            ProxyPass /media/ !
            ProxyPass / http://localhost:8129/
            ProxyPassReverse / http://localhost:8129/
            DocumentRoot /var/updoc/
            ProxyIOBufferSize 65536
            ServerSignature off
            RequestHeader set X_FORWARDED_PROTO https
            <Location />
                Options +FollowSymLinks +Indexes
                AuthType Kerberos
                AuthName "Updoc"
                KrbAuthRealms INTRANET.com interne.com
                Krb5Keytab $KEYTAB
                KrbLocalUserMapping On
                KrbServiceName HTTP
                KrbMethodK5Passwd Off
                KrbMethodNegotiate On
                KrbSaveCredentials On
                Require valid-user
            </Location>
            <Location /updoc/show_alt/>
                Order deny,allow
                Allow from all
                Satisfy any
            </Location>
            XSendFile on
            XSendFilePath /var/updoc/data/media/
            # in older versions of XSendFile (<= 0.9), use XSendFileAllowAbove On
            <Location /static/>
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


ElasticSearch
-------------

UpDoc uses ElasticSearch to index documents.::

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
        sudo /bin/systemctl daemon-reload
        sudo /bin/systemctl enable elasticsearch.service
        sudo sed -i -s 's%#LOG_DIR=/var/log/elasticsearch%LOG_DIR=/var/log/elasticsearch%' /etc/default/elasticsearch
        sudo sed -i -s 's%#DATA_DIR=/var/lib/elasticsearch%DATA_DIR=/var/lib/elasticsearch%' /etc/default/elasticsearch
        sudo sed -i -s 's%#WORK_DIR=/tmp/elasticsearch%WORK_DIR=/tmp/elasticsearch%' /etc/default/elasticsearch
        sudo sed -i -s 's%#CONF_DIR=/etc/elasticsearch%CONF_DIR=/etc/elasticsearch%' /etc/default/elasticsearch
        sudo sed -i -s 's%#CONF_FILE=/etc/elasticsearch/elasticsearch.yml%CONF_FILE=/etc/elasticsearch/elasticsearch.yml%' /etc/default/elasticsearch
        sudo sed -i -s 's%#network.bind_host: 192.168.0.1%network.bind_host: 127.0.0.1%' /etc/elasticsearch/elasticsearch.yml
        echo 'JAVA_OPTS="$JAVA_OPTS -Djava.net.preferIPv4Stack=true"' | sudo tee -a /usr/share/elasticsearch/bin/elasticsearch.in.sh

        sudo /bin/systemctl start elasticsearch.service


On Debian 7, you probably should use something like::

        sudo update-rc.d elasticsearch defaults 95 10
        sudo /etc/init.d/elasticsearch start


Application
-----------

Now, it's time to install UpDoc::

        sudo mkdir -p /var/updoc
        adduser --disabled-password updoc
        sudo chown updoc:www-data /var/updoc
        sudo apt-get install virtualenvwrapper python3.4 supervisor python3.4-dev build-essential postgresql-client
        # application
        sudo -u updoc -i
        SERVICE_NAME=updoc.example.com
        mkvirtualenv updoc -p `which python3.4`
        pip install setuptools --upgrade
        pip install pip --upgrade
        pip install updoc psycopg2
        mkdir -p $VIRTUAL_ENV/etc/updoc
        cat << EOF > $VIRTUAL_ENV/etc/updoc/settings.ini
        [global]
        server_name = $SERVICE_NAME
        protocol = http
        ; use https if your Apache uses SSL
        bind_address = 127.0.0.1:8129
        data_path = /var/updoc
        admin_email = admin@$SERVICE_NAME
        time_zone = Europe/Paris
        language_code = fr-fr
        x_send_file =  true
        x_accel_converter = false
        public_bookmarks = true
        public_proxies = true
        public_index = true
        public_docs = true
        remote_user_header = HTTP_REMOTE_USER
        ; leave it blank if you do not use kerberos

        [elasticsearch]
        hosts = 127.0.0.1:9200
        index = updoc

        [redis]
        host = 127.0.0.1
        port = 6379

        [database]
        engine = django.db.backends.postgresql_psycopg2
        name = updoc
        user = updoc
        password = upd0c-5trongp4ssw0rd
        host = localhost
        port = 5432
        EOF

        updoc-manage collectstatic --noinput
        updoc-manage migrate auth
        # this command will finish in error :(
        updoc-manage migrate sites
        updoc-manage migrate auth
        updoc-manage migrate
        updoc-manage init_es
        updoc-manage collectstatic --noinput
        updoc-manage createsuperuser

supervisor
----------

Supervisor is required to automatically launch updoc::

        sudo apt-get install supervisor
        cat << EOF | sudo tee /etc/supervisor/conf.d/updoc.conf
        [program:updoc_gunicorn]
        command = $VIRTUAL_ENV/bin/updoc-gunicorn
        user = updoc
        [program:updoc_celery]
        command = $VIRTUAL_ENV/bin/updoc-celery worker
        user = updoc
        EOF

Now, Supervisor should start updoc after a reboot.