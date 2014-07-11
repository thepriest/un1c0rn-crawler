#!/usr/bin/python3

# Web crawler to dump un1c0rn.net database to local mongo instance.
# It lacks an update functionality (don't know how to implement) and uses
# html parsing (since there is no other way to get the data).
# It's unofficial, so be careful (and please don't blame for the code, I'm not
# python guru. Can make it better? Do!).
#
# In case of any questions or suggestions feel free to email me.
#
# Author: thepriest <maverik.mail@gmail.com>
# Date: 2014-07-11
#
# Copyright © 2014 thepriest <maverik.mail@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.

import string
import time
import urllib.request
from bs4 import BeautifulSoup
from pymongo import MongoClient
from multiprocessing import Pool

# Parse page by its number and push results to database
def processPage(pageNumber):
    print('Processing page #' + str(pageNumber) + '...');
    
    # Open page by page number and grab html code to parse
    while(1):
        try:
            response = urllib.request.urlopen('http://un1c0rn.net/?module=hosts&action=list&page=' + str(pageNumber));
            break;
        except urllib.error.HTTPError as e:
            if (e.code == 404) return;
            print('HTTP error: ' + str(e.code));
            time.sleep(1);
            continue;

    # Parse page's html code. All search results are in <div class="search-result-item">
    # There are 20 results per page (may be less for the last one)
    html = response.read();
    soup = BeautifulSoup(html);

    divs = soup.find_all('div', attrs={'class':'search-result-item'});
    if (len(divs) == 0): exit(0);

    # Fill the hosts list with the search values.
    # <a> tag contains link to the datails page (as href), host's IPv4 address
    # and resolved name (if any) as a text.
    # <small> tag contains vulnerability type (weakmysql, mongo, etc), update date
    # in format yyyy-mm-dd and update time in format hh:mm:ss (24hrs format).
    hosts = []
    for div in divs:
        link = div.a;
        linkReference = link['href'];
        linkText = link.string
        small = div.small;
        smallText = small.string; # | [type] date time

        # Open details page using link we get from <a> tag and parse its html code
        while(1):
            try:
                response = urllib.request.urlopen('http://un1c0rn.net/' + linkReference);
                break;
            except urllib.error.HTTPError as e:
                if (e.code == 404) return;
                print('HTTP error: ' + str(e.code));
                time.sleep(1);
                continue;

        # Details about vulnerability is placed between <pre> tag
        html = response.read();
        soup = BeautifulSoup(html);

        pre = soup.find('pre');
        preText = pre.string;

        hostData = linkText.split('-');
        vulnData = smallText.strip().split(' ');
        hosts.append({'ip': hostData[0].strip(), 'hostname': hostData[1].strip() if len(hostData) > 1 else '',
                'vulnType': vulnData[0][vulnData[0].find('[') + 1 : vulnData[0].rfind(']')],
                'updateDate': vulnData[0][vulnData[0].rfind(']') + 2:], 'updateTime': vulnData[1],
                'dump': preText.strip() if preText else ''
        })
    db.hosts.insert(hosts);

if __name__ == '__main__':
    client = MongoClient()
    db = client.unicorn;
    pool = Pool(8);

    # We need somehow to get number of pages we can process.
    # E.g. you can parse it from the page ('112369 open host(s) found | 112369 indexed')
    # and then divide this number by 20 (results per page, don't forget the fraction),
    # but I'm too lazy to do this for my simple tool. So I count it by hands :)
    pool.map(processPage, range(1, 5616))
