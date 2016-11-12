Before installing the MapOSMatic web frontend you should have a working installation of OCitySMap.
We assume you have a "gis" user to be used in the maposmatic context. If not, adapt the instruction to your installation.

Quickstart
==========

Dependencies
------------
```bash
apt install python-django python-psycopg2 \
  python-feedparser python-imaging gettext imagemagick
```

Install sources
---------------
```bash
cd /srv
git clone https://gitlab.com/iggdrasil/maposmatic.git
chown -R gis maposmatic
```

Basic configuration
-------------------
```bash
su gis
cd maposmatic

cp www/settings_local.py.dist www/settings_local.py
# replace /srv/ocitysmap with the installation path of ocitysmap
echo -e "import sys\nsys.path.append('/srv/ocitysmap')" >> www/settings_local.py
# put a random string inside the secret key
echo "SECRET_KEY = 'a very unique key string'" >> www/settings_local.py

cp scripts/config.py.dist scripts/config.py

echo "OCITYSMAP_PATH = '/srv/ocitysmap'" >> scripts/config.py
```

Database initialization
-----------------------
Initialize MapOSMatic database with the default SQLite backend.

```bash
./manage.py migrate
```

Compile localization
--------------------
```bash
cd www/maposmatic
../../manage.py compilemessages
cd -
```

Rendering daemon
----------------
```bash
cd www
../scripts/wrapper.py scripts/daemon.py &
cd
```

Django test server
------------------
```bash
./manage.py runserver 0.0.0.0:8000
```

The test server should be available at the address of the server at port 8000.
Be carreful: it is nor a secure nor a performant solution. It is to be used only for testing purpose!

