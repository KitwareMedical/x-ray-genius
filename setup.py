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
        'Framework :: Django :: 5.1',
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
        'celery>=5.4',
        'channels[daphne]',
        'django>=5.1,<5.2',
        'django-allauth[socialaccount]',
        'django-celery-results',
        'django-click',
        'django-configurations[database,email]',
        'django-extensions',
        'django-filter',
        'django-login-required-middleware',
        'django-ninja',
        'django-oauth-toolkit',
        'django-vite',
        'django-widget-tweaks',
        'numpy',
        'pillow',
        'pydantic',
        'scipy',
        # Production-only
        'django-composed-configuration[prod]>=0.25',
        'django-s3-file-field[s3]>=1.0.0',
    ],
    extras_require={
        'worker': [
            'deepdrr',
            'pypng',
        ],
        'dev': [
            'django-autotyping',
            'django-browser-reload',
            'django-composed-configuration[dev]>=0.25',
            'django-debug-toolbar',
            'django-s3-file-field[minio]>=1.0.0',
            'django-stubs',
            'girder-client',
            'ipython',
            'tox',
        ],
    },
)
