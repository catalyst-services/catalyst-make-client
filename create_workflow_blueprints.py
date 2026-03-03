#!/usr/bin/env python3
"""
Create production workflow blueprints for Catalyst clients.
These blueprints define the structure of common workflows that will be deployed
to Make.com via the API.
"""

import json
from pathlib import Path
from datetime import datetime


def create_sms_reminder_blueprint():
    """SMS appointment reminder workflow."""
    return {
        "name": "SMS Appointment Reminder",
        "description": "Send SMS reminder 24 hours before appointment",
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "type": "scheduling",
        "use_case": "Reduce no-shows and keep customers informed",
        "implementation_hours": 10,
        "modules": [
            {
                "position": 1,
                "name": "Appointment Trigger",
                "type": "webhook",
                "app": "Make",
                "description": "Listen for new appointment scheduled events",
                "config": {
                    "trigger_type": "custom_webhook",
                    "expected_data": {
                        "appointment_id": "string",
                        "appointment_time": "datetime (ISO 8601)",
                        "customer_phone": "string (E.164 format)",
                        "customer_name": "string",
                        "service_type": "string"
                    }
                },
                "output_mapping": {
                    "appointment_id": "{{1.appointment_id}}",
                    "appointment_time": "{{1.appointment_time}}",
                    "customer_phone": "{{1.customer_phone}}",
                    "customer_name": "{{1.customer_name}}"
                }
            },
            {
                "position": 2,
                "name": "Schedule Delay",
                "type": "flow_control",
                "app": "Make",
                "description": "Wait 24 hours before sending reminder",
                "config": {
                    "delay_type": "until_datetime",
                    "target_datetime": "{{calculate(1.appointment_time, '-24h')}}",
                    "note": "Send reminder exactly 24 hours before appointment"
                }
            },
            {
                "position": 3,
                "name": "Send SMS Reminder",
                "type": "messaging",
                "app": "Twilio",
                "description": "Send SMS reminder via Twilio",
                "config": {
                    "from_number": "{{CLIENT_TWILIO_NUMBER}}",
                    "to_number": "{{1.customer_phone}}",
                    "message_template": "Hi {{1.customer_name}}, gentle reminder: you have an appointment tomorrow at {{format(1.appointment_time, 'h:mm A')}}. Reply STOP to opt-out."
                },
                "error_handling": {
                    "invalid_phone": "Log and skip",
                    "twilio_error": "Retry 2x with 5min delay"
                }
            },
            {
                "position": 4,
                "name": "Log Reminder Sent",
                "type": "database",
                "app": "Airtable",
                "description": "Record reminder sent for analytics",
                "config": {
                    "workspace": "{{CLIENT_AIRTABLE_WORKSPACE}}",
                    "table": "Appointment Reminders",
                    "fields": {
                        "Appointment ID": "{{1.appointment_id}}",
                        "Customer Name": "{{1.customer_name}}",
                        "Phone": "{{1.customer_phone}}",
                        "Reminder Sent": "{{now}}",
                        "Status": "Sent"
                    }
                }
            }
        ],
        "connections_required": [
            {
                "type": "twilio",
                "name": "Client Twilio Account",
                "description": "Client's own Twilio account (must have EIN verification)",
                "credentials_format": "Account SID + Auth Token"
            },
            {
                "type": "airtable",
                "name": "Client Airtable",
                "description": "Client's Airtable workspace for logging",
                "credentials_format": "Personal Access Token"
            }
        ],
        "testing": {
            "test_trigger": {
                "appointment_id": "apt_test_001",
                "appointment_time": "2026-03-03T14:00:00Z",
                "customer_phone": "+14155552671",
                "customer_name": "John Doe",
                "service_type": "Plumbing"
            },
            "expected_output": "SMS sent to +14155552671"
        },
        "deployment_checklist": [
            "✓ Verify client Twilio account configured",
            "✓ Test Twilio connection (test SMS)",
            "✓ Verify Airtable workspace access",
            "✓ Create 'Appointment Reminders' table in Airtable",
            "✓ Test webhook trigger",
            "✓ Run sample execution",
            "✓ Enable scenario"
        ]
    }


def create_lead_followup_blueprint():
    """Lead nurturing automation workflow."""
    return {
        "name": "Lead Follow-Up Automation",
        "description": "Nurture leads with personalized emails and track engagement",
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "type": "crm",
        "use_case": "Increase conversion rates by automated lead nurturing",
        "implementation_hours": 12,
        "modules": [
            {
                "position": 1,
                "name": "Lead Form Submission",
                "type": "forms",
                "app": "Typeform",
                "description": "Capture new leads from Typeform",
                "config": {
                    "form_id": "{{CLIENT_TYPEFORM_FORM_ID}}",
                    "expected_fields": ["name", "email", "phone", "service_interested", "urgency"]
                },
                "output_mapping": {
                    "lead_name": "{{1.name}}",
                    "lead_email": "{{1.email}}",
                    "lead_phone": "{{1.phone}}",
                    "service": "{{1.service_interested}}",
                    "urgency": "{{1.urgency}}"
                }
            },
            {
                "position": 2,
                "name": "Store Lead in Database",
                "type": "database",
                "app": "Airtable",
                "description": "Create lead record in Airtable",
                "config": {
                    "workspace": "{{CLIENT_AIRTABLE_WORKSPACE}}",
                    "table": "Leads",
                    "fields": {
                        "Name": "{{1.lead_name}}",
                        "Email": "{{1.lead_email}}",
                        "Phone": "{{1.lead_phone}}",
                        "Service Interest": "{{1.service}}",
                        "Urgency": "{{1.urgency}}",
                        "Status": "New Lead",
                        "Submitted": "{{now}}",
                        "Follow-up Scheduled": "false"
                    }
                }
            },
            {
                "position": 3,
                "name": "Generate Personalized Message",
                "type": "ai",
                "app": "OpenAI",
                "description": "Use GPT-4 to personalize follow-up message",
                "config": {
                    "model": "gpt-4",
                    "prompt": "Write a friendly, 75-word follow-up email for {{1.lead_name}} who is interested in {{1.service}}. {{#if:1.urgency='high'}}Emphasize quick response.{{/if}} Start with thanking them for their interest. Include a clear CTA.",
                    "max_tokens": 100,
                    "temperature": 0.7
                }
            },
            {
                "position": 4,
                "name": "Send Personalized Email",
                "type": "messaging",
                "app": "Gmail",
                "description": "Send personalized follow-up via Gmail",
                "config": {
                    "to": "{{1.lead_email}}",
                    "from": "{{CLIENT_GMAIL_ADDRESS}}",
                    "subject": "Hi {{1.lead_name}} - {{1.service}} Solutions We Discussed",
                    "body_template": "{{3.message}}\n\n---\nReady to discuss? Reply to this email or call {{CLIENT_PHONE}}.\n\nBest regards,\n{{CLIENT_NAME}}\n{{CLIENT_TITLE}}",
                    "reply_to": "{{CLIENT_EMAIL}}"
                },
                "error_handling": {
                    "invalid_email": "Log to error table",
                    "gmail_error": "Retry next day"
                }
            },
            {
                "position": 5,
                "name": "Update Lead Status",
                "type": "database",
                "app": "Airtable",
                "description": "Update lead record with follow-up sent",
                "config": {
                    "workspace": "{{CLIENT_AIRTABLE_WORKSPACE}}",
                    "table": "Leads",
                    "action": "update",
                    "record_id": "{{2.record_id}}",
                    "fields": {
                        "Status": "Follow-up Sent",
                        "Follow-up Scheduled": "true",
                        "Follow-up Sent": "{{now}}",
                        "AI Generated": "true"
                    }
                }
            }
        ],
        "connections_required": [
            {
                "type": "typeform",
                "name": "Client Typeform",
                "description": "Client's Typeform account"
            },
            {
                "type": "airtable",
                "name": "Client Airtable",
                "description": "Client's Airtable workspace"
            },
            {
                "type": "openai",
                "name": "Catalyst OpenAI Account",
                "description": "Shared OpenAI account (billed to Catalyst)"
            },
            {
                "type": "gmail",
                "name": "Client Gmail Account",
                "description": "Client's Gmail for sending emails"
            }
        ],
        "testing": {
            "test_data": {
                "name": "Jane Smith",
                "email": "test@example.com",
                "phone": "+15551234567",
                "service_interested": "HVAC Service",
                "urgency": "high"
            },
            "expected_output": "Follow-up email sent, lead record updated"
        },
        "deployment_checklist": [
            "✓ Connect Typeform form",
            "✓ Verify Airtable access",
            "✓ Test OpenAI connection",
            "✓ Create 'Leads' table in Airtable",
            "✓ Configure Gmail for outbound email",
            "✓ Test end-to-end with sample lead",
            "✓ Enable scenario"
        ]
    }


def create_chatbot_blueprint():
    """Customer support chatbot workflow."""
    return {
        "name": "Customer Support Chatbot",
        "description": "AI-powered SMS chatbot for FAQ and customer inquiries",
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "type": "customer_support",
        "use_case": "Answer FAQs 24/7, reduce support overhead",
        "implementation_hours": 15,
        "modules": [
            {
                "position": 1,
                "name": "Receive SMS Message",
                "type": "messaging",
                "app": "Twilio",
                "description": "Listen for incoming SMS messages",
                "config": {
                    "trigger": "incoming_sms",
                    "phone_number": "{{CLIENT_TWILIO_NUMBER}}"
                },
                "output_mapping": {
                    "from_number": "{{1.from_number}}",
                    "message": "{{1.message}}",
                    "timestamp": "{{1.timestamp}}"
                }
            },
            {
                "position": 2,
                "name": "Fetch Knowledge Base",
                "type": "database",
                "app": "Airtable",
                "description": "Get FAQ data for AI context",
                "config": {
                    "workspace": "{{CLIENT_AIRTABLE_WORKSPACE}}",
                    "table": "FAQ",
                    "fields": ["question", "answer", "category", "keywords"],
                    "note": "AI will use these Q&As to answer customer questions"
                }
            },
            {
                "position": 3,
                "name": "Process with AI",
                "type": "ai",
                "app": "OpenAI",
                "description": "Use GPT-4 to process customer inquiry",
                "config": {
                    "model": "gpt-4",
                    "system_prompt": "You are a helpful customer support bot for {{CLIENT_BUSINESS}}. Answer questions using the provided FAQ. If the question is not in the FAQ, politely say you'll transfer to a human and ask for their preferred contact method. Keep responses under 160 characters for SMS.",
                    "user_prompt": "Customer question: {{1.message}}\n\nRelevant FAQs:\n{{2.faq_formatted}}\n\nRespond helpfully and concisely.",
                    "max_tokens": 50,
                    "temperature": 0.5
                }
            },
            {
                "position": 4,
                "name": "Route Message",
                "type": "flow_control",
                "app": "Make",
                "description": "Decide if AI can answer or escalate",
                "config": {
                    "condition": "if response contains 'transfer' or 'human'",
                    "true_path": "Escalate to human support",
                    "false_path": "Send AI response"
                }
            },
            {
                "position": 4.1,
                "name": "Send AI Response",
                "type": "messaging",
                "app": "Twilio",
                "description": "Send chatbot answer (false path)",
                "config": {
                    "to": "{{1.from_number}}",
                    "message": "{{3.response}}\n\nReply HELP for menu or call {{CLIENT_PHONE}} to speak with someone."
                }
            },
            {
                "position": 4.2,
                "name": "Escalate to Support",
                "type": "messaging",
                "app": "Twilio",
                "description": "Escalate complex query (true path)",
                "config": {
                    "to": "{{1.from_number}}",
                    "message": "Thanks for reaching out! A member of our team will reply within 2 hours. Message: {{1.message}}"
                }
            },
            {
                "position": 5,
                "name": "Log Conversation",
                "type": "database",
                "app": "Airtable",
                "description": "Record all conversations for analytics",
                "config": {
                    "workspace": "{{CLIENT_AIRTABLE_WORKSPACE}}",
                    "table": "Chat Logs",
                    "fields": {
                        "Customer Phone": "{{1.from_number}}",
                        "Message": "{{1.message}}",
                        "AI Response": "{{3.response}}",
                        "Escalated": "{{4.escalated}}",
                        "Timestamp": "{{1.timestamp}}"
                    }
                }
            }
        ],
        "connections_required": [
            {
                "type": "twilio",
                "name": "Client Twilio Account",
                "description": "Client's Twilio account"
            },
            {
                "type": "airtable",
                "name": "Client Airtable",
                "description": "Client's Airtable workspace"
            },
            {
                "type": "openai",
                "name": "Catalyst OpenAI Account",
                "description": "Shared OpenAI (billed to Catalyst)"
            }
        ],
        "testing": {
            "test_messages": [
                {"text": "What are your hours?", "expected": "FAQ answer"},
                {"text": "I need emergency service", "expected": "Escalate to human"}
            ]
        },
        "deployment_checklist": [
            "✓ Set up Twilio SMS webhook",
            "✓ Populate 'FAQ' table in Airtable",
            "✓ Configure OpenAI connection",
            "✓ Create 'Chat Logs' table",
            "✓ Test with sample messages",
            "✓ Configure escalation rules",
            "✓ Enable scenario"
        ]
    }


def create_quote_generator_blueprint():
    """Quote/estimate generator workflow."""
    return {
        "name": "Quote Generator & Email",
        "description": "Generate custom quotes and send via email automatically",
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "type": "sales",
        "use_case": "Generate professional quotes instantly, improve closing rate",
        "implementation_hours": 7,
        "modules": [
            {
                "position": 1,
                "name": "Quote Request Form",
                "type": "forms",
                "app": "Typeform",
                "description": "Capture quote request details",
                "config": {
                    "form_id": "{{CLIENT_TYPEFORM_QUOTE_FORM_ID}}",
                    "fields": ["name", "email", "phone", "service", "scope", "urgency"]
                }
            },
            {
                "position": 2,
                "name": "Generate Quote",
                "type": "document",
                "app": "Google Docs",
                "description": "Create quote from template",
                "config": {
                    "template_id": "{{CLIENT_GOOGLE_DOCS_QUOTE_TEMPLATE}}",
                    "replacements": {
                        "{{CUSTOMER_NAME}}": "{{1.name}}",
                        "{{SERVICE}}": "{{1.service}}",
                        "{{SCOPE}}": "{{1.scope}}",
                        "{{DATE}}": "{{now|format:'MMM D, YYYY'}}",
                        "{{VALID_UNTIL}}": "{{now|add:'30 days'|format:'MMM D, YYYY'}}",
                        "{{PRICE}}": "{{calculatePrice(1.service, 1.scope, 1.urgency)}}",
                        "{{TOTAL_WITH_TAX}}": "{{calculatePrice(1.service, 1.scope, 1.urgency) * 1.08}}"
                    }
                }
            },
            {
                "position": 3,
                "name": "Convert to PDF",
                "type": "document",
                "app": "PDFMonkey",
                "description": "Convert Google Doc to PDF",
                "config": {
                    "document_url": "{{2.document_url}}",
                    "format": "pdf",
                    "filename": "Quote_{{1.name}}_{{now|format:'YYYYMMDD'}}.pdf"
                }
            },
            {
                "position": 4,
                "name": "Email Quote",
                "type": "messaging",
                "app": "Gmail",
                "description": "Send quote to customer",
                "config": {
                    "to": "{{1.email}}",
                    "from": "{{CLIENT_GMAIL_ADDRESS}}",
                    "subject": "Your Quote: {{1.service}} - {{1.name}}",
                    "body_template": "Hi {{1.name}},\n\nThank you for your interest in {{1.service}}. I've prepared a custom quote based on your requirements.\n\nQuote Amount: {{2.price}}\nValid Until: {{now|add:'30 days'|format:'MMM D, YYYY'}}\n\nPlease review and let me know if you have any questions. I'm happy to discuss.\n\n{{#if:1.urgency='high'}}Quick note: Given your urgency, I can start immediately if approved.\n{{/if}}\nBest regards,\n{{CLIENT_NAME}}\n{{CLIENT_PHONE}}",
                    "attachments": ["{{3.pdf_url}}"]
                }
            },
            {
                "position": 5,
                "name": "Log Quote in CRM",
                "type": "database",
                "app": "Airtable",
                "description": "Record quote for tracking",
                "config": {
                    "workspace": "{{CLIENT_AIRTABLE_WORKSPACE}}",
                    "table": "Quotes",
                    "fields": {
                        "Customer Name": "{{1.name}}",
                        "Email": "{{1.email}}",
                        "Phone": "{{1.phone}}",
                        "Service": "{{1.service}}",
                        "Scope": "{{1.scope}}",
                        "Amount": "{{2.price}}",
                        "Sent": "{{now}}",
                        "PDF URL": "{{3.pdf_url}}",
                        "Status": "Sent"
                    }
                }
            }
        ],
        "connections_required": [
            {
                "type": "typeform",
                "name": "Client Typeform",
                "description": "Quote request form"
            },
            {
                "type": "google_docs",
                "name": "Client Google Account",
                "description": "Access to Google Drive"
            },
            {
                "type": "pdfmonkey",
                "name": "Catalyst PDFMonkey Account",
                "description": "Shared PDF conversion (billed to Catalyst)"
            },
            {
                "type": "gmail",
                "name": "Client Gmail",
                "description": "Send quotes"
            },
            {
                "type": "airtable",
                "name": "Client Airtable",
                "description": "Track quotes"
            }
        ],
        "testing": {
            "test_data": {
                "name": "Test Customer",
                "email": "test@example.com",
                "phone": "+15551234567",
                "service": "Plumbing",
                "scope": "Full bathroom remodel",
                "urgency": "normal"
            }
        },
        "deployment_checklist": [
            "✓ Create Google Docs quote template",
            "✓ Connect Typeform form",
            "✓ Set up PDFMonkey",
            "✓ Configure Gmail",
            "✓ Create 'Quotes' table in Airtable",
            "✓ Test quote generation",
            "✓ Test PDF creation",
            "✓ Test email delivery",
            "✓ Enable scenario"
        ]
    }


def create_client_intake_blueprint():
    """Client intake form workflow."""
    return {
        "name": "Client Intake Automation",
        "description": "Collect client info via form, organize in database, send confirmation",
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "type": "onboarding",
        "use_case": "Streamline client onboarding, reduce data entry",
        "implementation_hours": 5,
        "modules": [
            {
                "position": 1,
                "name": "Intake Form Submission",
                "type": "forms",
                "app": "Typeform",
                "description": "Collect client information",
                "config": {
                    "form_id": "{{CLIENT_TYPEFORM_INTAKE_FORM_ID}}",
                    "fields": [
                        "full_name", "email", "phone", "company_name",
                        "company_type", "annual_revenue", "number_of_employees",
                        "main_challenge", "project_timeline"
                    ]
                }
            },
            {
                "position": 2,
                "name": "Store Client Data",
                "type": "database",
                "app": "Airtable",
                "description": "Create client record",
                "config": {
                    "workspace": "{{CLIENT_AIRTABLE_WORKSPACE}}",
                    "table": "Clients",
                    "fields": {
                        "Name": "{{1.full_name}}",
                        "Email": "{{1.email}}",
                        "Phone": "{{1.phone}}",
                        "Company": "{{1.company_name}}",
                        "Industry": "{{1.company_type}}",
                        "Annual Revenue": "{{1.annual_revenue}}",
                        "Employees": "{{1.number_of_employees}}",
                        "Main Challenge": "{{1.main_challenge}}",
                        "Project Timeline": "{{1.project_timeline}}",
                        "Status": "Intake Received",
                        "Intake Date": "{{now}}"
                    }
                }
            },
            {
                "position": 3,
                "name": "Send Confirmation Email",
                "type": "messaging",
                "app": "Gmail",
                "description": "Confirm receipt to client",
                "config": {
                    "to": "{{1.email}}",
                    "from": "{{CLIENT_GMAIL_ADDRESS}}",
                    "subject": "Thank you, {{1.full_name}}! We received your intake form",
                    "body_template": "Hi {{1.full_name}},\n\nThank you for filling out our intake form. We've received your information and will review your needs.\n\nCompany: {{1.company_name}}\nMain Challenge: {{1.main_challenge}}\nTimeline: {{1.project_timeline}}\n\nWe'll be in touch within 24 hours to discuss next steps.\n\nBest regards,\n{{CLIENT_NAME}}"
                }
            }
        ],
        "connections_required": [
            {
                "type": "typeform",
                "name": "Client Typeform",
                "description": "Intake form"
            },
            {
                "type": "airtable",
                "name": "Client Airtable",
                "description": "Client database"
            },
            {
                "type": "gmail",
                "name": "Client Gmail",
                "description": "Send confirmations"
            }
        ],
        "deployment_checklist": [
            "✓ Create intake form in Typeform",
            "✓ Create 'Clients' table in Airtable",
            "✓ Configure Gmail",
            "✓ Test form submission",
            "✓ Verify data storage",
            "✓ Test confirmation email",
            "✓ Enable scenario"
        ]
    }


def main():
    """Create all workflow blueprints."""
    blueprints = {
        "sms_reminder": create_sms_reminder_blueprint(),
        "lead_followup": create_lead_followup_blueprint(),
        "chatbot": create_chatbot_blueprint(),
        "quote_generator": create_quote_generator_blueprint(),
        "client_intake": create_client_intake_blueprint(),
    }
    
    # Create workflows directory
    workflows_dir = Path(__file__).parent / "workflows"
    workflows_dir.mkdir(exist_ok=True)
    
    print("\n" + "="*70)
    print("CATALYST: Workflow Blueprint Generator")
    print("="*70 + "\n")
    
    # Save each blueprint
    for name, blueprint in blueprints.items():
        filepath = workflows_dir / f"{name}_blueprint.json"
        with open(filepath, 'w') as f:
            json.dump(blueprint, f, indent=2)
        print(f"✅ Created: {filepath.name}")
        print(f"   Name: {blueprint['name']}")
        print(f"   Modules: {len(blueprint['modules'])}")
        print(f"   Implementation: {blueprint['implementation_hours']}h\n")
    
    # Create index
    index = {
        "title": "Catalyst Workflow Blueprints",
        "created_at": datetime.now().isoformat(),
        "workflows": [
            {
                "id": "sms_reminder",
                "name": "SMS Appointment Reminder",
                "type": "scheduling",
                "modules": 4,
                "implementation_hours": 10,
                "use_case": "Reduce no-shows with automated reminders"
            },
            {
                "id": "lead_followup",
                "name": "Lead Follow-Up Automation",
                "type": "crm",
                "modules": 5,
                "implementation_hours": 12,
                "use_case": "Nurture leads automatically"
            },
            {
                "id": "chatbot",
                "name": "Customer Support Chatbot",
                "type": "customer_support",
                "modules": 6,
                "implementation_hours": 15,
                "use_case": "24/7 customer support"
            },
            {
                "id": "quote_generator",
                "name": "Quote Generator & Email",
                "type": "sales",
                "modules": 5,
                "implementation_hours": 7,
                "use_case": "Generate quotes instantly"
            },
            {
                "id": "client_intake",
                "name": "Client Intake Automation",
                "type": "onboarding",
                "modules": 3,
                "implementation_hours": 5,
                "use_case": "Streamline client onboarding"
            }
        ],
        "total_workflows": len(blueprints),
        "total_implementation_hours": sum(b['implementation_hours'] for b in blueprints.values()),
        "deployment_notes": "Each blueprint includes detailed module configuration, test data, and deployment checklist. Use these as templates for creating Make.com scenarios via the API."
    }
    
    index_path = workflows_dir / "index.json"
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)
    
    print("="*70)
    print(f"✅ Created workflow index: {index_path.name}")
    print(f"   Total workflows: {len(blueprints)}")
    print(f"   Total implementation hours: {sum(b['implementation_hours'] for b in blueprints.values())}h")
    print("="*70 + "\n")
    
    print("📖 Blueprint Details:")
    print("-" * 70)
    for item in index['workflows']:
        print(f"\n{item['name']}")
        print(f"  Type: {item['type']} | Modules: {item['modules']} | Hours: {item['implementation_hours']}h")
        print(f"  Use case: {item['use_case']}")
    
    print("\n" + "="*70)
    print("✅ All blueprints generated successfully!")
    print(f"📁 Location: {workflows_dir}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
