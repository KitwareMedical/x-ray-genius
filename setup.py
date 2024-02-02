from pathlib import Path

from setuptools import find_packages, setup

readme_file = Path(__file__).parent / 'README.md'
if readme_file.exists():
    with readme_file.open() as f:
        long_description = f.read()
else:
    # When this is first installed in development Docker, README.md is not available
    long_description = ''

setup(
    name='xray_genius',
    version='0.1.0',
    description='',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='Apache 2.0',
    author='Kitware, Inc.',
    author_email='kitware@kitware.com',
    keywords='',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django :: 4.2',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python',
    ],
    python_requires='>=3.11',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'celery',
        'django<4.2',
        'django-allauth',
        'django-configurations[database,email]',
        'django-extensions',
        'django-filter',
        'django-login-required-middleware',
        'django-ninja',
        'django-oauth-toolkit',
        'django-widget-tweaks',
        # Production-only
        'django-composed-configuration[prod]>=0.20',
        'django-s3-file-field[s3]>=1.0.0',
        'gunicorn',
    ],
    extras_require={
        'dev': [
            'django-composed-configuration[dev]>=0.18',
            'django-debug-toolbar',
            'django-s3-file-field[minio]>=1.0.0',
            'ipython',
            'tox',
        ]
    },
)
