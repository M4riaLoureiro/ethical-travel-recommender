# Sustainable Tourism Recommender for Southeast Asia

This repository contains the code and resources for developing a Retrieval-Augmented Generation (RAG) system that provides trip plans and tourism recommendations for Southeast Asian countries. The focus is on promoting sustainable and ethical travel practices, leveraging data from WikiVoyage and sustainability-related content.

## Project Overview

**Ethical Travel Recommender** is an AI-based system designed to help travelers plan eco-friendly and ethical trips across Southeast Asia. It uses a Retrieval-Augmented Generation (RAG) approach to combine the power of information retrieval and generative AI, ensuring that travel suggestions are both accurate and insightful, with a strong emphasis on sustainability.

### Key Features:
- **Customized Trip Plans:** Generates personalized travel itineraries based on user preferences, such as budget, travel style, and duration.
- **Sustainability Recommendations:** Highlights eco-friendly accommodations, local experiences, and sustainable travel tips to encourage responsible tourism.
- **Focus on Southeast Asia:** Specializes in recommendations for countries such as Thailand, Vietnam, Cambodia, Malaysia, Indonesia, and more.

## Data Sources

The system uses data from the following sources:
- **[WikiVoyage](https://en.wikivoyage.org/)**: A community-driven travel guide with comprehensive information on destinations, attractions, and travel tips.
- **Sustainability Pages on WikiVoyage**: Sections focused on sustainable tourism, including eco-friendly accommodations, ethical travel practices, and green transportation options.

## Repository Structure

```plaintext
├── data                        # Scripts for data collection and pre-processing
├── ethical_travel_recommender  # Source code for the RAG system
├── notebooks                   # Jupyter notebooks for exploratory data analysis and prototyping
├── utils                       # Utility scripts for common tasks
├── docker                      # Docker files for containerization
├── requirements.txt            # Dependencies required to run the project
└── README.md                   # This README file