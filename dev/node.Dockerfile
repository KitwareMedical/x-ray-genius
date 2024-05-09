FROM node:18-alpine

WORKDIR /opt/django-project/

# "@parcel/watcher" requires "node-gyp", which requires Python to build for some architectures
RUN apk update && apk add g++ make python3 pixman-dev cairo-dev pango-dev

# Copy these for the same reason as setup.py; they are needed for installation, but will be mounted
# over in the container.
COPY ./package.json /opt/django-project/package.json
COPY ./package-lock.json /opt/django-project/package-lock.json
COPY ./viewer/package.json /opt/django-project/viewer/package.json
COPY ./viewer/package-lock.json /opt/django-project/viewer/package-lock.json
RUN npm install

# Copy statically built wasm/other binary files to the shared Django volume
COPY ./viewer/core/VolView/src/io /opt/django-project/viewer/core/VolView/src/io
COPY ./viewer/core/VolView/src/io/itk-dicom/emscripten-build/* /opt/django-project/viewer/dist/itk/pipelines
COPY ./viewer/core/VolView/src/io/resample/emscripten-build/* /opt/django-project/viewer/dist/itk/pipelines

WORKDIR /opt/django-project
