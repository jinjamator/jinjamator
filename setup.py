import setuptools
import os



with open("README.rst", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    install_requires = fh.read().split("\n")

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
    },

)
