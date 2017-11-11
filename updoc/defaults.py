
__author__ = 'Matthieu Gallet'

PUBLIC_BOOKMARKS = True
PUBLIC_PROXIES = True
PUBLIC_INDEX = True
PUBLIC_DOCS = True

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
USE_HTTP_BASIC_AUTH = True
DEVELOPMENT = False
