# -*- coding: utf-8 -*-

__author__ = 'Matthieu Gallet'

PUBLIC_BOOKMARKS = True
PUBLIC_BOOKMARKS_HELP = 'Are bookmarks publicly available?'
PUBLIC_PROXIES = True
PUBLIC_PROXIES_HELP = 'Is proxy.pac file publicly available?'
PUBLIC_INDEX = True
PUBLIC_INDEX_HELP = 'Is the list of all documentations publicly available?'
PUBLIC_DOCS = True
PUBLIC_DOCS_HELP = 'Are documentations publicly available?'

LISTEN_ADDRESS = '127.0.0.1:8129'
ES_HOSTS = None
ES_HOSTS_HELP = 'IP:port of your ElasticSearch database, leave it empty if you do not use ElasticSearch'
ES_INDEX = 'updoc_index'
ES_INDEX_HELP = 'name of your ElasticSearch index'
ES_TIKA_EXTENSIONS = 'pdf,html,doc,odt,rtf,epub'
ES_MAX_SIZE = 30 * 1024 * 1024
ES_DOC_TYPE = 'document'
ES_PLAIN_EXTENSIONS = 'txt,csv,md,rst'
ES_EXCLUDED_DIR = '_sources,_static'

DF_TEMPLATE_CONTEXT_PROCESSORS = ['updoc.context_processors.most_checked']
DF_INDEX_VIEW = 'updoc.views.index'
DF_PROJECT_NAME = 'UpDoc!'
DF_JS = ['js/jquery.ui.widget.js', 'js/jquery.iframe-transport.js', 'js/jquery.fileupload.js', 'js/fuelux.min.js',
         'js/updoc.js', ]
DF_CSS = ['css/fuelux.min.css', 'css/updoc.css']
DF_URL_CONF = 'updoc.root_urls.urls'
