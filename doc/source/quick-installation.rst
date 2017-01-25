Quick installation
==================

You can quickly test UpDoc!, storing all data in $HOME/updoc:

.. code-block:: bash

    sudo apt-get install python3.5 python3.5-dev build-essential
    pip install updoc
    updoc-manage migrate  # create the database (SQLite by default)
    updoc-manage collectstatic --noinput  # prepare static files (CSS, JS, …)
    updoc-manage createsuperuser  # create an admin user



You can easily change the root location for all data (SQLite database, uploaded or temp files, static files, …) by
editing the configuration file:

.. code-block:: bash

    CONFIG_FILENAME=`updoc-manage  config ini -v 2 | head -n 1 | grep ".ini" | cut -d '"' -f 2`
    # create required folders
    mkdir -p `dirname $FILENAME` $HOME/updoc
    # prepare a limited configuration file
    cat << EOF > $FILENAME
    [global]
    data = $HOME/updoc
    EOF

Of course, you must run again the `migrate` and `collectstatic` commands (or moving data to this new folder).


You can launch the server processes (the second process is required for background tasks):

.. code-block:: bash

    updoc-aiohttp
    updoc-celery worker -Q celery,slow


Then open http://127.0.0.1:8129 in your favorite browser.

You should use virtualenv or install UpDoc! using the `--user` option.