#!/bin/bash
SCRIPTPATH=/pvr/Plex
export LD_LIBRARY_PATH="/usr/local/lib/compat:${SCRIPTPATH}:$SCRIPTPATH/lib"
export PLEX_MEDIA_SERVER_HOME="${SCRIPTPATH}"
#export LANG="en_US.UTF-8"
# default script for Plex Media Server

# the number of plugins that can run at the same time
export PLEX_MEDIA_SERVER_MAX_PLUGIN_PROCS=5

# ulimit -s $PLEX_MEDIA_SERVER_MAX_STACK_SIZE
export PLEX_MEDIA_SERVER_MAX_STACK_SIZE=3000

# where the mediaserver should store the transcodes
export PLEX_MEDIA_SERVER_TMPDIR="/mnt/plextmp"

# uncomment to set it to something else
export PLEX_MEDIA_SERVER_APPLICATION_SUPPORT_DIR="/mnt/plexmediaserver"

# the user that PMS should run as, defaults to 'plex'
# note that if you change this you might need to move
# the Application Support directory to not lose your
# media library
export PLEX_MEDIA_SERVER_USER=$USER
export PYTHONHOME="${SCRIPTPATH}/Resources/Python"
export PATH="${SCRIPTPATH}/Resources/Python/bin:${PATH}"

#change these parameters in /etc/default/plexmediaserver
ulimit -s $PLEX_MEDIA_SERVER_MAX_STACK_SIZE
/pvr/Plex/Plex\ Media\ Server
