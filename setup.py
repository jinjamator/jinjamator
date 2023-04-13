import setuptools
import os
from pathlib import Path
root_path = Path(__file__).parent
version_file = f"{root_path}/jinjamator/VERSION"





with open("README.rst", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    install_requires = fh.read().split("\n")

try:
    from setuptools_git_versioning import version_from_git
    with open(version_file,"w") as fh:
        fh.write(version_from_git())
except ModuleNotFoundError:
    pass

setuptools.setup(
    name="jinjamator",
    author="Wilhelm Putz",
    author_email="jinjamator@aci.guru",
    description="Boilerplate-free scripting and IT automation for python programmers",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/jinjamator/jinjamator",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={"": ["*"]},
    install_requires=install_requires,
    license="ASL V2",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
     entry_points = {
        'console_scripts': ['jinjamator=jinjamator:__main__'],
    },
    python_requires=">=3.7",
    zip_safe=False,
    setup_requires=["setuptools-git-versioning<2"],
    setuptools_git_versioning={
        "enabled": True,
        'version_file': version_file

    },

)

from setuptools_git_versioning import version_from_git
with open(version_file,"w") as fh:
    fh.write(version_from_git())
