from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="dogepal",
    version="0.1.0",
    packages=find_packages(include=["app", "app.*"]),
    package_dir={"": "backend"},
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "dogepal-init-db=app.db.init_db:main",
        ],
    },
)
