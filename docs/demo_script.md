# Demo Script

## Setup Before Demo

1. Create Elastic Cloud Serverless project.
2. Put `ELASTICSEARCH_URL` and `ELASTICSEARCH_API_KEY` in `.env`.
3. Optionally add `JINA_API_KEY`.
4. Run:

```bash
python elastic/create_indices.py
python ingestion/generate_embeddings.py
python ingestion/ingest_sample_data.py
```

5. Load the agent markdown files into Elastic Agent Builder.
6. Configure Bedrock models:
   - Claude 3.5 Sonnet for Supervisor and Route + Traffic
   - Amazon Nova Lite or Claude Haiku for Weather and Transit

## Opening Story

Every Bengaluru commute is a multi-variable decision: traffic, Metro, BMTC, rain, parking, last-mile effort, and time pressure. CommuteCopilot turns that uncertainty into an explained recommendation.

## Live Query

```txt
I am at Spice Garden and need to reach MG Road by 6 PM. What should I do?
```

## Expected Agent Answer

```txt
Leave in 18 minutes.

Best option: Metro + walk.

Route: Spice Garden -> Indiranagar Metro -> MG Road -> walk 900m.

Why:
- Metro is more predictable during evening traffic.
- Cab has high congestion risk around Domlur and Indiranagar.
- Parking near MG Road is unreliable during evening hours.
- Rain risk is moderate, but the last-mile walk is manageable with an umbrella.

Alternative:
Cab via Old Airport Road, but it has lower reliability because congestion and parking search time are both high.

Confidence: 84%
```

## Kibana Moment

Show:

- indexed commute context
- hotspot and parking documents
- route records
- decision log for the live query

## Closing Line

CommuteCopilot is not trying to replace maps. It sits one level above maps: it explains which commute tradeoff is actually worth taking right now.
