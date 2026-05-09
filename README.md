# Commute Copilot Bangalore
AI Agent to tackle commute problem, assisting with routes, mode and time. Using Open crawler, Jina embeddings v5, Elastic Inference Service, Kibana, EC2
Built for the AWS UG Bengaluru HackNight hackathon.

## Problem Statement
### Commute Intelligence
The goal of this project is to build an agent that answers it with reasoning, grounded in real feeds and explained transparently with the calculation: traffic, BMTC, Metro, parking, weather, and whether the schools are letting out early, multiplied by which route, which mode, and which time.
Example:
> Leave in 18 minutes, take Metro to MG Road, walk the last kilometre — here’s why.

## Project Overview
RouteWise Bengaluru is a multi-agent commute planner that helps users decide:
- when to leave
- which route to take, why that route is better
- which mode of transport to choose
- what risks exist, what alternatives are available
Instead of giving only a map route, Commute-Copilot gives a commute decision with transparent reasoning.

## Final Tech Stack
### Agent Development
- Elastic Agent Builder
- Amazon Bedrock

### LLMs
- Claude 3.5 Sonnet via Amazon Bedrock for Supervisor Agent and complex reasoning
- Amazon Nova Lite / Claude Haiku for lightweight specialist agents

### Search and Retrieval
- Elasticsearch on Elastic Cloud Serverless
- ES|QL
- Hybrid search
- Vector search

### Embeddings
- Jina Embeddings v5
- Model: `jina-embeddings-v5-text-small`
- Used for semantic retrieval over commute context, advisories, events, parking notes, and previous decisions

### Data Collection
- Python ingestion scripts
- Lightweight crawler / Elastic Open Crawler
- Open-Meteo API
- OSRM / OpenStreetMap route data
- Manual Bengaluru commute dataset

### Visualization
- Kibana dashboard

### Deployment
No custom EC2 deployment is required for the MVP.

The system uses:
- Elastic Cloud Serverless for Elasticsearch and Kibana
- Amazon Bedrock for LLM reasoning
- Local Python scripts for ingestion and crawling
- Elastic Agent Builder for the agent demo

The goal is to build a working, explainable, multi-agent commute intelligence system using Elastic and AWS.

## High-Level Architecture
```mermaid
flowchart TD
    User[User Commute Query] --> Supervisor[RouteWise Supervisor Agent]

    Supervisor --> Weather[Weather Agent]
    Supervisor --> RouteTraffic[Route + Traffic Agent]
    Supervisor --> Transit[Transit Context Agent]

    Weather --> WeatherAPI[Open-Meteo API]
    RouteTraffic --> RouteAPI[OSRM / Sample Route Data]
    RouteTraffic --> Elastic[Elasticsearch on Elastic Cloud Serverless]
    Transit --> Elastic

    Crawler[Crawler / Open Crawler] --> Ingestion[Python Ingestion Scripts]
    Ingestion --> Jina[Jina Embeddings v5]
    Jina --> Elastic

    Supervisor --> Final[Final Recommendation]
    Final --> DecisionLogs[Decision Logs]
    DecisionLogs --> Elastic
    Elastic --> Kibana[Kibana Dashboard]
