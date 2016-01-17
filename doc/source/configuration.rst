Complete configuration
======================

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
`updoc.defaults`) by creating a file named `[prefix]/etc/updoc/settings.py`.

Valid engines for your database are:

  - `django.db.backends.sqlite3` (use the `name` option for its filepath)
  - `django.db.backends.postgresql_psycopg2`
  - `django.db.backends.mysql`
  - `django.db.backends.oracle`

Use `x_send_file` with Apache, and `x_accel_converter` with nginx.

Debugging
---------

If something does not work as expected, you can look at logs (in /var/log/supervisor if you use supervisor)
or try to run the server interactively:

.. code-block:: bash

  sudo service supervisor stop
  sudo -u updoc -i
  workon updoc
  updoc-manage runserver
  updoc-gunicorn
  updoc-celery worker
