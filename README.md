# Commute Copilot Bangalore
AI Agent to tackle commute problem, assisting with routes, mode and time. Using Open crawler, Jina embeddings v5, Elastic Inference Service, Kibana, EC2

AI-powered commute intelligence agent for Bengaluru, built for the AWS UG Bengaluru HackNight hackathon.

## Problem Statement

### Commute Intelligence

Every Bengaluru morning is the same calculation: traffic, BMTC, Metro, parking, weather, and whether the schools are letting out early, multiplied by which route, which mode, and which time.

People usually answer this question with vibes.

The goal of this project is to build an agent that answers it with reasoning, grounded in real feeds and explained transparently.

Example output:

> Leave in 18 minutes, take Metro to MG Road, walk the last kilometre — here’s why.

## Project Idea

RouteWise Bengaluru is an AI commute planner that recommends when to leave, which mode to take, and why that option is better.

The agent considers:
- traffic risk
- Metro/BMTC availability
- weather
- parking difficulty
- events or school/office timing patterns
- last-mile walking effort
- route confidence score

## Hackathon Context

This is a hackathon project for AWS UG Bengaluru HackNight.

Judging criteria:
- Real-world impact and relevance
- Data effort
- Elastic usage
- AWS usage
- Actionability and security practices
- Demo quality and storytelling

## Tech Stack

### Frontend
- Next.js
- Tailwind CSS

### Backend
- FastAPI or Node.js/Express
- REST APIs for commute recommendations

### Agent Layer
- Amazon Bedrock for LLM reasoning
- Elastic Agent Builder for agent workflow
- Tool-based reasoning for route, weather, traffic, and context lookup

### Search and Retrieval
- Elastic Cloud Serverless
- Elasticsearch
- ES|QL
- Jina Embeddings v5
- Vector search for route/context retrieval
- Kibana dashboard for demo and observability

### AWS
- Amazon Bedrock
- EC2 for backend deployment
- S3 for storing raw commute/context data
- Lambda optional for scheduled crawling
- CloudWatch optional for logs

## Architecture

User enters source, destination, target arrival time, and preferences.

The backend sends this query to the agent.

The agent uses tools to:
1. Search indexed commute data in Elasticsearch
2. Retrieve relevant route/context records using vector search
3. Check weather and traffic risk
4. Compare commute options
5. Generate a transparent recommendation

The final output includes:
- recommended leave time
- best route
- mode of transport
- explanation
- risks
- confidence score
- alternate options

## Example Query

```txt
I am at Spice Garden and need to reach MG Road by 6 PM. What should I do?
