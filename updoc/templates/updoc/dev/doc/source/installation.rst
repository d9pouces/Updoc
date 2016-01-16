{% extends 'djangofloor/dev/doc/source/installation.rst' %}

{% block post_dependencies %}  * elasticsearch>=2.0.0
  * requests
  * markdown
  * hiredis{% endblock %}

{% block webserver_ssl_extra %}            <Location /updoc/show_alt/>
                Order deny,allow
                Allow from all
                Satisfy any
            </Location>
{% endblock %}

{% block post_application %}    moneta-manage createsuperuser
    echo "CACHES = {'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}}" > $VIRTUAL_ENV/etc/updoc/settings.py
    updoc-manage init_es
{% endblock %}

{% block other_application %}Elasticsearch
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

{% endblock %}