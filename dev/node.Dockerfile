FROM node:current-alpine

# "@parcel/watcher" requires "node-gyp", which requires Python to build for some architectures
RUN apk update && apk add g++ make python3

# Copy these for the same reason as setup.py; they are needed for installation, but will be mounted
# over in the container.
COPY ./package.json /opt/django-project/package.json
COPY ./package-lock.json /opt/django-project/package-lock.json
RUN npm --prefix /opt/django-project --ignore-scripts install

WORKDIR /opt/django-project
