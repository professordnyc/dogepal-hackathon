from setuptools import setup, find_packages

# Read requirements from both root and models/requirements.txt
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("models/requirements.txt") as f:
    model_requirements = f.read().splitlines()

# Combine requirements, removing duplicates
all_requirements = list(dict.fromkeys(requirements + model_requirements))

setup(
    name="dogepal",
    version="0.1.0",
    packages=find_packages(include=["app", "app.*", "models", "models.*"]),
    package_dir={
        "": ".",
        "app": "backend/app"
    },
    install_requires=all_requirements,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "dogepal-init-db=app.db.init_db:main",
            "dogepal-train=models.train:main",
        ],
    },
    # Include non-Python files like model artifacts
    include_package_data=True,
    package_data={
        "models": ["*.json", "*.joblib"],
    },
)
