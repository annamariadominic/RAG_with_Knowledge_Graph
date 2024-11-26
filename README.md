# RAG with Knowledge Graph

This repository implements a **Retrieval-Augmented Generation (RAG)** framework enhanced with a **Knowledge Graph** to compare and analyze the effectiveness of integrating structured data in generating nuanced and actionable business insights.

## Objectives
The primary goal of this project is to:
- Compare traditional RAG with RAG+Knowledge Graph approaches.
- Demonstrate where and how knowledge graphs improve business insights.
- Explore workflows for both broad and specific queries.

## Features
- **Knowledge Graph Integration**:
  - Extracts structured data from company presentations and other documents.
  - Enhances query responses with additional context from the graph.
- **Dynamic Query Workflow**:
  - Broad queries combine both vector database and knowledge graph contexts.
  - Specific queries refine the vector database search using knowledge graph-derived context.
- **Comparison Analysis**:
  - Side-by-side comparison of responses with and without the knowledge graph.
  - AI-generated analysis of differences in depth, nuance, and relevance.
- **Streamlit App**:
  - Interactive interface to test and visualize RAG with and without knowledge graph integration.

## Repository Structure
```plaintext
├── chroma/                    # Vector database
├── data/                      # Raw document data
├── data_md/                   # Pre-processed Markdown files
├── companies.csv              # Knowledge graph nodes (companies)
├── products.csv               # Knowledge graph nodes (products)
├── relationships.csv          # Knowledge graph relationships
├── create_database.py         # Script to create vector database
├── markdown_to_neo4j.py       # Script to generate knowledge graph in Neo4j
├── query_helpers.py           # Helper functions for querying KG and vector DB
├── demo.py                    # Streamlit app for comparison
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
