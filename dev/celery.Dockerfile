FROM python:3.11-slim
# Install system libraries for Python packages:
# * psycopg2
RUN apt-get update && \
    apt-get install --no-install-recommends --yes \
        libpq-dev gcc libc6-dev && \
    rm -rf /var/lib/apt/lists/*

# Install additional packages needed for deepdrr GPU/celery worker
RUN apt-get update && \
    apt-get install --no-install-recommends --yes \
        curl g++ gpg && \
    rm -rf /var/lib/apt/lists/*

# Install CUDA
RUN curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg && \
    curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    tee /etc/apt/sources.list.d/nvidia-container-toolkit.list && \
    apt-get update && \
    apt-get install -y nvidia-container-toolkit

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Only copy the setup.py, it will still force all install_requires to be installed,
# but find_packages() will find nothing (which is fine). When Docker Compose mounts the real source
# over top of this directory, the .egg-link in site-packages resolves to the mounted directory
# and all package modules are importable.
COPY ./setup.py /opt/django-project/setup.py
RUN pip install --editable /opt/django-project
RUN pip install --editable /opt/django-project[worker]

# Use a directory name which will never be an import name, as isort considers this as first-party.
WORKDIR /opt/django-project
