FROM debian:latest

LABEL description="Plex builder config"

RUN apt-get update && apt-get install -y \
	python3-bs4 \
	python3-requests \
	rpm2cpio \
	curl \
	cpio \
	procps \
	locales \
	&& rm -rf /var/lib/apt/lists/*
ENV DEBIAN_FRONTEND=noninteractive
RUN useradd --no-create-home -s /bin/bash --uid 1002 --gid 1002 pvr
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && /usr/sbin/locale-gen
RUN mkdir -p /pvr \
	&& curl -SL https://raw.githubusercontent.com/joshbaptiste/plexupdater/master/plex_updater.py \
	-o /pvr/plex_updater.py \
    && curl -SL https://raw.githubusercontent.com/joshbaptiste/plexupdater/master/start_plex_docker.sh \
    -o /pvr/start_plex_docker.sh \
    && chown pvr -R /pvr
EXPOSE 32400/tcp
#Everything done here by user pvr
WORKDIR /pvr
USER pvr
# Create a default plex symlink
RUN mkdir -- plexmediaserver-1.4.3.3433-03e4cfa35 \
	&& ln -s -- plexmediaserver-1.4.3.3433-03e4cfa35 Plex \
	&& python3 /pvr/plex_updater.py
CMD ["bash", "/pvr/start_plex_docker.sh"]

