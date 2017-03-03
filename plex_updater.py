#!/usr/bin/env python3

import os
import shutil
import sys
import re
from bs4 import BeautifulSoup as bs
import requests
import subprocess

l = 'https://aur.archlinux.org/packages/plex-media-server-plexpass/'

def download_file(url):
    local_filename = '/tmp/' + url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian
    return local_filename


def convert_file(f):
    try:
        command = 'rpm2cpio /tmp/{} | cpio -idmv'.format(f)
        print("Running " + command)
        subprocess.check_output(command, shell=True)
    except subprocess.CalledProcessError as err:
        print(str(err))
        sys.exit(1)

def rename_file(ff):
    f = '.'.join(ff.split('.')[:-2])
    print("Renaming relative dir usr/lib/plexmediaserver to " + f)
    try:
        os.rename('usr/lib/plexmediaserver',f)
        print('removing usr')
        shutil.rmtree('usr')
        print('removing etc')
        shutil.rmtree('etc')
        print('removing lib')
        shutil.rmtree('lib')
    except OSError as err:
        print(str(err))
        sys.exit(2)


def check_exists(f):
    """ check if plexmediaserver-1.4.3.3433-03e4cfa35 exists """
    _f = '.'.join(f.split('.')[:-2])
    print("Checking if {} exists".format(_f))
    if os.path.exists(_f):
        print("Exiting dir already exists")
        sys.exit(3)
    else:
        return True

if __name__ == '__main__':
    html = requests.get(l).content
    soup = bs(html, 'html.parser')
    for link in soup.find_all('a'):
            match = re.search(r'^http.*x86_64.*rpm$', link.get('href'))
            if match:
                url = match.group()
                f = url.split('/')[-1]
                if check_exists(f):
                    print("Downloading to /tmp/" + f  )
                    download_file(url)

    convert_file(f)
    rename_file(f)
