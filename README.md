# LLM Chatbot

[![Powered by Kedro](https://img.shields.io/badge/powered_by-kedro-ffc900?logo=kedro)](https://kedro.org)

## Overview

A Retrieval-Augmented Generation (RAG) system for scraping website data, embedding text, and answering questions via LLM


## How to install dependencies

Declare any dependencies in `requirements.txt` and `pyproject.toml` for `pip` installation.

To install them, run:
```
git clone https://github.com/DeliciousBoy/llm-chatbot-backend.git
cd llm-chatbot-backend
```
```
uv venv
.venv\Scripts\activate # Window
source .venv/bin/activate # Unix
```
```
pip install -r requirements.txt
```
```
uv install -e .[dev, doc]
```

## How to run Kedro pipeline

You can run your Kedro project with:

```
kedro run
```

## How to test your Kedro project
```
pytest tests/
```

## How to run chat interface
```
streamlit run main.py
```

## Proejct Structure
```
📁llm-chatbot-backend/
├── 📁conf/ # Kedro configuration files
│ └── 📁base/
│   └──📄catalog.yml
│   └──📄parameters.yml
├── 📁data/ # raw/cleaned/embedded/chromadb
├── 📁src/ # Source code (Kedro pipelines, modules)
│ └── 📁llm_chatbot_backend/
│   └── 📁datasets/
│   |   └── 📄utf8_json.py # Custom JSON
│   └── 📁pipelines/
│       └── 📁data_processing/
│       |  └──📄nodes.py
│       |  └──📄pipeline.py
│       └── 📁web_scraping/
│          └──📄nodes.py
│          └──📄pipeline.py
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
