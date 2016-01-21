{% extends 'djangofloor/dev/doc/source/installation.rst' %}

{% block post_dependencies %}
  * elasticsearch>=2.0.0
  * requests
  * markdown
  * hiredis{% endblock %}

{% block webserver_ssl_extra %}            <Location /updoc/show_alt/>
                Order deny,allow
                Allow from all
                Satisfy any
            </Location>
{% endblock %}

{% block post_application %}    updoc-manage createsuperuser
    echo "CACHES = {'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}}" > $VIRTUAL_ENV/etc/updoc/settings.py
    updoc-manage init_es
{% endblock %}

{% block webserver_ssl_media %}{% endblock %}
{% block webserver_media %}{% endblock %}

{% block other_application %}Elasticsearch
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

{% endblock %}