#!/usr/bin/env python3
"""
Test script to build and deploy basic Make.com workflows using the Python client.
This demonstrates:
1. SMS reminder workflow (scheduling)
2. Email follow-up workflow (lead nurturing)
3. Basic chatbot workflow (customer communication)
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add make_client to path
sys.path.insert(0, str(Path(__file__).parent.parent / "make_client"))

from make_client import Make, RateLimitError, ServerError, AuthenticationError


async def test_basic_connectivity():
    """Test basic API connectivity and organization info."""
    print("\n" + "="*60)
    print("TEST 1: Basic Connectivity")
    print("="*60)
    
    try:
        make = Make(token=os.getenv("MAKE_API_KEY"))
        org = await make.organizations.get()
        print(f"✅ Connected to Make.com")
        print(f"   Organization: {org.get('name', 'N/A')}")
        print(f"   ID: {org.get('id')}")
        return True
    except AuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


async def test_list_scenarios():
    """List existing scenarios."""
    print("\n" + "="*60)
    print("TEST 2: List Scenarios")
    print("="*60)
    
    try:
        make = Make(token=os.getenv("MAKE_API_KEY"))
        
        # Get first team (most users have at least one)
        teams = await make.teams.list()
        if not teams:
            print("⚠️  No teams found")
            return False
        
        team_id = teams[0].get('id')
        print(f"✅ Using team: {teams[0].get('name')} (ID: {team_id})")
        
        # List scenarios
        scenarios = await make.scenarios.list(team_id=team_id)
        print(f"✅ Found {len(scenarios)} scenarios")
        
        for scenario in scenarios[:5]:  # Show first 5
            print(f"   - {scenario.get('name')} (ID: {scenario.get('id')})")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_create_sms_reminder_workflow():
    """Create a basic SMS reminder workflow template."""
    print("\n" + "="*60)
    print("TEST 3: SMS Reminder Workflow Blueprint")
    print("="*60)
    
    try:
        make = Make(token=os.getenv("MAKE_API_KEY"))
        
        # SMS Reminder workflow structure
        sms_workflow = {
            "name": "SMS Appointment Reminder",
            "description": "Send SMS reminder 24 hours before appointment",
            "type": "scheduling",
            "modules": [
                {
                    "id": 1,
                    "type": "webhook",
                    "name": "Appointment Scheduled",
                    "config": {
                        "hook": "custom_webhook",
                        "data_structure": {
                            "appointment_time": "datetime",
                            "phone_number": "string",
                            "customer_name": "string"
                        }
                    }
                },
                {
                    "id": 2,
                    "type": "scheduling",
                    "name": "Schedule 24h Reminder",
                    "config": {
                        "delay": 86400,  # 24 hours in seconds
                        "time_unit": "seconds"
                    }
                },
                {
                    "id": 3,
                    "type": "twilio",
                    "name": "Send SMS Reminder",
                    "config": {
                        "to": "{{1.phone_number}}",
                        "body": "Hi {{1.customer_name}}, reminder: your appointment is tomorrow at {{1.appointment_time}}. Reply STOP to opt out."
                    }
                }
            ],
            "connections_required": ["twilio"],
            "estimated_hours": 10
        }
        
        print("✅ SMS Reminder Workflow Blueprint:")
        print(json.dumps(sms_workflow, indent=2))
        
        # Save blueprint
        blueprint_path = Path(__file__).parent / "workflows" / "sms_reminder_blueprint.json"
        blueprint_path.parent.mkdir(exist_ok=True)
        with open(blueprint_path, 'w') as f:
            json.dump(sms_workflow, f, indent=2)
        print(f"\n✅ Saved to: {blueprint_path}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_create_lead_followup_workflow():
    """Create a lead follow-up workflow template."""
    print("\n" + "="*60)
    print("TEST 4: Lead Follow-Up Workflow Blueprint")
    print("="*60)
    
    try:
        make = Make(token=os.getenv("MAKE_API_KEY"))
        
        # Lead follow-up workflow
        lead_workflow = {
            "name": "Lead Follow-Up Automation",
            "description": "Nurture leads with personalized emails and track engagement",
            "type": "crm",
            "modules": [
                {
                    "id": 1,
                    "type": "typeform",
                    "name": "Lead Form Submission",
                    "config": {
                        "form_id": "{{FORM_ID}}",
                        "fields": ["name", "email", "phone", "service_interested"]
                    }
                },
                {
                    "id": 2,
                    "type": "airtable",
                    "name": "Store Lead in Database",
                    "config": {
                        "table": "Leads",
                        "fields": {
                            "Name": "{{1.name}}",
                            "Email": "{{1.email}}",
                            "Phone": "{{1.phone}}",
                            "Service": "{{1.service_interested}}",
                            "Submitted": "{{now}}"
                        }
                    }
                },
                {
                    "id": 3,
                    "type": "openai",
                    "name": "Generate Personalized Message",
                    "config": {
                        "model": "gpt-4",
                        "prompt": "Write a friendly 50-word follow-up email for {{1.name}} who is interested in {{1.service_interested}}. Start with gratitude for their inquiry."
                    }
                },
                {
                    "id": 4,
                    "type": "gmail",
                    "name": "Send Follow-Up Email",
                    "config": {
                        "to": "{{1.email}}",
                        "subject": "Hi {{1.name}} - Let's talk about {{1.service_interested}}",
                        "body": "{{3.message}}\n\nBest regards,\nCatalyst Team"
                    }
                },
                {
                    "id": 5,
                    "type": "airtable",
                    "name": "Update Lead Status",
                    "config": {
                        "table": "Leads",
                        "action": "update",
                        "record_id": "{{2.id}}",
                        "fields": {
                            "Status": "Email Sent",
                            "Follow-up Sent": "{{now}}"
                        }
                    }
                }
            ],
            "connections_required": ["typeform", "airtable", "openai", "gmail"],
            "estimated_hours": 12
        }
        
        print("✅ Lead Follow-Up Workflow Blueprint:")
        print(json.dumps(lead_workflow, indent=2))
        
        # Save blueprint
        blueprint_path = Path(__file__).parent / "workflows" / "lead_followup_blueprint.json"
        blueprint_path.parent.mkdir(exist_ok=True)
        with open(blueprint_path, 'w') as f:
            json.dump(lead_workflow, f, indent=2)
        print(f"\n✅ Saved to: {blueprint_path}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_create_chatbot_workflow():
    """Create a customer chatbot workflow template."""
    print("\n" + "="*60)
    print("TEST 5: Customer Chatbot Workflow Blueprint")
    print("="*60)
    
    try:
        make = Make(token=os.getenv("MAKE_API_KEY"))
        
        # Chatbot workflow
        chatbot_workflow = {
            "name": "Customer Support Chatbot",
            "description": "AI-powered chatbot for FAQ and simple customer inquiries",
            "type": "customer_support",
            "modules": [
                {
                    "id": 1,
                    "type": "twilio",
                    "name": "Receive SMS",
                    "config": {
                        "trigger": "incoming_sms"
                    }
                },
                {
                    "id": 2,
                    "type": "airtable",
                    "name": "Get Knowledge Base",
                    "config": {
                        "table": "FAQ",
                        "view": "All",
                        "fields": ["question", "answer", "category"]
                    }
                },
                {
                    "id": 3,
                    "type": "openai",
                    "name": "Generate AI Response",
                    "config": {
                        "model": "gpt-4",
                        "prompt": "You are a customer support bot. Customer asked: '{{1.message}}'. Use this knowledge base to answer: {{2.faq}}. Keep response to 160 characters for SMS. If question is not in FAQ, offer to transfer to human.",
                        "max_tokens": 50
                    }
                },
                {
                    "id": 4,
                    "type": "twilio",
                    "name": "Send SMS Reply",
                    "config": {
                        "to": "{{1.from_number}}",
                        "body": "{{3.response}}"
                    }
                },
                {
                    "id": 5,
                    "type": "airtable",
                    "name": "Log Conversation",
                    "config": {
                        "table": "Chat Logs",
                        "fields": {
                            "Customer": "{{1.from_number}}",
                            "Message": "{{1.message}}",
                            "Response": "{{3.response}}",
                            "Timestamp": "{{now}}"
                        }
                    }
                }
            ],
            "connections_required": ["twilio", "airtable", "openai"],
            "estimated_hours": 15
        }
        
        print("✅ Customer Chatbot Workflow Blueprint:")
        print(json.dumps(chatbot_workflow, indent=2))
        
        # Save blueprint
        blueprint_path = Path(__file__).parent / "workflows" / "chatbot_blueprint.json"
        blueprint_path.parent.mkdir(exist_ok=True)
        with open(blueprint_path, 'w') as f:
            json.dump(chatbot_workflow, f, indent=2)
        print(f"\n✅ Saved to: {blueprint_path}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_create_quote_generator_workflow():
    """Create a quote/estimate generator workflow template."""
    print("\n" + "="*60)
    print("TEST 6: Quote Generator Workflow Blueprint")
    print("="*60)
    
    try:
        make = Make(token=os.getenv("MAKE_API_KEY"))
        
        # Quote generator workflow
        quote_workflow = {
            "name": "Quote Generator & Email",
            "description": "Generate custom quotes and send via email automatically",
            "type": "automation",
            "modules": [
                {
                    "id": 1,
                    "type": "typeform",
                    "name": "Quote Request Form",
                    "config": {
                        "form_id": "{{FORM_ID}}",
                        "fields": ["customer_name", "email", "service", "scope", "urgency"]
                    }
                },
                {
                    "id": 2,
                    "type": "google_docs",
                    "name": "Generate Quote from Template",
                    "config": {
                        "template_id": "{{TEMPLATE_ID}}",
                        "replacements": {
                            "{{CUSTOMER}}": "{{1.customer_name}}",
                            "{{SERVICE}}": "{{1.service}}",
                            "{{SCOPE}}": "{{1.scope}}",
                            "{{DATE}}": "{{now|formatDate:'YYYY-MM-DD'}}",
                            "{{PRICE}}": "{{calculatePrice(1.service, 1.urgency)}}"
                        }
                    }
                },
                {
                    "id": 3,
                    "type": "pdfmonkey",
                    "name": "Convert to PDF",
                    "config": {
                        "document_url": "{{2.document_url}}",
                        "format": "pdf"
                    }
                },
                {
                    "id": 4,
                    "type": "gmail",
                    "name": "Email Quote to Customer",
                    "config": {
                        "to": "{{1.email}}",
                        "subject": "Your Quote: {{1.service}} - {{1.customer_name}}",
                        "body": "Hi {{1.customer_name}},\n\nAttached is your quote for {{1.service}}.\n\nPlease reply with any questions. Quote valid for 30 days.\n\nBest regards,\nQuote Team",
                        "attachments": ["{{3.pdf_url}}"]
                    }
                },
                {
                    "id": 5,
                    "type": "airtable",
                    "name": "Log Quote in CRM",
                    "config": {
                        "table": "Quotes",
                        "fields": {
                            "Customer": "{{1.customer_name}}",
                            "Email": "{{1.email}}",
                            "Service": "{{1.service}}",
                            "Sent": "{{now}}",
                            "PDF": "{{3.pdf_url}}"
                        }
                    }
                }
            ],
            "connections_required": ["typeform", "google_docs", "pdfmonkey", "gmail", "airtable"],
            "estimated_hours": 7
        }
        
        print("✅ Quote Generator Workflow Blueprint:")
        print(json.dumps(quote_workflow, indent=2))
        
        # Save blueprint
        blueprint_path = Path(__file__).parent / "workflows" / "quote_generator_blueprint.json"
        blueprint_path.parent.mkdir(exist_ok=True)
        with open(blueprint_path, 'w') as f:
            json.dump(quote_workflow, f, indent=2)
        print(f"\n✅ Saved to: {blueprint_path}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def main():
    """Run all workflow tests."""
    print("\n" + "="*60)
    print("CATALYST: Make.com Workflow Testing Suite")
    print("="*60)
    
    # Get API key
    api_key = os.getenv("MAKE_API_KEY")
    if not api_key:
        # Try to read from file
        try:
            with open(Path.home() / ".catalyst_make_key", "r") as f:
                api_key = f.read().strip()
                os.environ["MAKE_API_KEY"] = api_key
        except FileNotFoundError:
            print("❌ MAKE_API_KEY not found in environment or ~/.catalyst_make_key")
            sys.exit(1)
    
    print(f"✅ Using API key: {api_key[:20]}...")
    
    # Run tests
    results = []
    results.append(("Connectivity", await test_basic_connectivity()))
    results.append(("List Scenarios", await test_list_scenarios()))
    results.append(("SMS Reminder", await test_create_sms_reminder_workflow()))
    results.append(("Lead Follow-Up", await test_create_lead_followup_workflow()))
    results.append(("Chatbot", await test_create_chatbot_workflow()))
    results.append(("Quote Generator", await test_create_quote_generator_workflow()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    # Show saved workflows
    workflows_dir = Path(__file__).parent / "workflows"
    if workflows_dir.exists():
        print(f"\n✅ Workflow blueprints saved to: {workflows_dir}")
        for f in sorted(workflows_dir.glob("*.json")):
            print(f"   - {f.name}")


if __name__ == "__main__":
    asyncio.run(main())
