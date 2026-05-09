# Judging Mapping

## Real-World Impact

Bengaluru commuters often choose between cab, Metro, BMTC, walking, and parking uncertainty under time pressure. RouteWise gives a clear action instead of another raw route list.

## Data Effort

The MVP combines:

- traffic hotspots
- metro station context
- parking zones
- route alternatives
- weather risk
- BMTC and last-mile notes
- contextual commute advisories
- final decision logs

## Elastic Usage

Elastic is central to the architecture:

- structured search over places and routes
- vector search over contextual commute notes
- hybrid retrieval for local evidence
- ES|QL route-risk exploration
- decision logging to Elasticsearch
- Kibana dashboard for demo and judging

## AWS Usage

Amazon Bedrock provides model reasoning:

- Claude 3.5 Sonnet for Supervisor Agent
- Claude 3.5 Sonnet for Route + Traffic Agent
- Amazon Nova Lite or Claude Haiku for Weather and Transit Context Agents

## Actionability

The answer includes:

- leave time
- selected route
- selected mode
- explanation
- risks
- alternatives
- confidence score

## Security

- Secrets live in `.env`, not source code.
- The MVP avoids storing personal identifiers.
- Decision logs contain commute decisions, not user profiles.
- API calls are limited to required data sources.

## Demo Quality

The demo is reliable because crawling and ingestion happen before the live query. During the live demo, agents retrieve from Elasticsearch, call stable tools, reason over evidence, and log the final decision.
