MapOSMatic - A web interface for creating printable OpenStreetMap maps
======================================================================

MapOSMatic is a web application to generate maps of cities or towns,
including index of streets, from OpenStreetMap data.

It is made of two components:

 * MapOSMatic (this repository): the web front-end. An application
   written using the Django framework allows to submit and visualize
   map rendering jobs.
   The rendering is done in the background by a daemon process.

 * OCitysMap (separate repository): the back-end that generates the map.
   It is available as a Python module, used both by the maposmatic daemon
   (above) and by a sample command line application.

This source tree contains maposmatic, the web front-end.

The OCitysMap repository can be found here:

https://github.com/hholzgra/ocitysmap

It is licensed under under GNU AGPLv3
(GNU Affero General Public License 3.0).

Translation
-----------

You can help translating the user interface into other languages here:

https://translate.get-map.org/projects/maposmatic/maposmatic/

Installation
------------

Please refer to the ``INSTALL.md`` file in this repository.

End user and API documentation
------------------------------

End user documentation for the web frontends useage, and API documentation
for developers who want to submit their own rendering job into the rendering
daemons queue, can be found in the ``documentation`` subdirectory.