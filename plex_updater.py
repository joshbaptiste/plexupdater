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


def download_rpm_file(url, rpm_file):
    if os.path.exists(rpm_file):
        print(rpm_file + " Already exists")
        return rpm_file
    print("Downloading to " + rpm_file)
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(rpm_file, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                # f.flush() commented by recommendation from J.F.Sebastian
    return rpm_file


def extract_rpm_file(f):
    try:
        command = "rpm2cpio {} | cpio -idmv './usr/lib/plexmediaserver/*' ".format(f)
        print("Running " + command)
        subprocess.check_output(command, shell=True)
    except subprocess.CalledProcessError as err:
        print(str(err))
        sys.exit(1)


def kill_plex(process_gid, sigkill=False):
    """ Retrieves the process group of Plex and sends TERM signal """
    if sigkill:
        print("SIGKILL sent to Plex process group ID")
        os.killpg(int(process_gid), signal.SIGKILL)
    else:
        os.killpg(int(process_gid), signal.SIGTERM)
    print("SIGTERM sent to Plex process group ID")
    print("Waiting {} seconds".format(SLEEP))


def rename_plex_dir(dirname):
    """ renames plexmediaserver -> plexmediaserver-1.4.3.3433-03e4cfa35 """
    print("Renaming relative dir usr/lib/plexmediaserver to " + dirname)
    try:
        os.rename('usr/lib/plexmediaserver', dirname)
    except OSError as err:
        print(str(err))
        sys.exit(2)


def symlink_plex_dirname(dirname):
    """ symlinks new version to Plex """
    link_name = 'Plex'
    try:
        # remove prev link
        os.remove(link_name)
    except FileNotFoundError as err:
        print(str(err))
    print("Symlinking {} to {}".format(dirname, link_name))
    os.symlink(dirname, link_name)


def remove_rpm_cpio_files(f=None):
    """ Removes relative files extracted by cpio and rpm file later"""
    if f:
        print("Removing " + f)
        os.remove(f)
    else:
        print('removing usr')
        shutil.rmtree('usr')


def get_filename_url():
    """ extracts link from AUR page """
    html = requests.get(LINK).content
    soup = bs(html, 'html.parser')
    for link in soup.find_all('a'):
        match = re.search(r'^http.*x86_64.*rpm$', link.get('href'))
        if match:
            url = match.group()
            return url


def check_dir_exists(dirname):
    """ check if plexmediaserver-1.4.3.3433-03e4cfa35 exists """
    print("Checking if {} exists".format(dirname))
    if os.path.exists(dirname):
        print("Exiting dir already exists")
        sys.exit(0)
    else:
        return False


def get_plex_pgid():
    # psutil has too many issues depending on the version used,
    # and has C baseddd extensions which is a pain sometimes
    # switched to pgrep for now
    # try:
    #     for proc in psutil.process_iter():
    #         if proc.name == "Plex Media Server":
    #             process_gid = os.getpgid(int(proc.pid))
    #             return process_gid
    # except psutil.ZombieProcess:
    #     pass
    try:
        pid = subprocess.check_output(
            "pgrep -f 'Plex Media Server$'", shell=True)
        process_gid = os.getpgid(int(pid))
        return process_gid
    except subprocess.CalledProcessError as err:
        print(str(err))


def get_prev_dirname(dirname):
    prev_dirname = None
    try:
        prev_dirname = os.readlink('Plex')
    except FileNotFoundError as err:
        print(str(err))
    # if they are equal this is the only dir
    if dirname == prev_dirname:
        prev_dirname = None
    return prev_dirname


def symlink_prev_file(prev_dirname):
    if not os.path.exists('Plex.old'):
        print('Symlinking previous file {} to Plex.old'.format(prev_dirname))
        os.symlink(prev_dirname, 'Plex.old')


def remove_old_dir():
    symlink = 'Plex.old'
    if os.path.exists(symlink):
        old_plex_dir = os.readlink(symlink)
        print("Removing old Plex dir {}".format(old_plex_dir))
        shutil.rmtree(old_plex_dir)
        os.remove(symlink)


def main():
    url = get_filename_url()
    rpm_file = DDIR + '/' + url.split('/')[-1]
    dirname = os.path.basename('.'.join(rpm_file.split('.')[:-2]))
    check_dir_exists(dirname)
    download_rpm_file(url, rpm_file)
    prev_dirname = get_prev_dirname(dirname)
    extract_rpm_file(rpm_file)
    rename_plex_dir(dirname)
    remove_rpm_cpio_files()

    while True:
        process_gid = get_plex_pgid()
        sigterm_count = 0
        if process_gid:
            if sigterm_count >= 3:
                kill_plex(process_gid, sigkill=True)
            else:
                kill_plex(process_gid)
                sigterm_count += 1
            sleep(SLEEP)
        else:
            symlink_plex_dirname(dirname)
            print("No Plex pid quitting")
            print("Removing %s in 10 seconds" % rpm_file)
            # remove rpm file
            sleep(SLEEP)
            remove_rpm_cpio_files(rpm_file)
            remove_old_dir()
            if prev_dirname:
                symlink_prev_file(prev_dirname)
            break


if __name__ == '__main__':
    main()
