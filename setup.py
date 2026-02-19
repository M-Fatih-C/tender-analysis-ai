"""TenderAI - İhale Şartname Analiz Platformu / Tender Specification Analysis Platform."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip()
        for line in fh
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="tender-analysis-ai",
    version="0.1.0",
    author="TenderAI Team",
    author_email="info@tenderai.com.tr",
    description="Yapay zeka destekli ihale teknik şartname analiz platformu",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/<kullanici>/tender-analysis-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.14",
        "Topic :: Office/Business",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.12",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "tenderai=ui.app:main",
        ],
    },
)
