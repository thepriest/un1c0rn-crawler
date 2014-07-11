un1c0rn-crawler
===============

Web-crawler for http://un1c0rn.net project. It parses HTML (sorry, no other way to do the work,
since the project doesn't provide an API or any way to dump the db) and fills local mongo database
(unicorn database, hosts table) with results.

See the (very small) code for details. Written in python 3. Tested with python-3.4
Requires: urllib, BeautifulSoup4, pymongo
