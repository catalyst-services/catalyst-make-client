# Catalyst Make.com Python Client

Tools for automating Make.com workflow deployment and management for service business automations.

## What's Included

- **test_api_connectivity.py** — Validate Make.com API key and connection
- **test_workflows.py** — Test workflow blueprints before deployment
- **create_workflow_blueprints.py** — Generate workflow JSON blueprints for Make.com
- **pyproject.toml** — Python project configuration

## Quick Start

### 1. Install Dependencies

```bash
pip install aiohttp pydantic python-dotenv
```

### 2. Set Your Make.com API Key

```bash
export MAKE_API_KEY="your_api_key_here"
```

Or save to `~/.catalyst_make_key`:
```bash
echo "your_api_key_here" > ~/.catalyst_make_key
```

### 3. Test Connection

```bash
python3 test_api_connectivity.py
```

### 4. Generate Workflow Blueprints

```bash
python3 create_workflow_blueprints.py
```

## What We Automate

- **Lead Follow-Up** — Instant SMS responses to new leads
- **Job Management** — Appointment reminders, invoicing, quote generation
- **Reviews & Reputation** — Review requests, negative review alerts, AI-drafted responses
- **Recurring Services** — Automated reminders for service intervals

## Integration Points

- Jobber / Calendly / Acuity (scheduling)
- QuickBooks / Xero / Stripe (payments & invoicing)
- Twilio (SMS)
- Google Business Profile / Google Reviews (reputation)
- HubSpot / Airtable (CRM)
- Facebook Ads / Google Ads (lead capture)
- Make.com (workflow automation)

## Development

The Python client is designed to:

1. Validate Make.com API connectivity
2. Deploy workflow blueprints
3. Test automations before going live
4. Manage scenarios and executions

## Contact

📧 catalyst.ai.services@gmail.com  
📞 (619) 800-2253  
🏢 San Diego, CA
