from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from extensions import db
from auth import login_required, check_credentials
from models import Contact, Deal, Note, ActivityLog, PageView, Purchase
from sqlalchemy import func
from datetime import datetime, timedelta

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if check_credentials(username, password):
            session["logged_in"] = True
            session.permanent = True
            next_url = request.args.get("next", url_for("admin.dashboard"))
            return redirect(next_url)
        else:
            flash("Invalid credentials. Please try again.", "danger")

    return render_template("admin/login.html")


@admin_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin.login"))


@admin_bp.route("/dashboard")
@login_required
def dashboard():
    stats = {
        "total_contacts": Contact.query.count(),
        "total_leads": Contact.query.filter(Contact.status == "Lead").count(),
        "pipeline_value": float(db.session.query(func.coalesce(func.sum(Deal.value), 0)).filter(
            Deal.stage.notin_(["Won", "Lost"])
        ).scalar()),
        "total_revenue": float(db.session.query(func.coalesce(func.sum(Deal.value), 0)).filter(
            Deal.stage == "Won"
        ).scalar()),
        "total_deals": Deal.query.count(),
        "won_deals": Deal.query.filter(Deal.stage == "Won").count(),
    }
    recent_activity = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()

    # Analytics funnel (last 30 days)
    funnel = None
    if current_app.config.get("FEATURE_ANALYTICS") == "true":
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        page_views = PageView.query.filter(PageView.created_at >= thirty_days_ago).count()
        signups = Contact.query.filter(Contact.created_at >= thirty_days_ago).count()
        purchases = Purchase.query.filter(Purchase.purchased_at >= thirty_days_ago).count()

        funnel = {
            "page_views": page_views,
            "signups": signups,
            "purchases": purchases,
            "signup_rate": round((signups / page_views * 100), 1) if page_views > 0 else 0,
            "purchase_rate": round((purchases / signups * 100), 1) if signups > 0 else 0,
        }

    return render_template("admin/dashboard.html", stats=stats, recent_activity=recent_activity, funnel=funnel)


@admin_bp.route("/contacts")
@login_required
def contacts():
    q = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()

    query = Contact.query
    if q:
        search = f"%{q}%"
        query = query.filter(
            db.or_(
                Contact.name.ilike(search),
                Contact.email.ilike(search),
                Contact.company.ilike(search),
            )
        )
    if status_filter:
        query = query.filter(Contact.status == status_filter)

    contacts_list = query.order_by(Contact.created_at.desc()).all()
    return render_template("admin/contacts.html", contacts=contacts_list, q=q, status_filter=status_filter)


@admin_bp.route("/contacts/<int:contact_id>")
@login_required
def contact_detail(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    activities = ActivityLog.query.filter_by(contact_id=contact_id).order_by(ActivityLog.created_at.desc()).limit(20).all()
    all_deals = Deal.query.filter_by(contact_id=contact_id).all()

    return render_template("admin/contact_detail.html", contact=contact, activities=activities, deals=all_deals)


@admin_bp.route("/deals")
@login_required
def deals():
    stages = ["New Lead", "Contacted", "Proposal", "Negotiation", "Won", "Lost"]
    deals_by_stage = {}
    stage_values = {}
    for stage in stages:
        stage_deals = Deal.query.filter_by(stage=stage).order_by(Deal.created_at.desc()).all()
        deals_by_stage[stage] = stage_deals
        stage_values[stage] = sum(float(d.value) for d in stage_deals)

    all_contacts = Contact.query.order_by(Contact.name).all()

    return render_template("admin/deals.html", stages=stages, deals_by_stage=deals_by_stage, stage_values=stage_values, contacts=all_contacts)
