app_name = "alphax_grc_maturity"
app_title = "AlphaX GRC Maturity"
app_publisher = "IRSAA Business Solution"
app_description = "GRC maturity assessment with global and profile-specific questions and weightage, white-label portal (AlphaX)"
app_email = "grc.audit.assessment@irsaa.com"
app_license = "Proprietary"
app_logo_url = "/assets/alphax_grc_maturity/images/alphax-logo.svg"

required_apps = ["frappe"]

add_to_apps_screen = [
	{
		"name": "alphax_grc_maturity",
		"logo": "/assets/alphax_grc_maturity/images/alphax-logo.svg",
		"title": "GRC Maturity",
		"route": "/app/grc-maturity",
	}
]

after_install = "alphax_grc_maturity.install.after_install"
after_migrate = "alphax_grc_maturity.install.after_migrate"

_clear = {
	"on_update": "alphax_grc_maturity.engine.resolver.on_master_change",
	"on_trash": "alphax_grc_maturity.engine.resolver.on_master_change",
}
doc_events = {
	dt: _clear
	for dt in (
		"GRC Maturity Section",
		"GRC Maturity Topic",
		"GRC Maturity Regulator",
		"GRC Maturity Industry Type",
		"GRC Maturity Industry Sector",
		"GRC Maturity Nationality",
		"GRC Maturity License Type",
		"GRC Maturity Question",
	)
}

website_route_rules = []
