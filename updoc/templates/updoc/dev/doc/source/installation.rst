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

sudo chown elasticsearch:elasticsearch /usr/share/elasticsearch
sudo sed -i -s 's%#LOG_DIR=/var/log/elasticsearch%LOG_DIR=/var/log/elasticsearch%' /etc/default/elasticsearch
sudo sed -i -s 's%#DATA_DIR=/var/lib/elasticsearch%DATA_DIR=/var/lib/elasticsearch%' /etc/default/elasticsearch
sudo sed -i -s 's%#WORK_DIR=/tmp/elasticsearch%WORK_DIR=/tmp/elasticsearch%' /etc/default/elasticsearch
sudo sed -i -s 's%#CONF_DIR=/etc/elasticsearch%CONF_DIR=/etc/elasticsearch%' /etc/default/elasticsearch
sudo sed -i -s 's%#CONF_FILE=/etc/elasticsearch/elasticsearch.yml%CONF_FILE=/etc/elasticsearch/elasticsearch.yml%' /etc/default/elasticsearch
sudo sed -i -s 's%#network.bind_host: 192.168.0.1%network.bind_host: 127.0.0.1%' /etc/elasticsearch/elasticsearch.yml
# if you still use IP v.4
echo 'JAVA_OPTS="$JAVA_OPTS -Djava.net.preferIPv4Stack=true"' | sudo tee -a /usr/share/elasticsearch/bin/elasticsearch.in.sh

On Debian 7, you probably should use something like:

.. code-block:: bash

    sudo update-rc.d elasticsearch defaults 95 10
    sudo /etc/init.d/elasticsearch start

{% endblock %}