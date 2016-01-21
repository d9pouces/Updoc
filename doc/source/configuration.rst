
Complete configuration
======================


Configuration options
---------------------

You can look current settings with the following command:

.. code-block:: bash

    updoc-manage config

Here is the complete list of settings:

.. code-block:: ini

  [database]
  engine = django.db.backends.postgresql_psycopg2
  # SQL database engine, can be 'django.db.backends.[postgresql_psycopg2|mysql|sqlite3|oracle]'.
  host = localhost
  # Empty for localhost through domain sockets or "127.0.0.1" for localhost + TCP
  name = updoc
  # Name of your database, or path to database file if using sqlite3.
  password = 5trongp4ssw0rd
  # Database password (not used with sqlite3)
  port = 5432
  # Database port, leave it empty for default (not used with sqlite3)
  user = updoc
  # Database user (not used with sqlite3)
  [elasticsearch]
  hosts = localhost:9200
  # IP:port of your ElasticSearch database, leave it empty if you do not use ElasticSearch
  index = updoc_index
  # name of your ElasticSearch index
  [global]
  admin_email = admin@updoc.example.org
  # error logs are sent to this e-mail address
  bind_address = localhost:8129
  # The socket (IP address:port) to bind to.
  data_path = /var/updoc
  # Base path for all data
  debug = False
  # A boolean that turns on/off debug mode.
  default_group = Users
  # Name of the default group for newly-created users.
  language_code = fr-fr
  # A string representing the language code for this installation.
  protocol = http
  # Protocol (or scheme) used by your webserver (apache/nginx/…, can be http or https)
  public_bookmarks = True
  # Are bookmarks publicly available?
  public_docs = True
  # Are documentations publicly available?
  public_index = True
  # Is the list of all documentations publicly available?
  public_proxies = True
  # Is proxy.pac file publicly available?
  remote_user_header = HTTP_REMOTE_USER
  # HTTP header corresponding to the username when using HTTP authentication.Should be "HTTP_REMOTE_USER". Leave it empty to disable HTTP authentication.
  secret_key = 5I0zJQuHzqcACuzGIwTAC3cV6RlZpjV8MNUETYd5KZXg6UoI4G
  # A secret key for a particular Django installation. This is used to provide cryptographic signing, and should be set to a unique, unpredictable value.
  server_name = updoc.example.org
  # the name of your webserver (should be a DNS name, but can be an IP address)
  time_zone = Europe/Paris
  # A string representing the time zone for this installation, or None. 
  x_accel_converter = False
  # Nginx only. Set it to "true" or "false"
  x_send_file = True
  # Apache and LightHTTPd only. Use the XSendFile header for sending large files.
  [redis]
  broker_db = 13
  # database name of your Celery instance
  host = localhost
  # hostname of your Redis database for Redis-based services (cache, Celery, websockets, sessions)
  port = 6379
  # port of your Redis database



If you need more complex settings, you can override default values (given in `djangofloor.defaults` and
`updoc.defaults`) by creating a file named `/home/updoc/.virtualenvs/updoc/etc/updoc/settings.py`.



Debugging
---------

If something does not work as expected, you can look at logs (in /var/log/supervisor if you use supervisor)
or try to run the server interactively:

.. code-block:: bash

  sudo service supervisor stop
  sudo -u updoc -i
  workon updoc
  updoc-manage config
  updoc-manage runserver
  updoc-gunicorn
  updoc-celery worker




Backup
------

A complete UpDoc! installation is made a different kinds of files:

    * the code of your application and its dependencies (you should not have to backup them),
    * static files (as they are provided by the code, you can lost them),
    * configuration files (you can easily recreate it, or you must backup it),
    * database content (you must backup it),
    * user-created files (you must also backup them).

Many backup strategies exist, and you must choose one that fits your needs. We can only propose general-purpose strategies.

We use logrotate to backup the database, with a new file each day.

.. code-block:: bash

  sudo mkdir -p /var/backups/updoc
  sudo chown -r updoc: /var/backups/updoc
  sudo -u updoc -i
  cat << EOF > /home/updoc/.virtualenvs/updoc/etc/updoc/backup_db.conf
  /var/backups/updoc/backup_db.sql.gz {
    daily
    rotate 20
    nocompress
    missingok
    create 640 updoc updoc
    postrotate
    myproject-manage dumpdb | gzip > /var/backups/updoc/backup_db.sql.gz
    endscript
  }
  EOF
  touch /var/backups/updoc/backup_db.sql.gz
  crontab -e
  MAILTO=admin@updoc.example.org
  0 1 * * * /home/updoc/.virtualenvs/updoc/bin/updoc-manage clearsessions
  0 2 * * * logrotate -f /home/updoc/.virtualenvs/updoc/etc/updoc/backup_db.conf


Backup of the user-created files can be done with rsync, with a full backup each month:
If you have a lot of files to backup, beware of the available disk place!

.. code-block:: bash

  sudo mkdir -p /var/backups/updoc/media
  sudo chown -r updoc: /var/backups/updoc
  cat << EOF > /home/updoc/.virtualenvs/updoc/etc/updoc/backup_media.conf
  /var/backups/updoc/backup_media.tar.gz {
    monthly
    rotate 6
    nocompress
    missingok
    create 640 updoc updoc
    postrotate
    tar -czf /var/backups/updoc/backup_media.tar.gz /var/backups/updoc/media/
    endscript
  }
  EOF
  touch /var/backups/updoc/backup_media.tar.gz
  crontab -e
  MAILTO=admin@updoc.example.org
  0 3 * * * rsync -arltDE /var/updoc/data/media/ /var/backups/updoc/media/
  0 5 0 * * logrotate -f /home/updoc/.virtualenvs/updoc/etc/updoc/backup_media.conf

Restoring a backup
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

  cat /var/backups/updoc/backup_db.sql.gz | gunzip | /home/updoc/.virtualenvs/updoc/bin/updoc-manage dbshell
  tar -C /var/updoc/data/media/ -xf /var/backups/updoc/backup_media.tar.gz





Monitoring
----------


You can use Nagios checks to monitor several points:

  * connection to the application server (gunicorn or uwsgi):
  * connection to the database servers (PostgreSQL and Redis),
  * connection to the reverse-proxy server (apache or nginx),
  * the validity of the SSL certificate (can be combined with the previous check),
  * time of the last backup (database and files),
  * living processes for gunicorn, celery, redis, postgresql, apache,
  * standard checks for RAM, disk, swap…

Here is a sample NRPE configuration file:

.. code-block:: bash

  cat << EOF | sudo tee /etc/nagios/nrpe.d/updoc.cfg
  command[updoc_wsgi]=/usr/lib/nagios/plugins/check_http -H localhost -p 8129
  command[updoc_redis]=/usr/lib/nagios/plugins/check_tcp -H localhost -p 6379
  command[updoc_database]=/usr/lib/nagios/plugins/check_tcp -H localhost -p 5432
  command[updoc_reverse_proxy]=/usr/lib/nagios/plugins/check_http -H updoc.example.org -p 80 -e 401
  command[updoc_backup_db]=/usr/lib/nagios/plugins/check_file_age -w 172800 -c 432000 /var/backups/updoc/backup_db.sql.gz
  command[updoc_backup_media]=/usr/lib/nagios/plugins/check_file_age -w 3024000 -c 6048000 /var/backups/updoc/backup_media.sql.gz
  command[updoc_gunicorn]=/usr/lib/nagios/plugins/check_procs -C python -a '/home/updoc/.virtualenvs/updoc/bin/updoc-gunicorn'
  command[updoc_celery]=/usr/lib/nagios/plugins/check_procs -C python -a '/home/updoc/.virtualenvs/updoc/bin/updoc-celery worker'
  EOF



LDAP groups
-----------

There are two possibilities to use LDAP groups, with their own pros and cons:

  * on each request, use an extra LDAP connection to retrieve groups instead of looking in the SQL database,
  * regularly synchronize groups between the LDAP server and the SQL servers.

The second approach can be used without any modification in your code and remove a point of failure
in the global architecture (if you allow some delay during the synchronization process).
A tool exists for such synchronization: `MultiSync <https://github.com/d9pouces/Multisync>`_.
