Quick installation
==================

UpDoc! mainly requires Python (3.5) and a Redis server for background tasks.

You should create a dedicated virtualenvironment on your system to isolate UpDoc!.
You can use `pipenv <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_ or `virtualenvwrapper <https://virtualenvwrapper.readthedocs.io>`_.

For example, on Debian-based systems like Ubuntu:

.. code-block:: bash

    sudo apt-get install python3.6 python3.6-dev build-essential redis-server






If these requirements are fullfilled, then you can gon on and install UpDoc!:

.. code-block:: bash

    pip install updoc --user
    updoc-ctl collectstatic --noinput  # prepare static files (CSS, JS, …)
    updoc-ctl migrate  # create the database (SQLite by default)
    updoc-ctl createsuperuser  # create an admin user
    updoc-ctl check  # everything should be ok




You can easily change the root location for all data (SQLite database, uploaded or temp files, static files, …) by
editing the configuration file.

.. code-block:: bash

    CONFIG_FILENAME=`updoc-ctl config ini -v 2 | grep -m 1 ' - .ini file' | cut -d '"' -f 2`
    # prepare a limited configuration file
    cat << EOF > $FILENAME
    [global]
    data = $HOME/updoc
    EOF

Of course, you must run again the `migrate` and `collectstatic` commands (or moving data to this new folder).




You can launch the server processes (the second process is required for background tasks):

.. code-block:: bash

    updoc-ctl server
    updoc-ctl worker -Q celery,slow


Then open http://localhost:8139 with your favorite browser.



You can install UpDoc! in your home (with the `--user` option), globally (without this option), or (preferably)
inside a virtualenv.
