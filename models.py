from datetime import datetime, date
from extensions import db


class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    company = db.Column(db.String(200))
    status = db.Column(db.String(20), default="Lead")
    lead_source = db.Column(db.String(30), default="Other")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    notes = db.relationship("Note", backref="contact", lazy=True, cascade="all, delete-orphan")
    deals = db.relationship("Deal", backref="contact", lazy=True)
    activities = db.relationship("ActivityLog", backref="contact", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "company": self.company,
            "status": self.status,
            "lead_source": self.lead_source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Deal(db.Model):
    __tablename__ = "deals"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)
    value = db.Column(db.Numeric(12, 2), default=0)
    stage = db.Column(db.String(30), default="New Lead")
    expected_close_date = db.Column(db.Date, nullable=True)
    won_lost_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    activities = db.relationship("ActivityLog", backref="deal", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "contact_id": self.contact_id,
            "contact_name": self.contact.name if self.contact else None,
            "value": float(self.value) if self.value else 0,
            "stage": self.stage,
            "expected_close_date": self.expected_close_date.isoformat() if self.expected_close_date else None,
            "won_lost_reason": self.won_lost_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "contact_id": self.contact_id,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ActivityLog(db.Model):
    __tablename__ = "activity_log"

    id = db.Column(db.Integer, primary_key=True)
    action_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)
    deal_id = db.Column(db.Integer, db.ForeignKey("deals.id", ondelete="SET NULL"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "action_type": self.action_type,
            "description": self.description,
            "contact_id": self.contact_id,
            "deal_id": self.deal_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


def log_activity(action_type, description, contact_id=None, deal_id=None):
    """Helper to log an activity. Call BEFORE db.session.commit() — does NOT commit itself."""
    activity = ActivityLog(
        action_type=action_type,
        description=description,
        contact_id=contact_id,
        deal_id=deal_id,
    )
    db.session.add(activity)
    return activity
