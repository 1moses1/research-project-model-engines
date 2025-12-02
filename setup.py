#!/usr/bin/env python3
"""
Rwanda NCSA Compliance Auditor - Setup Script

This script installs the Rwanda NCSA Compliance Auditor CLI globally.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

setup(
    name="rwanda-ncsa-compliance-auditor",
    version="1.0.0",
    description="Rwanda NCSA Compliance Auditor - Comprehensive compliance auditing tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rwanda NCSA Compliance Team",
    author_email="compliance@ncsa.gov.rw",
    url="https://github.com/rwanda-ncsa/compliance-auditor",
    license="Proprietary",

    packages=find_packages(),
    include_package_data=True,

    python_requires=">=3.9",

    install_requires=[
        "click>=8.1.0",
        "rich>=13.0.0",
        "httpx>=0.25.0",
        "python-dotenv>=1.0.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.5.0",
        "PyJWT>=2.8.0",
    ],

    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "ml": [
            "xgboost>=2.0.0",
            "scikit-learn>=1.3.0",
            "pandas>=2.0.0",
            "numpy>=1.24.0",
        ],
    },

    entry_points={
        "console_scripts": [
            "rwanda-ncsa=cli.main:main",
        ],
    },

    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
    ],

    keywords="compliance, audit, security, ncsa, nist, regulatory",
)
