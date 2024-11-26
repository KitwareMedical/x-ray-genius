# xray_genius

**Note: running the X-Ray simulation requires Cuda. The web application can still run without it, but the celery worker will
fail if any batch simulations are kicked off.**

## Develop with Docker (recommended quickstart)
This is the simplest configuration for developers to start with.

### Initial Setup
1. Install Nvidia GPU drivers, cuda, and the `nvidia-container-toolkit` if they are not already installed.
   - You can verify that the `nvidia-container-toolkit` is installed by running `nvidia-ctk --version`.
2. Run `docker compose run --rm django ./manage.py migrate`
3. Run `docker compose run --rm django ./manage.py createsuperuser`
   and follow the prompts to create your own user
4. Optionally, run `docker compose run --rm django ./manage.py load_test_data <girder_api_key>`
   to load some sample data into your system.
   1. Make sure to replace `<girder_api_key>` with your DKC API key.

### Run Application
1. Run `docker compose up`
2. Access the site, starting at http://localhost:8000/admin/
3. When finished, use `Ctrl+C`

### Application Maintenance
Occasionally, new package dependencies or schema changes will necessitate
maintenance. To non-destructively update your development stack at any time:
1. Run `docker compose pull`
2. Run `docker compose build --pull --no-cache`
3. Run `docker compose run --rm django ./manage.py migrate`

## Develop Natively (advanced)
This configuration still uses Docker to run attached services in the background,
but allows developers to run Python code on their native system.

### Initial Setup
1. Run `docker compose -f ./docker-compose.yml up -d`
2. Install Python 3.11 and Node.js 18
3. Install
   [`psycopg2` build prerequisites](https://www.psycopg.org/docs/install.html#build-prerequisites)
4. Install Nvidia GPU drivers and cuda if they are not already installed.
5. Create and activate a new Python virtualenv
6. Run `pip install -e .[dev]`
7. Run `source ./dev/export-env.sh`
8. Run `./manage.py migrate`
9. Run `npm ci`
10. Run `./manage.py createsuperuser` and follow the prompts to create your own user

### Run Application
1.  Ensure `docker compose -f ./docker-compose.yml up -d` is still active
2. Run:
   1. `source ./dev/export-env.sh`
   2. `./manage.py runserver`
3. Run in a separate terminal:
   1. `source ./dev/export-env.sh`
   2. `celery --app xray_genius.celery worker --loglevel INFO --pool solo`
4. Run in a separate terminal:
   1. `npm start`
5. Optionally, run `./manage.py load_test_data <girder_api_key>`
   to load some sample data into your system.
   1. Make sure to replace `<girder_api_key>` with your DKC API key. Alternatively, set the
      `GIRDER_API_KEY` environment variable to your DKC API key.
5. When finished, run `docker compose stop`
6. To destroy the stack and start fresh, run `docker compose down -v`

## Remap Service Ports (optional)
Attached services may be exposed to the host system via alternative ports. Developers who work
on multiple software projects concurrently may find this helpful to avoid port conflicts.

To do so, before running any `docker compose` commands, set any of the environment variables:
* `DOCKER_POSTGRES_PORT`
* `DOCKER_REDIS_PORT`
* `DOCKER_MINIO_PORT`

The Django server must be informed about the changes:
* When running the "Develop with Docker" configuration, override the environment variables:
  * `DJANGO_MINIO_STORAGE_MEDIA_URL`, using the port from `DOCKER_MINIO_PORT`.
* When running the "Develop Natively" configuration, override the environment variables:
  * `DJANGO_DATABASE_URL`, using the port from `DOCKER_POSTGRES_PORT`
  * `DJANGO_CELERY_BROKER_URL`, using the port from `DOCKER_REDIS_PORT`
  * `DJANGO_MINIO_STORAGE_ENDPOINT`, using the port from `DOCKER_MINIO_PORT`

Since most of Django's environment variables contain additional content, use the values from
the appropriate `dev/.env.docker-compose*` file as a baseline for overrides.

## Testing
### Initial Setup
tox is used to execute all tests.
tox is installed automatically with the `dev` package extra.

When running the "Develop with Docker" configuration, all tox commands must be run as
`docker compose run --rm django tox`; extra arguments may also be appended to this form.

### Running Tests
Run `tox` to launch the full test suite.

Individual test environments may be selectively run.
This also allows additional options to be be added.
Useful sub-commands include:
* `tox -e lint`: Run only the style checks
* `tox -e type`: Run only the type checks
* `tox -e test`: Run only the pytest-driven tests

To automatically reformat all code to comply with
some (but not all) of the style checks, run `tox -e format`.
