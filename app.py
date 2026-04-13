"""
Digital Marketing Agency CRM — Flask Backend
"""

from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import json, os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///crm.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ─────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────

class Lead(db.Model):
    __tablename__ = "leads"
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(120))
    source        = db.Column(db.String(60))          # "gmail" | "whatsapp" | "manual"
    gmail_thread  = db.Column(db.String(120))
    status        = db.Column(db.String(40), default="New")  # New/Qualified/Closed
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    __tablename__ = "projects"
    id            = db.Column(db.Integer, primary_key=True)
    client_name   = db.Column(db.String(120), nullable=False)
    project_name  = db.Column(db.String(120))
    status        = db.Column(db.String(40), default="Pending")  # Active/Pending/Completed
    assigned_to   = db.Column(db.String(120))
    budget        = db.Column(db.Float, default=0)
    start_date    = db.Column(db.String(20))
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

class Employee(db.Model):
    __tablename__ = "employees"
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    role          = db.Column(db.String(80))
    hourly_rate   = db.Column(db.Float, default=0)
    current_load  = db.Column(db.Integer, default=0)   # % capacity 0-100
    email         = db.Column(db.String(120))
    avatar        = db.Column(db.String(10), default="👤")

class Finance(db.Model):
    __tablename__ = "finances"
    id            = db.Column(db.Integer, primary_key=True)
    client_id     = db.Column(db.Integer)
    client_name   = db.Column(db.String(120))
    type          = db.Column(db.String(40))   # "revenue" | "ad_spend" | "payroll" | "tool"
    amount        = db.Column(db.Float, nullable=False)
    description   = db.Column(db.String(200))
    date          = db.Column(db.String(20))
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    __tablename__ = "messages"
    id            = db.Column(db.Integer, primary_key=True)
    source        = db.Column(db.String(20))   # "gmail" | "whatsapp"
    sender        = db.Column(db.String(120))
    preview       = db.Column(db.String(200))
    full_body     = db.Column(db.Text)
    is_read       = db.Column(db.Boolean, default=False)
    timestamp     = db.Column(db.String(40))
    thread_id     = db.Column(db.String(120))

class Settings(db.Model):
    __tablename__ = "settings"
    key           = db.Column(db.String(80), primary_key=True)
    value         = db.Column(db.String(200))

# ─────────────────────────────────────────────
# SEED HELPERS
# ─────────────────────────────────────────────

def seed_data():
    if Lead.query.first():
        return

    # Leads
    leads = [
        Lead(name="Stella Romero",    email="stella@romero.co",  source="gmail",     status="Qualified", gmail_thread="thread_001"),
        Lead(name="Marcus Webb",      email="m.webb@brand.io",   source="whatsapp",  status="New"),
        Lead(name="Priya Nair",       email="priya@nair.in",     source="manual",    status="Closed"),
        Lead(name="Derek Huang",      email="dhuang@techflow.sg",source="gmail",     status="New",       gmail_thread="thread_002"),
        Lead(name="Lena Novak",       email="lena@novak.eu",     source="whatsapp",  status="Qualified"),
    ]
    db.session.add_all(leads)

    # Projects
    projects = [
        Project(client_name="Romero Co",    project_name="Q3 Social Campaign",  status="Active",    assigned_to="Jamie Chen",   budget=12000, start_date="2026-01-15"),
        Project(client_name="BrandIO",      project_name="SEO Overhaul",        status="Active",    assigned_to="Sara Malik",   budget=8500,  start_date="2026-02-01"),
        Project(client_name="TechFlow SG",  project_name="PPC Launch",          status="Pending",   assigned_to="Leo Park",     budget=5000,  start_date="2026-04-20"),
        Project(client_name="Nair Digital", project_name="Email Funnel Build",   status="Completed", assigned_to="Jamie Chen",   budget=3200,  start_date="2026-01-01"),
        Project(client_name="Novak EU",     project_name="Influencer Outreach", status="Active",    assigned_to="Sara Malik",   budget=9800,  start_date="2026-03-10"),
    ]
    db.session.add_all(projects)

    # Employees
    employees = [
        Employee(name="Jamie Chen",   role="Campaign Manager",    hourly_rate=85,  current_load=78,  email="jamie@agency.com",  avatar="👩‍💼"),
        Employee(name="Sara Malik",   role="SEO Strategist",      hourly_rate=75,  current_load=92,  email="sara@agency.com",   avatar="👩‍💻"),
        Employee(name="Leo Park",     role="Paid Media Specialist",hourly_rate=80, current_load=45,  email="leo@agency.com",    avatar="👨‍💼"),
        Employee(name="Dana Torres",  role="Creative Director",   hourly_rate=95,  current_load=60,  email="dana@agency.com",   avatar="🎨"),
        Employee(name="Kai Williams", role="Analytics Lead",      hourly_rate=90,  current_load=55,  email="kai@agency.com",    avatar="📊"),
    ]
    db.session.add_all(employees)

    # Finances
    finances = [
        Finance(client_name="Romero Co",    type="revenue",   amount=12000, description="Monthly retainer",      date="2026-04-01"),
        Finance(client_name="BrandIO",      type="revenue",   amount=8500,  description="SEO project payment",   date="2026-04-05"),
        Finance(client_name="Novak EU",     type="revenue",   amount=4900,  description="50% upfront retainer",  date="2026-04-07"),
        Finance(client_name="Romero Co",    type="ad_spend",  amount=3200,  description="Meta Ads Q2",           date="2026-04-02"),
        Finance(client_name="BrandIO",      type="ad_spend",  amount=1800,  description="Google Ads budget",     date="2026-04-05"),
        Finance(client_name="",             type="payroll",   amount=7600,  description="April payroll run",     date="2026-04-10"),
        Finance(client_name="",             type="tool",      amount=420,   description="SaaS tools (HubSpot, Ahrefs)", date="2026-04-01"),
        Finance(client_name="TechFlow SG",  type="revenue",   amount=2500,  description="Kickoff deposit",      date="2026-04-12"),
    ]
    db.session.add_all(finances)

    # Messages
    messages = [
        Message(source="gmail",     sender="stella@romero.co",   preview="Can we schedule the Q3 review call?",     full_body="Hi team, hope you're well! I'd love to lock in our Q3 review. How does Thursday at 3pm work?",              is_read=False, timestamp="10:42 AM", thread_id="thread_001"),
        Message(source="whatsapp",  sender="Marcus Webb",        preview="Just saw the report — numbers look 🔥",   full_body="Just saw the May report you sent. Numbers look great! The CTR jumped 18% MoM. Really happy.",              is_read=False, timestamp="9:15 AM",  thread_id="wa_001"),
        Message(source="gmail",     sender="dhuang@techflow.sg", preview="Invoice query — see attached",            full_body="Hi, I had a question about invoice #INV-204. There seems to be a discrepancy in the ad spend line item.", is_read=True,  timestamp="Yesterday", thread_id="thread_002"),
        Message(source="whatsapp",  sender="Lena Novak",         preview="Love the new creatives! Can we tweak…",   full_body="Love the new creatives you shared! One small ask — can we swap the CTA copy to 'Explore Now' instead?",    is_read=True,  timestamp="Yesterday", thread_id="wa_002"),
        Message(source="gmail",     sender="partnerships@meta.com",preview="Your agency tier has been upgraded",    full_body="Congratulations! Based on your managed spend, your agency has been upgraded to Meta Business Partner tier.", is_read=False, timestamp="Mon",       thread_id="thread_003"),
    ]
    db.session.add_all(messages)

    # Settings
    settings = [
        Settings(key="whatsapp_sync", value="true"),
        Settings(key="gmail_sync",    value="true"),
        Settings(key="sync_interval", value="5"),
        Settings(key="agency_name",   value="Apex Digital Agency"),
    ]
    db.session.add_all(settings)

    db.session.commit()

# ─────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

# ─────────────────────────────────────────────
# API: DASHBOARD
# ─────────────────────────────────────────────

@app.route("/api/dashboard")
def api_dashboard():
    total_revenue = db.session.query(db.func.sum(Finance.amount)).filter_by(type="revenue").scalar() or 0
    total_costs   = db.session.query(db.func.sum(Finance.amount)).filter(Finance.type != "revenue").scalar() or 0
    active_proj   = Project.query.filter_by(status="Active").count()
    open_leads    = Lead.query.filter(Lead.status != "Closed").count()
    unread_msgs   = Message.query.filter_by(is_read=False).count()

    return jsonify({
        "total_revenue": total_revenue,
        "total_costs":   total_costs,
        "net_profit":    total_revenue - total_costs,
        "active_projects": active_proj,
        "open_leads":    open_leads,
        "unread_messages": unread_msgs,
    })

# ─────────────────────────────────────────────
# API: LEADS
# ─────────────────────────────────────────────

@app.route("/api/leads", methods=["GET"])
def get_leads():
    leads = Lead.query.order_by(Lead.created_at.desc()).all()
    return jsonify([{
        "id": l.id, "name": l.name, "email": l.email,
        "source": l.source, "status": l.status,
        "gmail_thread": l.gmail_thread,
        "created_at": l.created_at.strftime("%Y-%m-%d"),
    } for l in leads])

@app.route("/api/leads", methods=["POST"])
def create_lead():
    d = request.json
    lead = Lead(
        name=d.get("name", ""),
        email=d.get("email", ""),
        source=d.get("source", "manual"),
        status=d.get("status", "New"),
        gmail_thread=d.get("gmail_thread", ""),
    )
    db.session.add(lead)
    db.session.commit()
    return jsonify({"id": lead.id, "message": "Lead created"}), 201

@app.route("/api/leads/<int:lid>", methods=["PUT"])
def update_lead(lid):
    lead = Lead.query.get_or_404(lid)
    d = request.json
    for field in ["name","email","source","status","gmail_thread"]:
        if field in d:
            setattr(lead, field, d[field])
    db.session.commit()
    return jsonify({"message": "Updated"})

@app.route("/api/leads/<int:lid>", methods=["DELETE"])
def delete_lead(lid):
    lead = Lead.query.get_or_404(lid)
    db.session.delete(lead)
    db.session.commit()
    return jsonify({"message": "Deleted"})

# ─────────────────────────────────────────────
# API: PROJECTS
# ─────────────────────────────────────────────

@app.route("/api/projects", methods=["GET"])
def get_projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return jsonify([{
        "id": p.id, "client_name": p.client_name, "project_name": p.project_name,
        "status": p.status, "assigned_to": p.assigned_to,
        "budget": p.budget, "start_date": p.start_date,
    } for p in projects])

@app.route("/api/projects", methods=["POST"])
def create_project():
    d = request.json
    proj = Project(
        client_name=d.get("client_name",""),
        project_name=d.get("project_name",""),
        status=d.get("status","Pending"),
        assigned_to=d.get("assigned_to",""),
        budget=d.get("budget",0),
        start_date=d.get("start_date",""),
    )
    db.session.add(proj)
    db.session.commit()
    return jsonify({"id": proj.id, "message": "Project created"}), 201

# ─────────────────────────────────────────────
# API: EMPLOYEES
# ─────────────────────────────────────────────

@app.route("/api/employees", methods=["GET"])
def get_employees():
    emps = Employee.query.all()
    return jsonify([{
        "id": e.id, "name": e.name, "role": e.role,
        "hourly_rate": e.hourly_rate, "current_load": e.current_load,
        "email": e.email, "avatar": e.avatar,
    } for e in emps])

@app.route("/api/employees", methods=["POST"])
def create_employee():
    d = request.json
    emp = Employee(
        name=d.get("name",""),
        role=d.get("role",""),
        hourly_rate=d.get("hourly_rate",0),
        current_load=d.get("current_load",0),
        email=d.get("email",""),
        avatar=d.get("avatar","👤"),
    )
    db.session.add(emp)
    db.session.commit()
    return jsonify({"id": emp.id, "message": "Employee created"}), 201

@app.route("/api/employees/<int:eid>", methods=["PUT"])
def update_employee(eid):
    emp = Employee.query.get_or_404(eid)
    d = request.json
    for field in ["name","role","hourly_rate","current_load","email"]:
        if field in d:
            setattr(emp, field, d[field])
    db.session.commit()
    return jsonify({"message": "Updated"})

# ─────────────────────────────────────────────
# API: FINANCES
# ─────────────────────────────────────────────

@app.route("/api/finances", methods=["GET"])
def get_finances():
    finances = Finance.query.order_by(Finance.created_at.desc()).all()
    total_revenue = db.session.query(db.func.sum(Finance.amount)).filter_by(type="revenue").scalar() or 0
    total_costs   = db.session.query(db.func.sum(Finance.amount)).filter(Finance.type != "revenue").scalar() or 0
    return jsonify({
        "summary": {
            "total_revenue": total_revenue,
            "total_costs": total_costs,
            "net_profit": total_revenue - total_costs,
            "margin_pct": round((total_revenue - total_costs) / total_revenue * 100, 1) if total_revenue else 0,
        },
        "records": [{
            "id": f.id, "client_name": f.client_name, "type": f.type,
            "amount": f.amount, "description": f.description, "date": f.date,
        } for f in finances],
    })

@app.route("/api/finances", methods=["POST"])
def create_finance():
    d = request.json
    fin = Finance(
        client_name=d.get("client_name",""),
        type=d.get("type","revenue"),
        amount=d.get("amount",0),
        description=d.get("description",""),
        date=d.get("date", date.today().isoformat()),
    )
    db.session.add(fin)
    db.session.commit()
    return jsonify({"id": fin.id, "message": "Finance record created"}), 201

@app.route("/api/finances/<int:fid>", methods=["DELETE"])
def delete_finance(fid):
    fin = Finance.query.get_or_404(fid)
    db.session.delete(fin)
    db.session.commit()
    return jsonify({"message": "Deleted"})

# ─────────────────────────────────────────────
# API: MESSAGES (Communication Hub)
# ─────────────────────────────────────────────

@app.route("/api/messages", methods=["GET"])
def get_messages():
    source = request.args.get("source")
    q = Message.query
    if source:
        q = q.filter_by(source=source)
    msgs = q.order_by(Message.id.desc()).all()
    return jsonify([{
        "id": m.id, "source": m.source, "sender": m.sender,
        "preview": m.preview, "full_body": m.full_body,
        "is_read": m.is_read, "timestamp": m.timestamp,
        "thread_id": m.thread_id,
    } for m in msgs])

@app.route("/api/messages/<int:mid>/read", methods=["PUT"])
def mark_read(mid):
    msg = Message.query.get_or_404(mid)
    msg.is_read = True
    db.session.commit()
    return jsonify({"message": "Marked read"})

# ─────────────────────────────────────────────
# API: SETTINGS
# ─────────────────────────────────────────────

@app.route("/api/settings", methods=["GET"])
def get_settings():
    rows = Settings.query.all()
    return jsonify({r.key: r.value for r in rows})

@app.route("/api/settings", methods=["POST"])
def update_settings():
    d = request.json
    for key, val in d.items():
        row = Settings.query.get(key)
        if row:
            row.value = str(val)
        else:
            db.session.add(Settings(key=key, value=str(val)))
    db.session.commit()
    return jsonify({"message": "Settings saved"})

# ─────────────────────────────────────────────
# API: DYNAMIC FIELDS CONFIG
# ─────────────────────────────────────────────

@app.route("/api/fields.json", methods=["GET"])
def fields_config():
    path = os.path.join(app.root_path, "data", "fields.json")
    with open(path) as f:
        return jsonify(json.load(f))

@app.route("/api/fields.json", methods=["POST"])
def save_fields_config():
    path = os.path.join(app.root_path, "data", "fields.json")
    with open(path, "w") as f:
        json.dump(request.json, f, indent=2)
    return jsonify({"message": "Fields config saved"})

# ─────────────────────────────────────────────
# SYNC SIMULATION ENDPOINT
# ─────────────────────────────────────────────

@app.route("/api/sync/<source>", methods=["POST"])
def sync_source(source):
    """Simulates a sync from Gmail or WhatsApp."""
    settings = {r.key: r.value for r in Settings.query.all()}
    key = f"{source}_sync"
    if settings.get(key) != "true":
        return jsonify({"message": f"{source} sync is disabled"}), 400
    # In production: call Google/Twilio APIs here
    return jsonify({"message": f"{source} sync triggered", "new_messages": 0})

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True, port=5000)
