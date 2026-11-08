# Copyright (c) 2026, IRSAA Business Solution (AlphaX) and contributors
import frappe
from frappe import _

from alphax_grc_maturity.engine import branding

no_cache = 1
sitemap = 0


def get_context(context):
	settings = frappe.get_cached_doc("GRC Maturity Settings")
	if frappe.session.user == "Guest" and not settings.allow_guest:
		from urllib.parse import quote

		frappe.local.flags.redirect_location = "/login?redirect-to=" + quote(frappe.request.full_path)
		raise frappe.Redirect
	brand = branding.get_brand(frappe.form_dict.get("b"))
	theme = frappe.get_cached_doc("GRC Maturity Theme", brand.theme)
	lang = frappe.form_dict.get("lang")
	boot = branding.boot_payload(brand.route_slug, lang)
	context.no_cache = 1
	context.show_sidebar = False
	context.title = brand.app_title or _("GRC Maturity Assessment")
	context.favicon = brand.favicon or None
	context.theme_css = branding.theme_css(theme)
	context.google_font = branding.google_font_url(theme)
	context.boot_json = frappe.as_json(boot, indent=None).replace("</", "<\\/")
	context.lang_dir = "rtl" if boot["lang"] == "ar" else "ltr"
	context.html_lang = boot["lang"]
	context.asset_v = frappe.get_attr("alphax_grc_maturity.__version__")
	return context
