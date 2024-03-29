FROM nvidia/cuda:12.3.2-cudnn9-devel-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive

# Install Python 3.11
RUN apt-get update && \
    apt-get --yes install software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa --yes && \
    apt-get --yes install python3.11 python3.11-dev python3.11-venv

# Install system libraries for Python packages:
# * psycopg2
RUN apt-get update && \
    apt-get install --no-install-recommends --yes \
        libpq-dev gcc libc6-dev libgl1-mesa-glx libxrender1 && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Only copy the setup.py, it will still force all install_requires to be installed,
# but find_packages() will find nothing (which is fine). When Docker Compose mounts the real source
# over top of this directory, the .egg-link in site-packages resolves to the mounted directory
# and all package modules are importable.
COPY ./setup.py /opt/django-project/setup.py

RUN python3.11 -m venv /opt/venv
RUN /opt/venv/bin/pip install --editable /opt/django-project[dev,worker]

ENV PATH="/opt/venv/bin:$PATH"

# Use a directory name which will never be an import name, as isort considers this as first-party.
WORKDIR /opt/django-project
