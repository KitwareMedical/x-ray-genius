FROM node:18-alpine

WORKDIR /opt/django-project/

# "@parcel/watcher" requires "node-gyp", which requires Python to build for some architectures
RUN apk update && apk add g++ make python3 pixman-dev cairo-dev pango-dev

# Copy these for the same reason as setup.py; they are needed for installation, but will be mounted
# over in the container.
COPY ./package.json /opt/django-project/package.json
COPY ./package-lock.json /opt/django-project/package-lock.json
COPY ./viewer/ /opt/django-project/viewer/
RUN npm install

# Build static files for the viewer. They will go in the shared volume with Django so it can serve them.
RUN npm run build:viewer

WORKDIR /opt/django-project
