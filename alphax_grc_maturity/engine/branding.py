# Copyright (c) 2026, IRSAA Business Solution (AlphaX) and contributors
"""Brand / theme resolution and the boot payload for the portal page."""

import re

import frappe
from frappe import _

COLOR_RE = re.compile(r"^#[0-9a-fA-F]{3,8}$")
FONT_RE = re.compile(r"^[A-Za-z0-9 ]{1,60}$")


def get_brand(slug_or_name=None):
	if slug_or_name:
		name = frappe.db.get_value("GRC Maturity Brand", {"route_slug": slug_or_name, "enabled": 1}, "name") or (
			slug_or_name if frappe.db.exists("GRC Maturity Brand", {"name": slug_or_name, "enabled": 1}) else None
		)
		if name:
			return frappe.get_cached_doc("GRC Maturity Brand", name)
	default = frappe.db.get_single_value("GRC Maturity Settings", "default_brand")
	if default:
		return frappe.get_cached_doc("GRC Maturity Brand", default)
	frappe.throw(_("No GRC Maturity Brand is configured. Set a Default Brand in GRC Maturity Settings."))


def _c(value, fallback):
	return value if value and COLOR_RE.match(value) else fallback


def theme_css(theme):
	"""CSS custom properties for a theme. Colors are validated so admin input cannot break out of the style block."""
	t = theme
	light = {
		"--axg-primary": _c(t.primary_color, "#1e3a5f"), "--axg-primary-dark": _c(t.primary_dark_color, "#143049"),
		"--axg-accent": _c(t.accent_color, "#1e7b4c"), "--axg-bg": _c(t.background_color, "#f4f7fc"),
		"--axg-surface": _c(t.surface_color, "#ffffff"), "--axg-soft": _c(t.soft_color, "#eef3fa"),
		"--axg-text": _c(t.text_color, "#1e2a3a"), "--axg-muted": _c(t.muted_color, "#5a6f87"),
		"--axg-border": _c(t.border_color, "#e7edf4"),
	}
	dark = {
		"--axg-bg": _c(t.dark_background_color, "#0f1722"), "--axg-surface": _c(t.dark_surface_color, "#172233"),
		"--axg-soft": _c(t.dark_border_color, "#26354a"), "--axg-text": _c(t.dark_text_color, "#e6edf6"),
		"--axg-muted": _c(t.dark_muted_color, "#93a5bb"), "--axg-border": _c(t.dark_border_color, "#26354a"),
	}
	font = (t.font_family or "").replace(";", "").replace("}", "").replace("<", "")[:200] or "system-ui, sans-serif"
	afont = (t.arabic_font_family or "").replace(";", "").replace("}", "").replace("<", "")[:200] or font
	radius = max(0, min(32, t.radius or 16))
	pad = "0.75rem 1rem" if t.density == "Compact" else "1rem 1.25rem"
	block = lambda d: ";".join(f"{k}:{v}" for k, v in d.items())
	css = f":root{{{block(light)};--axg-radius:{radius}px;--axg-pad:{pad};--axg-font:{font};--axg-font-ar:{afont}}}"
	if t.mode == "Dark":
		css += f":root{{{block(dark)};color-scheme:dark}}"
	elif t.mode == "Auto":
		css += f"@media (prefers-color-scheme: dark){{:root{{{block(dark)};color-scheme:dark}}}}"
	if t.custom_css:
		css += "\n" + t.custom_css.replace("</", "<\\/")
	return css


def google_font_url(theme):
	if theme.google_font and FONT_RE.match(theme.google_font):
		return "https://fonts.googleapis.com/css2?family=" + theme.google_font.strip().replace(" ", "+") + ":wght@400;500;600;700&display=swap"
	return None


def label_regulators(rows, lang):
	if lang != "ar":
		return [{**r, "label": r["regulator"]} for r in rows]
	ar = dict(frappe.get_all("GRC Maturity Regulator", fields=["name", "regulator_name_ar"], as_list=True))
	return [{**r, "label": ar.get(r["regulator"]) or r["regulator"]} for r in rows]


def boot_payload(slug=None, lang=None):
	s = frappe.get_cached_doc("GRC Maturity Settings")
	brand = get_brand(slug)
	theme = frappe.get_cached_doc("GRC Maturity Theme", brand.theme)
	lang = lang if lang in ("en", "ar") and (lang == "en" or s.enable_arabic) else (s.default_language or "en")

	def rows(dt, label, label_ar, extra=()):
		fields = ["name", label, label_ar, *extra]
		return [
			{"value": r.name, "label": r.get(label), "label_ar": r.get(label_ar), **{e: r.get(e) for e in extra}}
			for r in frappe.get_all(dt, filters={"enabled": 1}, fields=fields, order_by="sequence asc, name asc")
		]

	sectors = {}
	for r in frappe.get_all("GRC Maturity Industry Sector", filters={"enabled": 1},
			fields=["name", "industry_type", "sector_name", "sector_name_ar", "is_other"], order_by="sequence asc, sector_name asc"):
		sectors.setdefault(r.industry_type, []).append({"value": r.name, "label": r.sector_name, "label_ar": r.sector_name_ar, "is_other": r.is_other})
	industries = rows("GRC Maturity Industry Type", "industry_type", "industry_type_ar")
	for i in industries:
		i["sectors"] = sectors.get(i["value"], [])
	white = bool(brand.white_label)
	return {
		"lang": lang, "arabic": bool(s.enable_arabic), "version": s.app_version_label or "",
		"brand": {
			"slug": brand.route_slug, "title": brand.app_title, "title_ar": brand.app_title_ar,
			"company": brand.company_name, "logo": brand.logo, "logo_dark": brand.logo_dark,
			"website": brand.website, "support_email": brand.support_email,
			"intro": brand.intro_text, "intro_ar": brand.intro_text_ar,
			"footer": brand.footer_text, "footer_ar": brand.footer_text_ar,
			"powered_by": None if white else (brand.powered_by_text or "Powered by AlphaX · IRSAA Business Solution"),
			"hide_score": bool(brand.hide_score_from_respondent), "show_weights": bool(brand.show_weights),
		},
		"theme": {"mode": theme.mode, "layout": theme.layout_style or "Cards", "density": theme.density},
		"flags": {
			"require_email": bool(s.require_contact_email), "ask_legal_form": bool(s.ask_legal_form),
			"ask_entity_size": bool(s.ask_entity_size), "ask_licenses": bool(s.ask_license_types),
			"license_mode": s.license_mode or "Both", "ask_regulators": bool(s.ask_regulators),
			"regulators_drive": bool(s.regulator_answers_drive_questions),
		},
		"industries": industries,
		"nationalities": rows("GRC Maturity Nationality", "nationality", "nationality_ar", ("ask_cr", "is_foreign")),
		"license_types": rows("GRC Maturity License Type", "license_type", "license_type_ar"),
		"legal_forms": rows("GRC Maturity Legal Form", "legal_form", "legal_form_ar"),
		"entity_sizes": rows("GRC Maturity Entity Size", "entity_size", "entity_size_ar", ("description",)),
		"scale": [{"value": r.option_value, "label": r.option_label, "label_ar": r.option_label_ar, "points": r.points} for r in s.answer_scale],
		"bands": [{"key": b.band_key, "label": b.band_label, "label_ar": b.band_label_ar, "min": b.min_pct, "max": b.max_pct,
			"color": b.color, "icon": b.icon, "text": b.interpretation, "text_ar": b.interpretation_ar} for b in sorted(s.bands, key=lambda b: b.min_pct)],
	}
