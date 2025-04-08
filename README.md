# LLM Chatbot

[![Powered by Kedro](https://img.shields.io/badge/powered_by-kedro-ffc900?logo=kedro)](https://kedro.org)

## Overview

A Retrieval-Augmented Generation (RAG) system for scraping website data, embedding text, and answering questions via LLM


## How to install dependencies

Declare any dependencies in `requirements.txt` and `pyproject.toml` for `pip` installation.

### clone the repository
```
git clone https://github.com/DeliciousBoy/llm-chatbot-backend.git
cd llm-chatbot-backend
```

### Installing `uv`
this project uses `uv` to manage virtual environments and dependencies for different Python versions. You can install `uv` run:

```
curl -Ls https://astral.sh/uv/install.sh | sh
```
Or follow the instructions from the official GitHub repository: https://github.com/astral-sh/uv
Once installed, you can set up the environment with:


### Install with `uv` (Recommended) `This project requires Python 3.11.11`
```
uv venv
source .venv/bin/activate # Or .venv/Scripts/activate for Windows
uv pip install -r requirements.txt
uv pip install -e .[dev, docs]
```
If you prefer not to use uv, you can fall back to pip (see below).

### Install with `pip` (Not recommended)
This is not recommended as it may lead to dependency conflicts, especially if you are using different Python versions.
```
python -m venv .venv
source .venv/bin/activate # Or .venv/Scripts/activate for Windows
pip install -r requirements.txt
pip install -e .[dev,docs]
```

## How to run Kedro pipeline

You can run your Kedro project with:

```
kedro run
```

## How to test your Kedro project
this project uses `pytest` to run test cases. You can run your tests with:

```
pytest
```

## How to run chat interface
This project includes a Streamlit app for interacting with the chatbot. You can run the app with:

```
streamlit run main.py
```
To run the app locally, make sure the virtual environment is activated and dependencies are installed

## Proejct Structure
This project follows the [Kedro](https://kedro.org) project layout with additional components for web scraping, vector embeddings, and an LLM chatbot interface via Streamlit.
```
📁llm-chatbot-backend/
├── 📁conf/ # Kedro configuration files
│ └── 📁base/
│   └──📄catalog.yml # Dataset definitions (inputs/outputs for pipelines)
│   └──📄parameters.yml # Project-level parameters for nodes/pipelines
├── 📁data/ # raw/cleaned/embedded/chromadb
├── 📁src/ # Source code (Kedro pipelines, modules)
│ └── 📁llm_chatbot_backend/
│   └── 📁datasets/ # Custom Kedro dataset classes
│   |   └── 📄utf8_json.py # Custom JSON
│   └── 📁pipelines/ # All Kedro pipelines
│       └── 📁data_processing/
│       |  └──📄nodes.py  # Data cleaning / embedding logic
│       |  └──📄pipeline.py # Defines the data_processing pipeline
│       └── 📁web_scraping/
│          └──📄nodes.py # Async scraping logic
│          └──📄pipeline.py # Defines the web_scraping pipeline
├── 📁tests/ # Pytest test cases
│   └── 📁pipelines/
│       └── 📁data_processing/
│       |   └──📄test_pipeline.py
│       └── 📁web_scraping/
|           └──📄test_pipeline.py
├──📄main.py # Streamlit chat interface
├──📄pyproject.toml # Project config & dependencies
├──📄requirements.txt # Pip requirements
├──📄uv.lock # uv dependency lockfile
└──📄.env # Environment variables
```
