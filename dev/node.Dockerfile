FROM node:18-alpine AS base
# "@parcel/watcher" requires "node-gyp", which requires Python to build for some architectures
RUN apk update && apk add g++ make python3 pixman-dev cairo-dev pango-dev
WORKDIR /opt/django-project/
# Copy these for the same reason as setup.py; they are needed for installation, but will be mounted
# over in the container.
COPY ./package.json /opt/django-project/package.json
COPY ./package-lock.json /opt/django-project/package-lock.json
COPY ./viewer/package.json /opt/django-project/viewer/package.json
COPY ./viewer/package-lock.json /opt/django-project/viewer/package-lock.json
RUN npm install


# Build the ITK wasm static files in a separate stage
FROM base AS build-wasm
COPY --from=base /opt/django-project/node_modules/ /opt/django-project/node_modules/
COPY --from=base /opt/django-project/viewer/node_modules/ /opt/django-project/viewer/node_modules/
COPY ./viewer/ viewer/
RUN npm run build:viewer


FROM build-wasm
WORKDIR /opt/django-project/
COPY --from=build-wasm /opt/django-project/viewer/dist/itk/itk-wasm-pipeline.min.worker.js /opt/django-project/viewer/dist/itk/itk-wasm-pipeline.min.worker.js
COPY ./package.json /opt/django-project/package.json
COPY ./package-lock.json /opt/django-project/package-lock.json
COPY ./viewer/package.json /opt/django-project/viewer/package.json
COPY ./viewer/package-lock.json /opt/django-project/viewer/package-lock.json
