#!/usr/bin/env bash -x
new_version=$(curl -sN https://aur.archlinux.org/packages/plex-media-server-plexpass | grep -i "package details" | grep -Eo "[0-9][-.0-9]+[0-9]")
media="/mnt/superfree/media"
name="plex"

if [[ -n $new_version ]]
then
    if current_version=$(docker container ls --filter "name=$name" --format "{{.Image}}" | grep "$new_version")
    then
         exit 0 
    else
        tag="local:plex-$new_version"
        echo "Version mismatch.. upgrading Plex"
        docker container stop $name
        docker container rm $name
        docker image build  --file Dockerfile --no-cache --tag $tag
        docker container run --detach -it --net=host --name $name -v /mnt/plex:/mnt -v $media:$media -v /mnt/superfree2:/mnt/superfree2 $tag
    fi
fi

