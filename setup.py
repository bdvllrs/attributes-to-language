from setuptools import find_packages, setup


def get_requirements():
    with open("requirements.txt", "r") as f:
        requirements = f.read().splitlines()
    return requirements


def get_version():
    with open("version.txt", "r") as f:
        version = f.read().lstrip("\n")
    return version


if __name__ == '__main__':
    setup(name='attributes_to_language',
          version=get_version(),
          install_requires=get_requirements(),
          packages=find_packages(),
          )
