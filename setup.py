from __future__ import annotations

from pathlib import Path

import setuptools  # type: ignore


# Load version number without importing HABApp
def load_version() -> str:
    version: dict[str, str] = {}
    with open('src/sml2mqtt/__version__.py') as fp:
        exec(fp.read(), version)
    assert version['__version__'], version
    return version['__version__']


def load_req() -> list[str]:
    req_file = Path(__file__).with_name('requirements_setup.txt')
    with req_file.open() as f:
        return f.readlines()


__version__ = load_version()

print(f'Version: {__version__}')
print('')

# When we run tox tests we don't have these files available so we skip them
readme = Path(__file__).with_name('readme.md')
long_description = ''
if readme.is_file():
    with readme.open('r', encoding='utf-8') as fh:
        long_description = fh.read()

setuptools.setup(
    name='sml2mqtt',
    version=__version__,
    author='spaceman_spiff',
    # author_email="",
    description='A sml (Smart Message Language) energy meter to MQTT bridge. '
                'Can read from serial ports or http (e.g. Tibber Pulse).',
    keywords=[
        'mqtt',
        'sml',
        'Smart Message Language',
        'energy meter',
        'tibber'
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/spacemanspiff2007/sml2mqtt',
    project_urls={
        'GitHub': 'https://github.com/spacemanspiff2007/sml2mqtt',
    },
    packages=setuptools.find_packages(where='src', exclude=['tests*']),
    package_dir={'': 'src'},
    python_requires='>=3.10',
    install_requires=load_req(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: AsyncIO',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Home Automation'
    ],
    entry_points={
        'console_scripts': [
            'sml2mqtt = sml2mqtt.__main__:main'
        ]
    }
)
