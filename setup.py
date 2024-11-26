from setuptools import setup, find_packages

setup(
    name="iosdefaults",
    version="1.0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pymobiledevice3",
    ],
    entry_points={
        "console_scripts": [
            "iosdefaults=iOSDefaults.cli:main",
        ],
    },
    author="Maxime MADRAU",
    author_email="maxime@madrau.fr",
    description="Command line tool for editing app user-preferences on iOS devices through usb",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Maxmad68/iOSDefaults",  # Remplacez par l'URL réelle
	classifiers = [
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		"Operating System :: OS Independent",
	],
	python_requires = ">=3.6",
	license = "GPL-3.0-or-later",  # Indication explicite de la licence
)
