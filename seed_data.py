import json
import os
import sys
from dotenv import load_dotenv

# Ensure UTF-8 output encoding across all operating systems / Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Load environment variables from .env
load_dotenv()

# Import Hindsight SDK (support both package naming conventions)
from hindsight_client import Hindsight

def generate_current_identities_file(filepath: str = "current_identities.json") -> list[dict]:
    """Generates the local current snapshot of non-human AWS identities."""
    identities = [
        {
            "id": "nh-id-001",
            "name": "payment-service-account",
            "type": "IAM Role",
            "account_id": "123456789012",
            "arn": "arn:aws:iam::123456789012:role/payment-service-account",
            "permissions": [
                "Database Read",
                "S3 Write",
                "Admin"
            ],
            "status": "Active",
            "environment": "AWS Production",
            "description": "Service account initially allocated for Payment Migration Project",
            "created_date": "2026-01-15",
            "last_active": "2026-05-18"
        },
        {
            "id": "nh-id-002",
            "name": "email-notification-bot",
            "type": "IAM User / Machine Account",
            "account_id": "123456789012",
            "arn": "arn:aws:iam::123456789012:user/email-notification-bot",
            "permissions": [
                "SES Send"
            ],
            "status": "Active",
            "environment": "AWS Production",
            "description": "Automated system identity for sending transactional notifications",
            "created_date": "2025-11-10",
            "last_active": "2026-09-29"
        },
        {
            "id": "nh-id-003",
            "name": "analytics-service",
            "type": "IAM Role",
            "account_id": "123456789012",
            "arn": "arn:aws:iam::123456789012:role/analytics-service",
            "permissions": [
                "S3 Read"
            ],
            "status": "Active",
            "environment": "AWS Production",
            "description": "Background analytics ETL ingestion service account",
            "created_date": "2025-08-20",
            "last_active": "2026-09-29"
        }
    ]

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(identities, f, indent=2)

    print(f"[+] Generated current identities snapshot at '{filepath}' with {len(identities)} identities.", flush=True)
    return identities


def seed_hindsight_memory(bank_id: str = "identity-memory") -> None:
    """Connects to Hindsight and seeds historical context for the identities."""
    base_url = os.getenv("HINDSIGHT_BASE_URL", os.getenv("HINDSIGHT_API_URL", "http://localhost:8888"))
    api_key = os.getenv("HINDSIGHT_API_KEY", None)
    timeout = float(os.getenv("HINDSIGHT_TIMEOUT", "10.0"))

    print(f"\n[*] Connecting to Hindsight at '{base_url}' (Bank: '{bank_id}')...", flush=True)
    client = Hindsight(base_url=base_url, api_key=api_key, timeout=timeout)

    # Historical timeline and events for non-human identities
    historical_timeline = {
        "payment-service-account": [
            "payment-service-account: Created Jan 2026 for Payment Migration Project with DB Read and S3 Read",
            "payment-service-account: March 2026: Payment Migration Project marked complete",
            "payment-service-account: April 2026: Account mostly dormant",
            "payment-service-account: May 2026: S3 Write and Admin permissions added by unknown user"
        ],
        "email-notification-bot": [
            "email-notification-bot: Created November 2025 for Transactional Email Service with SES Send permission",
            "email-notification-bot: December 2025: Successfully integrated into customer notification microservice",
            "email-notification-bot: February 2026: Routine IAM access key rotation completed with no permission changes",
            "email-notification-bot: August 2026: Regular quarterly permission audit verified least-privilege SES Send compliance"
        ],
        "analytics-service": [
            "analytics-service: Created August 2025 for Business Intelligence Data Lake ingestion with S3 Read permission",
            "analytics-service: October 2025: Nightly ETL pipeline connected to data warehouse",
            "analytics-service: January 2026: Security review approved read-only bucket policy access",
            "analytics-service: July 2026: Annual compliance audit confirmed scoped S3 Read access intact"
        ]
    }

    try:
        # Create bank if it doesn't already exist
        try:
            client.create_bank(
                bank_id=bank_id,
                retain_mission="Extract historical facts, project lifecycles, and permission changes for cloud identities and service accounts."
            )
            print(f"[+] Initialized/verified memory bank '{bank_id}'.", flush=True)
        except Exception as e:
            # Bank might already exist or server auto-provisions on retain
            print(f"[*] Memory bank status check: {e}", flush=True)

        total_stored = 0
        print(f"\n[*] Seeding historical facts into '{bank_id}'...", flush=True)

        for account, facts in historical_timeline.items():
            print(f"\n--- Storing timeline facts for: {account} ---", flush=True)
            for fact in facts:
                client.retain(
                    bank_id=bank_id,
                    content=fact,
                    context=f"Identity audit trail for {account}"
                )
                total_stored += 1
                print(f"  [+] Successfully stored fact: \"{fact}\"", flush=True)

        print(f"\n[+] Finished seeding Hindsight memory bank '{bank_id}'. Total facts stored: {total_stored}", flush=True)

    except Exception as e:
        print(f"\n[!] Note on Hindsight connection: {e}", flush=True)
        print("[!] Ensure the Hindsight API server is running (e.g. at HINDSIGHT_BASE_URL or http://localhost:8888).", flush=True)


def main():
    print("=" * 65, flush=True)
    print(" Identity Hindsight Data Seeder", flush=True)
    print("=" * 65, flush=True)

    # 1. Generate current_identities.json
    generate_current_identities_file("current_identities.json")

    # 2. Seed Hindsight identity-memory bank
    seed_hindsight_memory("identity-memory")

    print("\n" + "=" * 65, flush=True)
    print(" Seeding process completed.", flush=True)
    print("=" * 65, flush=True)


if __name__ == "__main__":
    main()
