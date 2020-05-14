#!/usr/bin/env bash

url="https://aur.archlinux.org/packages/plex-media-server-plexpass"
new_version=$(curl -sN "$url" | grep -i "package details" | grep -Eo "[0-9][-.0-9]+[0-9]")
media="/mnt/superfree/media"
media2="/mnt/superfree2"
name="plex"

if [[ -n $new_version ]]
then
    # If current container version matches we have the latest
    if docker container ls --filter "name=$name" --format "{{.Image}}" | grep -q "$new_version"
    then
         exit 0
    else
        tag="local:plex-$new_version"
        echo "Version mismatch.. upgrading Plex"
        docker container stop $name
        docker container rm $name
        docker image build  --file Dockerfile --no-cache --tag $tag .
        docker container run --detach -it --net=host --name $name -v /mnt/plex:/mnt -v $media:$media -v $media2:$media2 $tag
    fi
fi

