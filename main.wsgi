import sys 
sys.path.insert(0, '/var/www/html/KryptoDemoPrototype')

from main import app as application

# WSGIDaemonProcess KryptoDemoPrototype threads=5
# WSGIScriptAlias / /var/www/html/KryptoDemoPrototype/main.wsgi

# <Directory KryptoDemoPrototype>
#     WSGIProcessGroup KryptoDemoPrototype
#     WSGIApplicationGroup %{GLOBAL}
#     Order deny,allow
#     Allow from all
# </Directory>