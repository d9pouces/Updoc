
Complete configuration
======================


Configuration options
---------------------

You can look current settings with the following command:

.. code-block:: bash

    updoc-ctl config ini -v 2

You can also display the actual list of Python settings (for more complex tweaks):

.. code-block:: bash

    updoc-ctl config python -v 2


Here is the complete list of settings:

.. code-block:: ini

  [auth]
  allow_basic_auth = true 
  	# Set to "true" if you want to allow HTTP basic auth, using the Django database.
  create_users = true 
  	# Set to "false" if users cannot create their account themselvers, or only if existing users can by authenticated by the reverse-proxy.
  ldap_bind_dn = cn=admin,dc=example,dc=com 
  	# Bind dn for LDAP authentication
  ldap_bind_password = toto 
  	# Bind password for LDAP authentication
  ldap_deny_group =  
  	# authentication is denied for users belonging to this group. Must be something like "cn=disabled,ou=groups,dc=example,dc=com".
  ldap_direct_bind = uid=%(user)s,ou=People,dc=example,dc=com 
  	# Set it for a direct LDAP bind and to skip the LDAP search, like "uid=%%(user)s,ou=users,dc=example,dc=com". %%(user)s is the only allowed variable and the double "%%" is required in .ini files.
  ldap_email_attribute =  
  	# LDAP attribute for the user's email, like "email".
  ldap_filter = (uid=%(user)s) 
  	# Filter for LDAP authentication, like "(uid=%%(user)s)" (the default), the double "%%" is required in .ini files.
  ldap_first_name_attribute = givenName 
  	# LDAP attribute for the user's first name, like "givenName".
  ldap_group_search_base = ou=Groups,dc=example,dc=com 
  	# Search base for LDAP groups, like "ou=groups,dc=example,dc=com"
  ldap_group_type = posix 
  	# Type of LDAP groups. Valid choices: "posix", "nis", "GroupOfNames", "NestedGroupOfNames", "GroupOfUniqueNames", "NestedGroupOfUniqueNames", "ActiveDirectory", "NestedActiveDirectory", "OrganizationalRole", "NestedOrganizationalRole"
  ldap_is_active_group = cn=active,ou=Groups,dc=example,dc=com 
  	# LDAP group DN for active users, like "cn=active,ou=groups,dc=example,dc=com"
  ldap_is_staff_group = cn=staff,ou=Groups,dc=example,dc=com 
  	# LDAP group DN for staff users, like "cn=staff,ou=groups,dc=example,dc=com".
  ldap_is_superuser_group = cn=superusers,ou=Groups,dc=example,dc=com 
  	# LDAP group DN for superusers, like "cn=superuser,ou=groups,dc=example,dc=com".
  ldap_last_name_attribute = sn 
  	# LDAP attribute for the user's last name, like "sn".
  ldap_mirror_groups = true 
  	# Mirror LDAP groups at each user login
  ldap_require_group = cn=active,ou=Groups,dc=example,dc=com 
  	# only authenticates users belonging to this group. Must be something like "cn=enabled,ou=groups,dc=example,dc=com".
  ldap_server_url = ldap://localhost:12389/ 
  	# URL of your LDAP server, like "ldap://ldap.example.com". Python packages "pyldap" and "django-auth-ldap" must be installed.Can be used for retrieving attributes of users authenticated by the reverse proxy
  ldap_start_tls = false 
  	# Set to "true" if you want to use StartTLS.
  ldap_user_search_base = ou=People,dc=example,dc=com 
  	# Search base for LDAP authentication by direct after an search, like "ou=users,dc=example,dc=com".
  local_users = true 
  	# Set to "false" to deactivate local database of users.
  pam = false 
  	# Set to "true" if you want to activate PAM authentication
  radius_port =  
  	# port of the Radius server.
  radius_secret =  
  	# Shared secret if the Radius server
  radius_server =  
  	# IP or FQDN of the Radius server. Python package "django-radius" is required.
  remote_user_groups = Users 
  	# Comma-separated list of groups, for new users that are automatically created when authenticated by remote_user_header. Ignored if groups are read from a LDAP server. 
  remote_user_header = HTTP_REMOTE_USER 
  	# Set it if the reverse-proxy authenticates users, a common value is "HTTP_REMOTE_USER". Note: the HTTP_ prefix is automatically added, just set REMOTE_USER in the reverse-proxy configuration. 
  session_duration = 1209600 
  	# Duration of the connection sessions (in seconds, default to 1,209,600 s / 14 days)
  social_providers =  
  	# Comma-separated OAuth2 providers, among "coinbase","amazon","paypal","persona","soundcloud","reddit","weixin","tumblr","facebook","naver","asana","foursquare","angellist","edmodo","fivehundredpx","mailchimp","stripe","flickr","untappd","line","windowslive","kakao","fxa","instagram","baidu","dropbox","github","bitly","linkedin_oauth2","robinhood","digitalocean","basecamp","evernote","feedly","slack","linkedin","openid","gitlab","twentythreeandme","shopify","hubic","spotify","xing","auth0","draugiem","daum","google","twitter","vk","discord","orcid","bitbucket_oauth2","stackexchange","bitbucket","mailru","weibo","douban","eveonline","pinterest","twitch","vimeo","odnoklassniki","dropbox_oauth2". "django-allauth" package must be installed.
  
  [cache]
  db = 2 
  	# Database number of the Redis Cache DB. 
  	# Python package "django-redis" is required.
  host = localhost 
  	# Redis Cache DB host
  password =  
  	# Redis Cache DB password (if required)
  port = 6379 
  	# Redis Cache DB port
  
  [celery]
  db = 4 
  	# Database number of the Redis Celery DB 
  	# Celery is used for processing background tasks and websockets.
  host = localhost 
  	# Redis Celery DB host
  password =  
  	# Redis Celery DB password (if required)
  port = 6379 
  	# Redis Celery DB port
  processes = 4 
  	# number of Celery processes
  
  [database]
  db = updoc 
  	# Main database name (or path of the sqlite3 database)
  engine = postgresql 
  	# Main database engine ("mysql", "postgresql", "sqlite3", "oracle", or the dotted name of the Django backend)
  host = localhost 
  	# Main database host
  password = 5trongp4ssw0rd 
  	# Main database password
  port = 5432 
  	# Main database port
  user = updoc 
  	# Main database user
  
  [elasticsearch]
  hosts =  
  	# Comma-separated list of ElasticSearch servers. 
  	# ElasticSearch can be used to index all documents but remains optional.Example: es-srv1.example.org:9200,es-srv2.example.org:9200
  index = updoc_index 
  	# Name of the ElasticSearch index
  
  [email]
  from = admin@updoc.example.org 
  	# Displayed sender email
  host = localhost 
  	# SMTP server
  password =  
  	# SMTP password
  port = 25 
  	# SMTP port (often 25, 465 or 587)
  use_ssl = false 
  	# "true" if your SMTP uses SSL (often on port 465)
  use_tls = false 
  	# "true" if your SMTP uses STARTTLS (often on port 587)
  user =  
  	# SMTP user
  
  [global]
  admin_email = admin@updoc.example.org 
  	# e-mail address for receiving logged errors
  data = $DATA_ROOT 
  	# where all data will be stored (static/uploaded/temporary files, …). If you change it, you must run the collectstatic and migrate commands again.
  language_code = fr-fr 
  	# default to fr_FR
  listen_address = localhost:8139 
  	# address used by your web server.
  log_directory = $DATA_ROOT/log/ 
  	# Write all local logs to this directory.
  log_remote_access = true 
  	# If true, log of HTTP connections are also sent to syslog/logd
  log_remote_url =  
  	# Send logs to a syslog or systemd log daemon.  
  	# Examples: syslog+tcp://localhost:514/user, syslog:///local7, syslog:///dev/log/daemon, logd:///project_name
  public_bookmarks = true 
  	# Are bookmarks publicly available?
  public_docs = true 
  	# Are documentations publicly available?
  public_index = true 
  	# Is the list of all documentations publicly available?
  public_proxies = true 
  	# Is proxy.pac file publicly available?
  server_url = http://updoc.example.org 
  	# Public URL of your website.  
  	# Default to "http://{listen_address}/" but should be different if you use a reverse proxy like Apache or Nginx. Example: http://www.example.org/.
  ssl_certfile =  
  	# Public SSL certificate (if you do not use a reverse proxy with SSL)
  ssl_keyfile =  
  	# Private SSL key (if you do not use a reverse proxy with SSL)
  time_zone = Europe/Paris 
  	# default to Europe/Paris
  use_apache = true 
  	# "true" if Apache is used as reverse-proxy with mod_xsendfile.The X-SENDFILE header must be allowed from file directories
  use_nginx = False 
  	# "true" is nginx is used as reverse-proxy with x-accel-redirect.The media directory (and url) must be allowed in the Nginx configuration.
  
  [server]
  processes = 2 
  	# The number of web server processes for handling requests.
  threads = 2 
  	# The number of web server threads for handling requests.
  timeout = 30 
  	# Web workers silent for more than this many seconds are killed and restarted.
  
  [sessions]
  db = 3 
  	# Database number of the Redis sessions DB 
  	# Python package "django-redis-sessions" is required.
  host = localhost 
  	# Redis sessions DB host
  password =  
  	# Redis sessions DB password (if required)
  port = 6379 
  	# Redis sessions DB port
  
  [websocket]
  db = 3 
  	# Database number of the Redis websocket DB
  host = localhost 
  	# Redis websocket DB host
  password =  
  	# Redis websocket DB password (if required)
  port = 6379 
  	# Redis websocket DB port
  



If you need more complex settings, you can override default values (given in `djangofloor.defaults` and
`updoc.defaults`) by creating a file named `/updoc/settings.py`.



Optional components
-------------------

Efficient page caching
~~~~~~~~~~~~~~~~~~~~~~

You just need to install `django-redis`.
Settings are automatically changed for using a local Redis server (of course, you can change it in your config file).

.. code-block:: bash

  pip install django-redis

Faster session storage
~~~~~~~~~~~~~~~~~~~~~~

You just need to install `django-redis-sessions` for storing sessions into user sessions in Redis instead of storing them in the main database.
Redis is not designed to be backuped; if you loose your Redis server, sessions are lost and all users must login again.
However, Redis is faster than your main database server and sessions take a huge place if they are not regularly cleaned.
Settings are automatically changed for using a local Redis server (of course, you can change it in your config file).

.. code-block:: bash

  pip install django-redis-sessions



Debugging
---------

If something does not work as expected, you can look at logs (check the global configuration for determining their folder)
or try to run the server interactively:

.. code-block:: bash

  sudo service supervisor stop
  sudo -H -u updoc -i
  workon updoc
  updoc-ctl check
  updoc-ctl config ini
  updoc-ctl server
  updoc-ctl worker -Q celery,slow


You can also enable the DEBUG mode which is more verbose (and displays logs to stdout):

.. code-block:: bash

  FILENAME=`easydemo-ctl config ini -v 2 | grep -m 1 ' - .ini file' | cut -d '"' -f 2 | sed  's/.ini$/.py/'`
  echo "DEBUG = True" >> $FILENAME
  updoc-ctl runserver
  updoc-ctl worker -Q celery,slow



