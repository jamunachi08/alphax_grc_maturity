# Copyright (c) 2026, IRSAA Business Solution (AlphaX) and contributors
import frappe
from frappe import _

from alphax_grc_maturity.engine import branding

no_cache = 1
sitemap = 0


def get_context(context):
	brand = branding.get_brand(frappe.form_dict.get("b"))
	theme = frappe.get_cached_doc("GRC Maturity Theme", brand.theme)
	boot = branding.boot_payload(brand.route_slug, frappe.form_dict.get("lang"))
	redirect_to = frappe.form_dict.get("redirect-to") or ""
	if not redirect_to.startswith("/") or redirect_to.startswith("//"):
		redirect_to = "/grc-assessment?b=" + brand.route_slug
	user = boot.get("user")
	if user and not user.get("staff") and user.get("status") == "Active":
		frappe.local.flags.redirect_location = redirect_to
		raise frappe.Redirect
	boot["page"] = {
		"mode": frappe.form_dict.get("mode") if frappe.form_dict.get("mode") in ("register", "signin") else "register",
		"email": (frappe.form_dict.get("email") or "")[:140],
		"state": (user or {}).get("status") or "",
		"redirect": redirect_to,
		"staff": bool(user and user.get("staff")),
	}
	context.no_cache = 1
	context.show_sidebar = False
	context.title = _("Register") + " · " + (brand.app_title or _("GRC Maturity Assessment"))
	context.favicon = brand.favicon or None
	context.theme_css = branding.theme_css(theme)
	context.google_font = branding.google_font_url(theme)
	context.boot_json = frappe.as_json(boot, indent=None).replace("</", "<\\/")
	context.lang_dir = "rtl" if boot["lang"] == "ar" else "ltr"
	context.html_lang = boot["lang"]
	context.asset_v = frappe.get_attr("alphax_grc_maturity.__version__")
	return context
