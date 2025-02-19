FROM nvidia/cuda:11.6.1-cudnn8-devel-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive

# Install Python 3.13
RUN apt-get update && \
    apt-get --yes install software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa --yes && \
    apt-get --yes install python3.13 python3.13-dev python3.13-venv

# Install system libraries for Python packages:
# * psycopg2
RUN apt-get update && \
    apt-get install --no-install-recommends --yes \
        libpq-dev gcc libc6-dev libgl1-mesa-glx libxrender1 build-essential && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Use a directory name which will never be an import name, as isort considers this as first-party.
WORKDIR /opt/django-project

# Only copy the setup.py and requirements.txt, it will still force all install_requires to be installed,
# but find_packages() will find nothing (which is fine). When Docker Compose mounts the real source
# over top of this directory, the .egg-link in site-packages resolves to the mounted directory
# and all package modules are importable.
COPY ./requirements.dev.txt /opt/django-project/requirements.dev.txt
COPY ./requirements.worker.txt /opt/django-project/requirements.worker.txt
COPY ./setup.py /opt/django-project/setup.py

RUN python3.13 -m venv /opt/venv
RUN /opt/venv/bin/pip install --requirement /opt/django-project/requirements.worker.txt
RUN /opt/venv/bin/pip install --requirement /opt/django-project/requirements.dev.txt

ENV PATH="/opt/venv/bin:$PATH"
