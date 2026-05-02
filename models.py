from datetime import datetime, date
from extensions import db


class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    company = db.Column(db.String(200))
    status = db.Column(db.String(20), default="Lead")  # Lead, Customer, Client, VIP, Inactive, Archived
    lead_source = db.Column(db.String(30), default="Other")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    notes = db.relationship("Note", backref="contact", lazy=True, cascade="all, delete-orphan")
    deals = db.relationship("Deal", backref="contact", lazy=True)
    activities = db.relationship("ActivityLog", backref="contact", lazy=True)
    client_notes = db.relationship("ClientNote", backref="contact", lazy=True, cascade="all, delete-orphan")
    purchases = db.relationship("Purchase", backref="contact", lazy=True)

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


# --- NEW MODELS ---

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), default=0)
    product_type = db.Column(db.String(20), default="paid")  # free, paid
    delivery_url = db.Column(db.String(500))
    stripe_price_id = db.Column(db.String(200))
    image_url = db.Column(db.String(500))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    purchases = db.relationship("Purchase", backref="product", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": float(self.price) if self.price else 0,
            "product_type": self.product_type,
            "delivery_url": self.delivery_url,
            "stripe_price_id": self.stripe_price_id,
            "image_url": self.image_url,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Purchase(db.Model):
    __tablename__ = "purchases"

    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    stripe_session_id = db.Column(db.String(300))
    amount = db.Column(db.Numeric(10, 2), default=0)
    status = db.Column(db.String(20), default="completed")  # completed, pending, refunded
    purchased_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "contact_id": self.contact_id,
            "contact_name": self.contact.name if self.contact else None,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "amount": float(self.amount) if self.amount else 0,
            "status": self.status,
            "stripe_session_id": self.stripe_session_id,
            "purchased_at": self.purchased_at.isoformat() if self.purchased_at else None,
        }


class ClientNote(db.Model):
    __tablename__ = "client_notes"

    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "contact_id": self.contact_id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="todo")  # todo, in_progress, done
    priority = db.Column(db.String(10), default="medium")  # low, medium, high
    due_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class EmailTemplate(db.Model):
    __tablename__ = "email_templates"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    body_html = db.Column(db.Text, nullable=False)
    trigger_type = db.Column(db.String(30), nullable=False)  # lead_magnet, purchase_confirmation
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    email_logs = db.relationship("EmailLog", backref="template", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "subject": self.subject,
            "body_html": self.body_html,
            "trigger_type": self.trigger_type,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class EmailLog(db.Model):
    __tablename__ = "email_log"

    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey("email_templates.id", ondelete="SET NULL"), nullable=True)
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)
    to_email = db.Column(db.String(200))
    subject = db.Column(db.String(500))
    status = db.Column(db.String(20), default="mock")  # sent, failed, mock
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    log_contact = db.relationship("Contact", backref="email_logs", lazy=True, foreign_keys=[contact_id])

    def to_dict(self):
        return {
            "id": self.id,
            "template_id": self.template_id,
            "template_name": self.template.name if self.template else None,
            "contact_id": self.contact_id,
            "contact_name": self.log_contact.name if self.log_contact else None,
            "to_email": self.to_email,
            "subject": self.subject,
            "status": self.status,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
        }


class PageView(db.Model):
    __tablename__ = "page_views"

    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(200), nullable=False)
    visitor_id = db.Column(db.String(100))
    referrer = db.Column(db.String(500))
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "page": self.page,
            "visitor_id": self.visitor_id,
            "referrer": self.referrer,
            "contact_id": self.contact_id,
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
