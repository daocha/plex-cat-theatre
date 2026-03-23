from pathlib import Path

from setuptools import find_packages, setup


ROOT = Path(__file__).resolve().parent
README = (ROOT / "README.md").read_text(encoding="utf-8")

PY_MODULES = [
    "cat_theatre_init",
    "movies",
    "movies_catalog",
    "movies_catalog_index",
    "movies_catalog_media",
    "movies_catalog_scan",
    "movies_catalog_workers",
    "movies_resources",
    "movies_server",
    "movies_server_auth",
    "movies_server_core",
    "movies_server_locale",
    "movies_server_media",
    "movies_server_overlay",
    "movies_server_plex",
    "passcode",
]


setup(
    name="plex-cat-theatre",
    version="0.1.0",
    description="Lightweight self-hosted movie browser and streaming server with optional Plex integration.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Dao Cha",
    license="MIT",
    python_requires=">=3.9",
    install_requires=[
        "Flask>=3.0,<4.0",
        "waitress>=3.0,<4.0",
    ],
    py_modules=PY_MODULES,
    packages=find_packages(include=["cat_theatre_assets", "cat_theatre_assets.*"]),
    package_data={
        "cat_theatre_assets": [
            "index.html",
            "movies.css",
            "movies.js",
            "movies.min.js",
            "plex.svg",
            "movies_config.sample.json",
            "locales/*.js",
            "server_locales/*.json",
        ]
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "plex-cat-theatre-init=cat_theatre_init:main",
            "plex-cat-theatre=movies_server:main",
            "plex-cat-theatre-passcode=passcode:main",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
