# Copyright (c) 2026, IRSAA Business Solution (AlphaX) and contributors
"""Respondent registration and passwordless sign-in (email code) for the GRC Maturity portal.

Security notes
* Codes are 6 digits, stored only as a salted SHA-256 hash, expire (default 10 min) and lock after N wrong tries.
* Sign-in by code is limited to Website Users holding the GRC Maturity Respondent role. Staff (System Users)
  are refused and must use /login, so this path can never bypass desk passwords or two-factor authentication.
* Every endpoint is rate limited per IP.
"""

import hashlib
import re
import secrets

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import add_to_date, get_datetime, now_datetime

DT = "GRC Maturity Registration"
ROLE = "GRC Maturity Respondent"
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _settings():
	return frappe.get_cached_doc("GRC Maturity Settings")


def _hash(email, code):
	from frappe.utils.password import get_encryption_key

	return hashlib.sha256(f"{get_encryption_key()}|{email}|{code}".encode()).hexdigest()


def _clean_email(email):
	email = (email or "").strip().lower()
	if not EMAIL_RE.match(email):
		frappe.throw(_("Enter a valid work email."))
	s = _settings()
	if s.block_free_email:
		blocked = {d.strip().lower() for d in re.split(r"[,\s]+", s.blocked_email_domains or "") if d.strip()}
		if email.split("@", 1)[1] in blocked:
			frappe.throw(_("Use your work email address. Personal email domains are not accepted."))
	return email


def _staff(email):
	return frappe.db.get_value("User", email, "user_type") == "System User"


def _send_code(reg):
	s = _settings()
	if reg.otp_sent_on:
		wait = (s.otp_resend_seconds or 60) - (now_datetime() - get_datetime(reg.otp_sent_on)).total_seconds()
		if wait > 0:
			frappe.throw(_("Please wait {0} seconds before requesting another code.").format(int(wait) + 1))
	code = f"{secrets.randbelow(1000000):06d}"
	reg.otp_hash = _hash(reg.email, code)
	reg.otp_expires = add_to_date(now_datetime(), minutes=s.otp_expiry_minutes or 10)
	reg.otp_attempts = 0
	reg.otp_sent_on = now_datetime()
	reg.flags.ignore_permissions = True
	reg.save()
	brand = frappe.get_cached_doc("GRC Maturity Brand", reg.brand) if reg.brand else None
	sender = frappe.db.get_value("Email Account", brand.email_account, "email_id") if brand and brand.email_account else None
	frappe.sendmail(
		recipients=[reg.email], sender=sender,
		subject=_("Your verification code: {0}").format(code) if reg.language != "ar" else f"رمز التحقق: {code}",
		template="grc_maturity_otp",
		args={"code": code, "reg": reg, "brand": brand, "minutes": s.otp_expiry_minutes or 10, "lang": reg.language or "en"},
		reference_doctype=DT, reference_name=reg.name, now=True,
	)


def _check_code(reg, code):
	s = _settings()
	code = re.sub(r"\D", "", str(code or ""))
	if not reg.otp_hash or not reg.otp_expires or get_datetime(reg.otp_expires) < now_datetime():
		frappe.throw(_("The code has expired. Request a new one."))
	if (reg.otp_attempts or 0) >= (s.otp_max_attempts or 5):
		frappe.throw(_("Too many wrong codes. Request a new one."))
	if not secrets.compare_digest(_hash(reg.email, code), reg.otp_hash):
		frappe.db.set_value(DT, reg.name, "otp_attempts", (reg.otp_attempts or 0) + 1, update_modified=False)
		frappe.db.commit()
		frappe.throw(_("That code is not correct."))
	reg.otp_hash = None
	reg.otp_expires = None
	reg.otp_attempts = 0


def _ensure_user(reg, enabled):
	email = reg.email
	if frappe.db.exists("User", email):
		user = frappe.get_doc("User", email)
		if user.user_type == "System User":
			frappe.throw(_("This email belongs to a staff account. Sign in at /login instead."))
	else:
		first, _sp, last = (reg.contact_name or email).partition(" ")
		user = frappe.get_doc({
			"doctype": "User", "email": email, "first_name": first, "last_name": last or None,
			"user_type": "Website User", "send_welcome_email": 0, "language": reg.language or "en",
			"mobile_no": reg.mobile or None,
		})
		user.flags.ignore_permissions = True
		user.flags.no_welcome_mail = True
		user.insert()
	if ROLE not in [r.role for r in user.roles]:
		user.append("roles", {"role": ROLE})
	user.enabled = 1 if enabled else 0
	user.flags.ignore_permissions = True
	user.save()
	reg.user = user.name
	return user.name


def _login(reg):
	frappe.local.login_manager.login_as(reg.user)
	frappe.db.set_value(DT, reg.name, "last_login", now_datetime(), update_modified=False)


def _redirect(target, brand):
	target = target if target and target.startswith("/") and not target.startswith("//") else None
	slug = frappe.db.get_value("GRC Maturity Brand", brand, "route_slug") if brand else None
	return target or ("/grc-assessment" + (f"?b={slug}" if slug else ""))


# ---------------------------------------------------------------- endpoints
@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=10, seconds=3600)
def register(data):
	"""Create or refresh a registration and email a verification code."""
	import json

	d = json.loads(data) if isinstance(data, str) else data
	s = _settings()
	email = _clean_email(d.get("email"))
	if _staff(email):
		frappe.throw(_("This email belongs to a staff account. Sign in at /login instead."))
	for field, msg in (("organization_name", _("Enter the organization name.")), ("contact_name", _("Enter your name.")),
			("industry_type", _("Select the industry type.")), ("industry_sector", _("Select the industry sector.")),
			("company_nationality", _("Select the company nationality."))):
		if not (d.get(field) or "").strip():
			frappe.throw(msg)
	if s.registration_require_mobile and not (d.get("mobile") or "").strip():
		frappe.throw(_("Enter your mobile number."))
	cr = re.sub(r"\D", "", d.get("cr_number") or "")
	if cr and len(cr) != 10 or (s.registration_require_cr and not cr):
		frappe.throw(_("The CR number must be 10 digits."))
	if not d.get("consent"):
		frappe.throw(_("Please accept the consent statement to continue."))
	sector = frappe.db.get_value("GRC Maturity Industry Sector", d.get("industry_sector"), ["industry_type", "is_other"], as_dict=True)
	if not sector or sector.industry_type != d.get("industry_type"):
		frappe.throw(_("Select the industry sector."))
	if sector.is_other and not (d.get("sector_other") or "").strip():
		frappe.throw(_("Name the sector."))

	from alphax_grc_maturity.engine.branding import get_brand

	name = frappe.db.get_value(DT, {"email": email})
	reg = frappe.get_doc(DT, name) if name else frappe.new_doc(DT)
	if name and reg.status in ("Active", "Pending Approval") and reg.email_verified:
		return {"state": "exists", "message": _("This email is already registered. Use Sign in.")}
	if name and reg.status in ("Rejected", "Disabled"):
		frappe.throw(_("This registration cannot be used. Contact {0}.").format(get_brand(reg.brand).support_email or ""))
	reg.update({
		"organization_name": d.get("organization_name").strip(), "contact_name": d.get("contact_name").strip(),
		"job_title": d.get("job_title"), "email": email, "mobile": d.get("mobile"),
		"industry_type": d.get("industry_type"), "industry_sector": d.get("industry_sector"),
		"sector_other": d.get("sector_other") if sector.is_other else None,
		"company_nationality": d.get("company_nationality"), "cr_number": cr or None, "city": d.get("city"),
		"language": d.get("language") if d.get("language") in ("en", "ar") else "en",
		"brand": get_brand(d.get("brand")).name, "consent_given": 1, "consent_on": now_datetime(),
		"source_ip": getattr(frappe.local, "request_ip", None), "status": "Pending Verification",
	})
	reg.flags.ignore_permissions = True
	reg.save()
	_send_code(reg)
	frappe.db.commit()
	return {"state": "code_sent", "email": email}


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=10, seconds=3600)
def request_code(email):
	"""Sign-in: email a code to an existing registration. Same answer whether or not the email exists."""
	email = (email or "").strip().lower()
	if not EMAIL_RE.match(email):
		frappe.throw(_("Enter a valid work email."))
	if _staff(email):
		frappe.throw(_("This email belongs to a staff account. Sign in at /login instead."))
	name = frappe.db.get_value(DT, {"email": email})
	if name:
		reg = frappe.get_doc(DT, name)
		if reg.status not in ("Rejected", "Disabled"):
			_send_code(reg)
			frappe.db.commit()
	return {"state": "code_sent", "email": email}


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=30, seconds=3600)
def verify(email, code, redirect_to=None):
	email = (email or "").strip().lower()
	name = frappe.db.get_value(DT, {"email": email})
	if not name:
		frappe.throw(_("That code is not correct."))
	reg = frappe.get_doc(DT, name)
	if reg.status in ("Rejected", "Disabled"):
		frappe.throw(_("This registration cannot be used."))
	_check_code(reg, code)
	first_time = not reg.email_verified
	reg.email_verified = 1
	if not reg.verified_on:
		reg.verified_on = now_datetime()
	needs_approval = _settings().registration_mode == "Registration + Approval"
	if reg.status == "Pending Verification":
		reg.status = "Pending Approval" if needs_approval else "Active"
	_ensure_user(reg, enabled=reg.status == "Active")
	reg.flags.ignore_permissions = True
	reg.save()
	if first_time:
		_notify_internal(reg)
	if reg.status != "Active":
		frappe.db.commit()
		return {"state": "pending_approval"}
	_login(reg)
	frappe.db.commit()
	return {"state": "signed_in", "redirect": _redirect(redirect_to, reg.brand)}


@frappe.whitelist(allow_guest=True)
def whoami():
	if frappe.session.user == "Guest":
		return None
	return current_registration_payload()


def current_registration(user=None):
	user = user or frappe.session.user
	if user == "Guest":
		return None
	name = frappe.db.get_value(DT, {"user": user})
	return frappe.get_cached_doc(DT, name) if name else None


def current_registration_payload():
	reg = current_registration()
	user = frappe.session.user
	return {
		"email": user, "full_name": frappe.utils.get_fullname(user),
		"staff": frappe.db.get_value("User", user, "user_type") == "System User",
		"registration": reg.name if reg else None, "status": reg.status if reg else None,
		"profile": {
			"organization_name": reg.organization_name, "contact_name": reg.contact_name, "contact_email": reg.email,
			"contact_phone": reg.mobile, "industry_type": reg.industry_type, "industry_sector": reg.industry_sector,
			"sector_other": reg.sector_other, "company_nationality": reg.company_nationality, "cr_number": reg.cr_number,
		} if reg else None,
	}


# ---------------------------------------------------------------- desk actions & mail
def set_registration_status(reg, status):
	frappe.only_for(("System Manager", "GRC Maturity Manager"))
	if status == "Active" and not reg.email_verified:
		frappe.throw(_("The email has not been verified yet."))
	reg.status = status
	reg.reviewed_by = frappe.session.user
	if reg.user:
		frappe.db.set_value("User", reg.user, "enabled", 1 if status == "Active" else 0)
	elif status == "Active":
		_ensure_user(reg, enabled=True)
	reg.save()
	if status == "Active":
		_mail_status(reg, approved=True)
	elif status == "Rejected":
		_mail_status(reg, approved=False)


def _mail_status(reg, approved):
	brand = frappe.get_cached_doc("GRC Maturity Brand", reg.brand) if reg.brand else None
	from urllib.parse import quote

	link = frappe.utils.get_url(f"/grc-register?mode=signin&email={quote(reg.email)}" + (f"&b={brand.route_slug}" if brand else ""))
	frappe.sendmail(
		recipients=[reg.email],
		subject=_("Your registration is approved") if approved else _("Your registration was not approved"),
		template="grc_maturity_registration_status",
		args={"reg": reg, "brand": brand, "approved": approved, "link": link, "lang": reg.language or "en"},
		reference_doctype=DT, reference_name=reg.name,
	)


def _notify_internal(reg):
	brand = frappe.get_cached_doc("GRC Maturity Brand", reg.brand) if reg.brand else None
	recipients = [n.email for n in brand.notify] if brand else []
	if not recipients:
		return
	frappe.sendmail(
		recipients=recipients,
		subject=f"[GRC Maturity] New registration: {reg.organization_name} ({reg.status})",
		message=(f"<p><b>{frappe.utils.escape_html(reg.organization_name)}</b> registered: "
			f"{frappe.utils.escape_html(reg.contact_name)} &lt;{reg.email}&gt;, {frappe.utils.escape_html(reg.mobile or '')}<br>"
			f"{frappe.utils.escape_html(reg.industry_type or '')} · {frappe.utils.escape_html(reg.industry_sector or '')}<br>"
			f"Status: <b>{reg.status}</b></p><p><a href='{frappe.utils.get_url('/app/grc-maturity-registration/' + reg.name)}'>Open registration</a></p>"),
		reference_doctype=DT, reference_name=reg.name,
	)
