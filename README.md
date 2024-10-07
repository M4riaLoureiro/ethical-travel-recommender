# 🌏 TravelSEA Advisor: RAG-Powered Sustainable Travel Recommendations for Southeast Asia

This repository contains the code and resources for developing a Retrieval-Augmented Generation (RAG) system that provides trip plans and tourism recommendations for Southeast Asian countries. The focus is on promoting sustainable and ethical travel practices, leveraging data from WikiVoyage and sustainability-related content.


## Table of Contents

- [Problem Statement](#problem-statement)
  - [Key Features](#key-features)
  - [Data Sources](#data-source)
- [Evaluation Criteria Milestones](#evaluation-criteria-milestones) (hopefully a helper for project reviewers)
  - [Problem Definition](#problem-definition)
  - [RAG Flow](#rag-flow)
  - [Retrieval Evaluation](#retrieval-evaluation)
  - [RAG Evaluation](#rag-evaluation)
  - [Interface](#interface)
  - [Ingestion Pipeline](#ingestion-pipeline)
  - [Monitoring](#monitoring)
  - [Containerization](#containerization)
  - [Reproducibility](#reproducibility)
  - [Best Practices](#best-practices)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Best Practices Implemented](#best-practices-implemented)

## Problem Statement

In today’s travel industry, there is a growing demand for personalized and sustainable travel recommendations. This project introduces a RAG-based system that delivers contextually relevant, environmentally conscious travel suggestions specifically for Southeast Asian countries. While similar systems have been developed for major European cities, Southeast Asia, as one of the most popular holiday destinations globally, faces unique challenges.

With fewer protective laws and regulations, these countries are more vulnerable to the harmful impacts of mass tourism compared to their European counterparts. As a result, this project focuses on this region, which is particularly susceptible to the effects of climate change and overtourism.

### Key Features:
- **Customized Trip Plans:** Generates personalized travel itineraries based on user preferences, such as budget, travel style, and duration.
- **Sustainability Recommendations:** Highlights eco-friendly accommodations, local experiences, and sustainable travel tips to encourage responsible tourism.
- **Focus on Southeast Asia:** Specializes in recommendations for countries such as Thailand, Vietnam, Cambodia, Malaysia, Indonesia, and more.


### Data Sources
Currently, our knowledge base is built using data from Wikivoyage:
- **[WikiVoyage](https://en.wikivoyage.org/)**: A community-driven travel guide with comprehensive information on destinations, attractions, and travel tips.
- **Sustainability Pages on WikiVoyage**: Sections focused on sustainable tourism, including eco-friendly accommodations, ethical travel practices, and green transportation options.

These pages provide a good starting point for travel-related information. We acknowledge that this is a prototype version, and future iterations of the project could incorporate:
- Real-time data from verified travel sources
- Curated content from local tourism boards
- Verified sustainability metrics from environmental organizations
- User-generated content with proper review mechanisms


## Evaluation Criteria Milestones

### Problem definition

The problem is explain in the top of this readme file with references to previous projects developed with a similar motivation: [Problem Statement](#problem-statement).

### RAG Flow
Notebook: [📊 RAG Flow Implementation](notebooks/04_rag_experiments.ipynb)

RAG experiments notebooks includs the implementation of a knowledge base and an LLM that together compose the RAG system.

### Retrieval Evaluation
Notebook: [📈 Retrieval Analysis](notebooks/03_evaluate_retrieval_options.ipynb)

We conducted a comprehensive comparison of different retrieval approaches:

1. MinSearch:
   - [MinSearch](https://github.com/alexeygrigorev/minsearch) is a minimal vector similarity search implementation by Alexey Grigorev

2. Chroma DB, where two embedding models were compared:
   - Model 1: multi-qa-mpnet-base-dot-v1
   - Model 2: bge-large-en-v1.5

3. PGVector with hybrid search and scalability features 

These were the chosen Evaluation Metrics:
- Hit Rate (HR)
- Mean Reciprocal Rank (MRR)

The ground truth dataset for these evaluations was create using the notebook [Generate Ground Truth](notebooks/02_generate_ground_truth.ipynb).

In the end, the chosen retrieval system was pgvector (data and discussion of the decision process can be found on the notebook).


### RAG Evaluation
0 points: No evaluation of RAG is provided
1 point: Only one RAG approach (e.g., one prompt) is evaluated
2 points: Multiple RAG approaches are evaluated, and the best one is used
Notebook: [🎯 RAG Performance Analysis](notebooks/rag_evaluation.ipynb)
- Prompt engineering experiments
- Answer relevance assessment
- Factual accuracy verification
- Human evaluation results

### Interface
0 points: No way to interact with the application at all
1 point: Command line interface, a script, or a Jupyter notebook
2 points: UI (e.g., Streamlit), web application (e.g., Django), or an API (e.g., built with FastAPI)
[💻 API Documentation](docs/api.md)

Our system provides two interfaces:
1. REST API (FastAPI)
2. Web UI (Streamlit)

![Interface Example
](image.png)
### Ingestion Pipeline
0 points: No ingestion
1 point: Semi-automated ingestion of the dataset into the knowledge base, e.g., with a Jupyter notebook
2 points: Automated ingestion with a Python script or a special tool (e.g., Mage, dlt, Airflow, Prefect)
- Data Sources: Wikivoyage content for Southeast Asian countries
- ETL Pipeline development: [Process PDF Documents Notebook](notebooks/01_process_pdf_documents.ipynb) 
- Automated ETL Process with text cleaning, chunking, embedding and indexing to the vector store:

### Monitoring

User feedback is collected with interactive buttons and the feedback is saved in a json file.

### Containerization

0 points: No containerization
1 point: Dockerfile is provided for the main application OR there's a docker-compose for the dependencies only
2 points: Everything is in docker-compose
[🐳 Container Documentation](docker/README.md)

```bash
# Start all services
docker-compose up -d

# Access the UI
open http://localhost:8501
```

### Reproducibility

You can find all of the instructions on how to run the code in the [Getting Started](#getting-started) Section.

The pdf files exported from WikiVoyage can be found in the /data folder. For the processing of these pdf files, we have used marker-pdf, a library that requires some heavy gpu processing, so you can also find in the /data folder a pickle file with the pdf documents already preprocessed (docs_processed.pickle).

### Best practices

Hybrid search has been implemented to combine both text and vector search together, improving the retrieval system accuracy.

## Repository Structure

```plaintext
├── data                        # Scripts for data collection and pre-processing
├── ethical_travel_recommender  # Source code for the RAG system
├── notebooks                   # Jupyter notebooks for exploratory data analysis and prototyping
├── utils                       # Utility scripts for common tasks
├── docker                      # Docker files for containerization
├── requirements.txt            # Dependencies required to run the project
└── README.md                   # This README file
```

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.9+
- OpenAI API key
- HuggingFace API key

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/travelsea-advisor.git

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the application
docker-compose up
```