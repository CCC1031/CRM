"""Seed the database with demo data for the workshop.
Run: python seed.py
"""
from app import app
from extensions import db
from models import Contact, Deal, Note, ActivityLog
from datetime import datetime, timedelta
import random

def seed():
    with app.app_context():
        # Clear existing data
        ActivityLog.query.delete()
        Note.query.delete()
        Deal.query.delete()
        Contact.query.delete()
        db.session.commit()

        # --- CONTACTS ---
        contacts_data = [
            {"name": "Maria Garcia", "email": "maria.garcia@email.com", "phone": "(555) 234-5678", "company": "Garcia Properties", "status": "Customer", "lead_source": "Referral"},
            {"name": "James Wilson", "email": "james.w@outlook.com", "phone": "(555) 345-6789", "company": "Wilson Financial", "status": "Lead", "lead_source": "Website Form"},
            {"name": "Sarah Chen", "email": "sarah.chen@gmail.com", "phone": "(555) 456-7890", "company": "Chen & Associates", "status": "VIP", "lead_source": "Workshop"},
            {"name": "Michael Brown", "email": "mbrown@brownrealty.com", "phone": "(555) 567-8901", "company": "Brown Realty Group", "status": "Customer", "lead_source": "Referral"},
            {"name": "Jessica Taylor", "email": "jtaylor@email.com", "phone": "(555) 678-9012", "company": "", "status": "Lead", "lead_source": "TikTok"},
            {"name": "Robert Martinez", "email": "rmartinez@gmail.com", "phone": "(555) 789-0123", "company": "Martinez Ventures", "status": "Lead", "lead_source": "Cold Outreach"},
            {"name": "Amanda Johnson", "email": "amanda.j@hotmail.com", "phone": "(555) 890-1234", "company": "Johnson Consulting", "status": "Customer", "lead_source": "Cold Outreach"},
            {"name": "David Kim", "email": "dkim@kimgroup.com", "phone": "(555) 901-2345", "company": "Kim Investment Group", "status": "VIP", "lead_source": "Referral"},
            {"name": "Lisa Patel", "email": "lpatel@email.com", "phone": "(555) 012-3456", "company": "Patel & Partners", "status": "Lead", "lead_source": "Website Form"},
            {"name": "Chris Anderson", "email": "chris.a@gmail.com", "phone": "(555) 123-4567", "company": "", "status": "Lead", "lead_source": "TikTok"},
            {"name": "Nicole Thompson", "email": "nthompson@thompsonlaw.com", "phone": "(555) 234-5679", "company": "Thompson Law Firm", "status": "Customer", "lead_source": "Workshop"},
            {"name": "Daniel Lee", "email": "dlee@email.com", "phone": "(555) 345-6780", "company": "Lee Capital", "status": "Inactive", "lead_source": "Cold Outreach"},
            {"name": "Rachel White", "email": "rwhite@gmail.com", "phone": "(555) 456-7891", "company": "", "status": "Lead", "lead_source": "Website Form"},
            {"name": "Kevin Harris", "email": "kharris@harrisgroup.com", "phone": "(555) 567-8902", "company": "Harris Group LLC", "status": "Lead", "lead_source": "Cold Outreach"},
            {"name": "Sophia Rivera", "email": "srivera@email.com", "phone": "(555) 678-9013", "company": "Rivera Homes", "status": "Customer", "lead_source": "Referral"},
        ]

        contacts = []
        for i, c in enumerate(contacts_data):
            contact = Contact(**c, created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90)))
            db.session.add(contact)
            contacts.append(contact)
        db.session.flush()

        # --- DEALS ---
        deals_data = [
            {"title": "Garcia Properties - Home Purchase", "contact": 0, "value": 450000, "stage": "Won"},
            {"title": "Wilson Financial - Refinance", "contact": 1, "value": 325000, "stage": "New Lead"},
            {"title": "Chen & Associates - Commercial Loan", "contact": 2, "value": 1200000, "stage": "Negotiation"},
            {"title": "Brown Realty - Investment Property", "contact": 3, "value": 675000, "stage": "Proposal"},
            {"title": "Taylor - First-Time Buyer", "contact": 4, "value": 285000, "stage": "Contacted"},
            {"title": "Martinez Ventures - Portfolio Loan", "contact": 5, "value": 2500000, "stage": "New Lead"},
            {"title": "Kim Investment - Multi-Unit Purchase", "contact": 7, "value": 3400000, "stage": "Won"},
            {"title": "Patel & Partners - Office Mortgage", "contact": 8, "value": 890000, "stage": "Lost"},
        ]

        deals = []
        for d in deals_data:
            deal = Deal(
                title=d["title"], contact_id=contacts[d["contact"]].id,
                value=d["value"], stage=d["stage"],
                expected_close_date=datetime.utcnow().date() + timedelta(days=random.randint(7, 90)),
                won_lost_reason="Client found better rate elsewhere" if d["stage"] == "Lost" else None,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
            )
            db.session.add(deal)
            deals.append(deal)
        db.session.flush()

        # --- NOTES (20+) ---
        notes_data = [
            (0, "Initial consultation went well. Maria is looking to purchase a 3-bedroom home in the suburbs. Budget around $450K."),
            (0, "Pre-approval completed. Maria qualified for $475K. Sending property listings tomorrow."),
            (0, "Closed! Maria purchased the property at 123 Oak Street. Great referral potential."),
            (1, "James called about refinancing his current home. Currently at 6.5% - could save him $400/month."),
            (1, "Sent refinance comparison sheet. James is reviewing with his wife."),
            (2, "Sarah needs a commercial loan for her new office space. Looking at $1.2M. She's been a great client — treating this as VIP."),
            (2, "Sent term sheet. Sarah is reviewing with her business partner. Follow up Friday."),
            (3, "Michael referred by Maria Garcia. Looking for an investment property — rental income focused."),
            (3, "Showed Michael 3 properties. He's interested in the duplex on Elm Street."),
            (3, "Michael submitted offer on duplex. Waiting for seller response."),
            (4, "Jessica found us on TikTok. First-time buyer, needs education on the process. Scheduled intro call."),
            (5, "Cold outreach via LinkedIn. Robert has a portfolio of 5 properties, looking to add more."),
            (5, "Robert interested in portfolio loan. Scheduling a detailed consultation next week."),
            (7, "David is a high-net-worth client. Looking at multi-unit investment. Needs specialized lending."),
            (7, "Met with David's financial advisor. They want to structure this as an LLC purchase."),
            (7, "David approved! Closing on a 12-unit apartment complex. Huge deal."),
            (8, "Lisa needs office space mortgage for her accounting firm. Straightforward deal."),
            (8, "Lisa's application submitted. Awaiting underwriting."),
            (10, "Nicole referred by Sarah Chen. Looking at buying her first commercial property for her law firm."),
            (11, "Daniel went cold after initial call. Sent 2 follow-ups, no response. Moving to inactive."),
            (14, "Sophia closed on her new home! She's already referring friends."),
            (14, "Sophia sent over two referrals — following up with both this week."),
        ]

        for contact_idx, content in notes_data:
            note = Note(contact_id=contacts[contact_idx].id, content=content, created_at=datetime.utcnow() - timedelta(days=random.randint(1, 45)))
            db.session.add(note)

        # --- ACTIVITY LOG (30+) ---
        activities = [
            ("contact_created", "Created contact: Maria Garcia", 0, None),
            ("contact_created", "Created contact: James Wilson", 1, None),
            ("contact_created", "Created contact: Sarah Chen", 2, None),
            ("contact_created", "Created contact: Michael Brown", 3, None),
            ("contact_created", "Created contact: Jessica Taylor", 4, None),
            ("contact_created", "Created contact: Robert Martinez", 5, None),
            ("contact_created", "Created contact: Amanda Johnson", 6, None),
            ("contact_created", "Created contact: David Kim", 7, None),
            ("deal_created", "Created deal: Garcia Properties - Home Purchase", 0, 0),
            ("deal_created", "Created deal: Wilson Financial - Refinance", 1, 1),
            ("deal_created", "Created deal: Chen & Associates - Commercial Loan", 2, 2),
            ("deal_created", "Created deal: Brown Realty - Investment Property", 3, 3),
            ("deal_created", "Created deal: Taylor - First-Time Buyer", 4, 4),
            ("deal_created", "Created deal: Martinez Ventures - Portfolio Loan", 5, 5),
            ("deal_created", "Created deal: Kim Investment - Multi-Unit Purchase", 7, 6),
            ("deal_created", "Created deal: Patel & Partners - Office Mortgage", 8, 7),
            ("deal_moved", "Moved 'Garcia Properties' from Proposal to Won", 0, 0),
            ("deal_moved", "Moved 'Chen & Associates' from Proposal to Negotiation", 2, 2),
            ("deal_moved", "Moved 'Brown Realty' from Contacted to Proposal", 3, 3),
            ("deal_moved", "Moved 'Taylor' from New Lead to Contacted", 4, 4),
            ("deal_moved", "Moved 'Kim Investment' from Negotiation to Won", 7, 6),
            ("deal_moved", "Moved 'Patel & Partners' from Proposal to Lost", 8, 7),
            ("note_added", "Added note to Maria Garcia", 0, None),
            ("note_added", "Added note to James Wilson", 1, None),
            ("note_added", "Added note to Sarah Chen", 2, None),
            ("note_added", "Added note to Michael Brown", 3, None),
            ("note_added", "Added note to David Kim", 7, None),
            ("note_added", "Added note to Sophia Rivera", 14, None),
            ("contact_updated", "Updated Daniel Lee status to Inactive", 11, None),
            ("contact_updated", "Updated Sarah Chen status to VIP", 2, None),
            ("contact_updated", "Updated Amanda Johnson status to Customer", 6, None),
            ("contact_created", "New lead from landing page: Lisa Patel", 8, None),
        ]

        for action_type, desc, contact_idx, deal_idx in activities:
            activity = ActivityLog(
                action_type=action_type, description=desc,
                contact_id=contacts[contact_idx].id,
                deal_id=deals[deal_idx].id if deal_idx is not None else None,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30), hours=random.randint(0, 23)),
            )
            db.session.add(activity)

        db.session.commit()
        print(f"Seeded {len(contacts)} contacts, {len(deals)} deals, {len(notes_data)} notes, {len(activities)} activities")


if __name__ == "__main__":
    seed()
