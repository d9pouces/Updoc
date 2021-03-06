"""
this module define which extensions own an icon.
"""
__author__ = 'Matthieu Gallet'

ICONS = {
    'application-msword': {'docx', 'doc', 'dot', 'dotm', 'dotx'},
    'application-pdf': {'dvi', 'pdf'},
    'application-pgp-keys': {'pgp'},
    'application-rss+xml': {'rss'},
    'application-vnd.ms-excel': {'xls', 'xlsx', 'xlt', 'xlm', 'xlw', 'xltx'},
    'application-vnd.ms-powerpoint': {'pps', 'ppt', 'pptx', 'ppsx', 'ppot'},
    'application-vnd.scribus': {'ai'},
    'application-x-7zip': {'7z'},
    'application-x-ace': {'ace'},
    'application-x-archive': {'a', 'arc', 'as', 'bin', 'cab', 'cbz', 'cpgz', 'cpio', 'ar'},
    'application-x-bittorrent': {'bt'},
    'application-x-cd-image': {'cdr', 'dmg', 'iso'},
    'application-x-cue': {'cue'},
    'application-x-executable': {'app', 'so', 'dylib'},
    'application-x-flash-video': {'swf'},
    'application-x-jar': {'jar'},
    'application-x-ms-dos-executable': {'exe'},
    'application-x-php': {'php', 'php3', 'php4', 'php5'},
    'application-x-rar': {'rar'},
    'application-x-ruby': {'rb'},
    'application-x-sln': {'sln'},
    'application-x-tar': {'bz2', 'gz', 'xz', 'tbz', 'tbz2', 'tgz', 'txz'},
    'application-x-theme': {'theme'},
    'application-x-zip': {'zip'},
    'audio-x-generic': {'aiff', 'mp3', 'aac'},
    'audio-x-mp3-playlist': {'m3u'},
    'audio-x-mpeg': {'mpeg'},
    'audio-x-ms-wma': {'wma'},
    'audio-x-vorbis+ogg': {'ogg'},
    'audio-x-wav': {'wav'},
    'deb': {'deb'},
    'encrypted': {'pem', 'p12', 'cert', 'crt'},
    'font-x-generic': {'ttf'},
    'image-bmp': {'bmp'},
    'image-gif': {'gif'},
    'image-jpeg': {'jpeg', 'jpg', 'jp2'},
    'image-png': {'png', 'dng'},
    'image-tiff': {'tiff'},
    'image-x-eps': {'eps', 'ps'},
    'image-x-generic': {'svg'},
    'image-x-ico': {'ico', 'icns'},
    'image-x-psd': {'psd'},
    'image-x-xcf': {'xcf'},
    'rpm': {'rpm'},
    'text-css': {'css'},
    'text-html': {'html', 'htm', 'cgi', 'fcgi', 'mhtml'},
    'text-plain': {'txt', 'diff', 'ini', 'patch'},
    'text-richtext': {'rtf', 'md', 'rst'},
    'text-x-bak': {'bak'},
    'text-x-bibtex': {'bib'},
    'text-x-c': {'c'},
    'text-x-c++': {'cpp', 'c++', 'cxx', 'cc'},
    'text-x-c++hdr': {'hxx', 'hpp', 'hh', 'h++'},
    'text-x-changelog': {'log'},
    'text-x-chdr': {'h'},
    'text-x-generic-template': {'asp', 'aspx'},
    'text-x-java': {'java', 'jsp'},
    'text-x-javascript': {'js'},
    'text-x-makefile': {'makefile'},
    'text-x-python': {'py', 'pyc', 'pyo'},
    'text-x-readme': {'readme'},
    'text-x-script': {'applescript', 's', 'asm', 'sh', 'zsh', 'csh'},
    'text-x-source': {'erl', 'el', 'exp', 'f', 'f77', 'f90', 'f95', 'fo', 'for', 'lisp', 'lua', 'pl', 'perl', 'r',
                      'vim', 'yaml', 'y', 'yml', ''},
    'text-x-sql': {'sql'},
    'text-x-tex': {'tex', 'cls', 'sty', 'dtx'},
    'text-xhtml+xml': {'xhtml'},
    'text-xml': {'xml', 'dtd', 'plist', 'rdf'},
    'vcalendar': {'cal', 'ics'},
    'video-x-generic': {'avi', 'dv', 'mp4', 'mov', 'mkv', 'mpg'},
    'x-dia-diagram': {'odc'},
    'x-office-document': {'odt', 'ott'},
    'x-office-drawing': {'odg', 'odi'},
    'x-office-presentation': {'odp', 'otp'},
    'x-office-spreadsheet': {'ods', 'ots'},
    }

EXTENSIONS = {}
for key, values in ICONS.items():
    for value in values:
        EXTENSIONS[value] = key
