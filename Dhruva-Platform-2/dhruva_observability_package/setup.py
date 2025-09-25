"""
Setup script for dhruva-observability package
"""
from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="dhruva-observability",
    version="1.0.9",
    author="AI4X Team",
    author_email="team@ai4x.com",
    description="Enterprise observability plugin for Dhruva Platform",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ai4x/dhruva-observability",
    project_urls={
        "Bug Reports": "https://github.com/ai4x/dhruva-observability/issues",
        "Source": "https://github.com/ai4x/dhruva-observability",
        "Documentation": "https://github.com/ai4x/dhruva-observability/blob/main/README.md",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.68.0",
        "prometheus-client>=0.12.0",
        "psutil>=5.8.0",
        "pydantic>=1.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "gpu": [
            "nvidia-ml-py3>=7.352.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="dhruva, observability, monitoring, metrics, prometheus, fastapi, enterprise",
    entry_points={
        "console_scripts": [
            "dhruva-observability=dhruva_observability.cli:main",
        ],
    },
)
