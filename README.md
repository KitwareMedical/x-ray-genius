# X-ray Genius

**Note: running the X-Ray simulation requires Cuda. The web application can still run without it, but the celery worker will
fail if any batch simulations are kicked off.**

## Develop with Docker (recommended quickstart)
This is the simplest configuration for developers to start with.

### Initial Setup
1. **Note**: Ensure that you clone the repository with submodules. If you've already cloned it without submodules, run `git submodule update --init --recursive`.
2. Install Nvidia GPU drivers, cuda, and the `nvidia-container-toolkit` if they are not already installed.
   - You can verify that the `nvidia-container-toolkit` is installed by running `nvidia-ctk --version`.
3. Run `docker compose run --rm django ./manage.py migrate`
4. Run `docker compose run --rm django ./manage.py createsuperuser`
   and follow the prompts to create your own user
5. Optionally, run `docker compose run --rm django ./manage.py load_test_data <girder_api_key>`
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
1. **Note**: Ensure that you clone the repository with submodules. If you've already cloned it without submodules, run `git submodule update --init --recursive`.
2. Run `docker compose -f ./docker-compose.yml up -d`
3. Install Python 3.13 and Node.js 18
4. Install
   [`psycopg2` build prerequisites](https://www.psycopg.org/docs/install.html#build-prerequisites)
5. Install Nvidia GPU drivers and cuda if they are not already installed.
6. Create and activate a new Python virtualenv
7. Run `pip install -e .[dev]`
8. Run `source ./dev/export-env.sh`
9. Run `./manage.py migrate`
10. Run `npm ci`
11. Run `./manage.py createsuperuser` and follow the prompts to create your own user

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
