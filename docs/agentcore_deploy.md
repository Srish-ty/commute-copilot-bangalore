# AgentCore Deploy Runbook

AgentCore is the hosted AWS runtime for the agent. Kibana is still the dashboard for Elasticsearch data.

## Local CLI Demo

From the repo root:

```powershell
py -3.10 main.py "I am at Spice Garden and need to reach MG Road by 6 PM. What should I do?" --use-bedrock --verbose
```

## Local AgentCore Dev Demo

AgentCore project files live in `CommuteCopilot/`. Run AgentCore commands from that folder.

Terminal 1:

```powershell
cd C:\Users\srush\Documents\GitHub\commute-copilot-bangalore\CommuteCopilot
agentcore dev --runtime commutecopilot_agent --logs --no-browser --port 8081
```

Keep Terminal 1 open.

Terminal 2:

```powershell
cd C:\Users\srush\Documents\GitHub\commute-copilot-bangalore\CommuteCopilot
agentcore dev --port 8081 --runtime commutecopilot_agent '{"prompt":"I am at Spice Garden and need to reach MG Road by 6 PM. What should I do?","use_bedrock":true}'
```

PowerShell note: use single quotes around the JSON payload.

## Deploy To AWS AgentCore

Before deploy:

```powershell
py -3.10 check_stack.py
```

Make sure Elastic is `ok` and Bedrock models are `ok`.

Then:

```powershell
cd C:\Users\srush\Documents\GitHub\commute-copilot-bangalore\CommuteCopilot
agentcore validate
agentcore deploy --target default --yes --verbose
agentcore status
```

Invoke deployed runtime:

```powershell
agentcore invoke --runtime commutecopilot_agent --prompt '{"prompt":"I am at Spice Garden and need to reach MG Road by 6 PM. What should I do?","use_bedrock":true}' --json
```

## What To Show In Demo

1. CLI or AgentCore invocation returns commute recommendation.
2. Output `trace` shows all agent nodes ran.
3. Output `evidence.route_traffic.elastic_evidence` and `evidence.transit.elastic_evidence` show Elasticsearch retrieval.
4. Kibana `Discover` shows documents in:
   - `commute_context`
   - `commute_places`
   - `commute_routes`
   - `commute_decision_logs`

## Important Notes

- Do not commit `.env` or `.env.local`.
- AgentCore is not the Kibana dashboard. It is the runtime/deployment layer.
- Kibana is where we show indexed data, vector fields, route docs, and decision logs.
