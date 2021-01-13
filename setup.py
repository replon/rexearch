import os

from setuptools import find_packages, setup

PACKAGE_NAME = "rexearch"


def get_version():
    with open(os.path.join(PACKAGE_NAME, "__init__.py"), "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                _, version = line.strip().split("=")
                version = version.strip()[1:-1]
                return version
    return None


def get_require_packages():
    require_packages = []
    with open("requirements.txt") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or line == "":
                continue

            require_packages.append(line)

    return require_packages


setup(
    name="package",  # Change package name
    version=get_version(),
    description="package description",
    python_requires=">=3.6.0",
    install_requires=get_require_packages(),
    url="https://github.com/replon/rexearch",
    author="Dylan Lee",
    author_email="replon87@gmail.com",
    packages=find_packages(exclude=["tests"]),
)
