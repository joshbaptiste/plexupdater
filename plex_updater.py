#!/usr/bin/env python3

import os
import shutil
import sys
import re
from time import sleep
from bs4 import BeautifulSoup as bs
#import psutil
import requests
import subprocess
import signal

__doc__ = 'Script has to be run relative to the Plex directory and as running user or sudo'
LINK = 'https://aur.archlinux.org/packages/plex-media-server-plexpass/'
SLEEP = 10
DDIR = '/tmp'


def download_file(url):
    local_filename = DDIR + '/' + url.split('/')[-1]
    if os.path.exists(local_filename):
        print(local_filename + "Already exists")
        return local_filename
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                # f.flush() commented by recommendation from J.F.Sebastian
    return local_filename


def extract(f):
    try:
        command = 'rpm2cpio /tmp/{} | cpio -idmv'.format(f)
        print("Running " + command)
        subprocess.check_output(command, shell=True)
    except subprocess.CalledProcessError as err:
        print(str(err))
        sys.exit(1)


def kill_plex(process_gid):
    """ Retrieves the process group of Plex and sends TERM signal """
    os.killpg(int(process_gid), signal.SIGTERM)
    print("SIGTERM sent to Plex process group ID")
    print("Waiting {} seconds".format(SLEEP))


def rename(ff):
    f = '.'.join(ff.split('.')[:-2])
    print("Renaming relative dir usr/lib/plexmediaserver to " + f)
    try:
        os.rename('usr/lib/plexmediaserver', f)
    except OSError as err:
        print(str(err))
        sys.exit(2)


def symlink(f):
    """ symlinks new version to Plex """
    file_name = '.'.join(f.split('.')[:-2])
    link_name = 'Plex'
    try:
        os.remove(link_name)
    except FileNotFoundError as err:
        print(str(err))
    print("Symlinking {} to {}".format(file_name, link_name))
    os.symlink(file_name, link_name)


def remove(f=None):
    """ Removes relative files extracted by cpio"""
    if f:
        os.remove(DDIR + '/' + f)
    else:
        print('removing usr')
        shutil.rmtree('usr')
        print('removing etc')
        shutil.rmtree('etc')
        print('removing lib')
        shutil.rmtree('lib')


def extract_link():
    """ extracts link from AUR page """
    html = requests.get(LINK).content
    soup = bs(html, 'html.parser')
    for link in soup.find_all('a'):
        match = re.search(r'^http.*x86_64.*rpm$', link.get('href'))
        if match:
            url = match.group()
            file_name = url.split('/')[-1]
            if check_exists(file_name):
                print("Downloading to /tmp/" + file_name)
                download_file(url)
    return file_name


def check_exists(f):
    """ check if plexmediaserver-1.4.3.3433-03e4cfa35 exists """
    _f = '.'.join(f.split('.')[:-2])
    print("Checking if {} exists".format(_f))
    if os.path.exists(_f):
        print("Exiting dir already exists")
        sys.exit(3)
    else:
        return True


def get_plex_pgid():
    # psutil has to many issues depending on version used switch to pgrep 
    #	and has C based extensions which is a pain sometimes
    #"""
    # try:
    #     for proc in psutil.process_iter():
    #         if proc.name == "Plex Media Server":
    #             process_gid = os.getpgid(int(proc.pid))
    #             return process_gid
    # except psutil.ZombieProcess:
    #     pass
    try:
        pid = subprocess.check_output("pgrep -f 'Plex Media Server$'", shell=True)
        process_gid = os.getpgid(int(pid))
        return process_gid
    except subprocess.CalledProcessError as err:
        print(str(err))


def main():
    file_name = extract_link()
    extract(file_name)
    rename(file_name)
    remove()

    while True:
        process_gid = get_plex_pgid()
        if process_gid:
            kill_plex(process_gid)
            sleep(SLEEP)
        else:
            symlink(file_name)
            print("No Plex pid quitting")
            print("Removing %s in 10 seconds" % file_name)
            #remove rpm file
            sleep(SLEEP)
            remove(file_name)
            break


if __name__ == '__main__':
    main()
