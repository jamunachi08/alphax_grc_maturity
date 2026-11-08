#!/usr/bin/env python3
"""Structural guard for alphax_grc_maturity. Run before every push: python3 verify_tree.py"""
import ast, json, os, py_compile, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
APP = "alphax_grc_maturity"
PKG = os.path.join(ROOT, APP)
MOD_DIR = os.path.join(PKG, APP)
CORE = {"DocType", "User", "Email Account", "Role", "Currency", "Country", "File"}
RESERVED = {"name", "owner", "creation", "modified", "modified_by", "docstatus", "idx", "parent", "parenttype", "parentfield", "doctype"}
errors = []
err = errors.append

# 1. python compiles
for d, _, files in os.walk(ROOT):
	for f in files:
		if f.endswith(".py"):
			try:
				py_compile.compile(os.path.join(d, f), doraise=True)
			except py_compile.PyCompileError as e:
				err(f"compile: {e}")

# 2. doctypes
doctypes = {}
dt_dir = os.path.join(MOD_DIR, "doctype")
for folder in sorted(os.listdir(dt_dir)):
	p = os.path.join(dt_dir, folder)
	if not os.path.isdir(p) or folder.startswith("__"):
		continue
	for need in ("__init__.py", f"{folder}.json", f"{folder}.py"):
		if not os.path.exists(os.path.join(p, need)):
			err(f"{folder}: missing {need}")
	d = json.load(open(os.path.join(p, f"{folder}.json")))
	if d["name"].lower().replace(" ", "_") != folder:
		err(f"{folder}: name mismatch {d['name']}")
	if d["module"] != "AlphaX GRC Maturity":
		err(f"{folder}: module {d['module']}")
	cls = d["name"].replace(" ", "")
	if f"class {cls}(Document)" not in open(os.path.join(p, f"{folder}.py")).read():
		err(f"{folder}: controller class {cls} not found")
	doctypes[d["name"]] = d
for name, d in doctypes.items():
	names = [f["fieldname"] for f in d["fields"]]
	if len(names) != len(set(names)):
		err(f"{name}: duplicate fieldnames")
	if names != d["field_order"]:
		err(f"{name}: field_order out of sync")
	for f in d["fields"]:
		fn, ft, opt = f["fieldname"], f["fieldtype"], f.get("options")
		if fn in RESERVED:
			err(f"{name}.{fn}: reserved fieldname")
		if ft in ("Link", "Table", "Table MultiSelect") and opt not in doctypes and opt not in CORE:
			err(f"{name}.{fn}: unknown target {opt}")
		if ft == "Table" and opt in doctypes and not doctypes[opt]["istable"]:
			err(f"{name}.{fn}: {opt} is not a child table")
		if ft == "Dynamic Link" and opt not in names:
			err(f"{name}.{fn}: dynamic link source {opt} missing")
		for key in ("depends_on", "mandatory_depends_on"):
			for ref in re.findall(r"doc\.(\w+)", f.get(key) or ""):
				if ref not in names:
					err(f"{name}.{fn}: {key} references unknown field {ref}")
	if d.get("autoname", "").startswith("field:") and d["autoname"][6:] not in names:
		err(f"{name}: autoname field missing")
	if d.get("title_field") and d["title_field"] not in names:
		err(f"{name}: title_field missing")

# 3. hooks / dotted paths
src = open(os.path.join(PKG, "hooks.py")).read()
paths = set(re.findall(r'"(alphax_grc_maturity\.[\w\.]+)"', src))
for root_dir, _, files in os.walk(PKG):
	for f in files:
		if f.endswith((".js", ".py", ".html")):
			paths |= set(re.findall(r'["\'`](alphax_grc_maturity\.(?:api|engine|setup|install)[\w\.]+?)["\'`/]', open(os.path.join(root_dir, f), encoding="utf-8").read()))
for path in sorted(paths):
	mod, fn = path.rsplit(".", 1)
	fpath = os.path.join(ROOT, *mod.split(".")) + ".py"
	if not os.path.exists(fpath):
		if os.path.exists(os.path.join(ROOT, *path.split(".")) + ".py"):
			continue
		err(f"path {path}: module file missing")
		continue
	tree = ast.parse(open(fpath).read())
	defined = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
	defined |= {a.asname or a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) for a in n.names}
	if fn not in defined:
		err(f"path {path}: {fn} not defined")
# portal endpoints used by JS must be whitelisted with allow_guest
js = open(os.path.join(PKG, "public/js/grc_assessment.js")).read()
portal = open(os.path.join(PKG, "api/portal.py")).read()
for m in set(re.findall(r'call\("(\w+)"', js)) | {"pdf"}:
	if not re.search(r"@frappe\.whitelist\(allow_guest=True[^)]*\)\n(?:@[^\n]+\n)*def " + m + r"\(", portal):
		err(f"portal.{m}: not a guest-whitelisted endpoint")

reg_js = open(os.path.join(PKG, "public/js/grc_register.js")).read()
reg_py = open(os.path.join(PKG, "api/registration.py")).read()
for m in set(re.findall(r'call\("(\w+)"', reg_js)):
	if not re.search(r"@frappe\.whitelist\(allow_guest=True[^)]*\)\n(?:@[^\n]+\n)*def " + m + r"\(", reg_py):
		err(f"registration.{m}: not a guest-whitelisted endpoint")
for fn in ("_hash", "_check_code", "compare_digest", "rate_limit", 'user_type == "System User"'):
	if fn not in reg_py:
		err(f"registration security guard missing: {fn}")
if "allow_guest" in json.dumps(json.load(open(os.path.join(dt_dir, "grc_maturity_settings", "grc_maturity_settings.json")))["field_order"]):
	err("settings: allow_guest was replaced by registration_mode")

# 4. seed integrity
S = lambda n: json.load(open(os.path.join(PKG, "setup/seed_data", f"{n}.json"), encoding="utf-8"))
regs = {r["regulator_name"] for r in S("regulators")}
inds = {i["industry_type"] for i in S("industries")}
secs = {f"{s['industry_type']} | {s['sector_name']}" for s in S("sectors")}
nats = {n["nationality"] for n in S("nationalities")}
sections = {s["section_id"] for s in S("sections")}
topics = {f"{t['section']} | {t['topic_label']}" for t in S("topics")}
lic = {l["license_type"] for l in S("license_types")}
lf = {l["legal_form"] for l in S("legal_forms")}
es = {e["entity_size"] for e in S("entity_sizes")}
qs = S("questions") + S("sample_questions")
qcodes = {q["question_code"] for q in qs}
for group, items in (("industries", S("industries")), ("sectors", S("sectors")), ("nationalities", S("nationalities"))):
	for x in items:
		for r in x["regulators"]:
			if r not in regs:
				err(f"seed {group}: unknown regulator {r}")
for s in S("sectors"):
	if s["industry_type"] not in inds:
		err(f"seed sector industry {s['industry_type']}")
dim = {"Industry Type": inds, "Industry Sector": secs, "Company Nationality": nats, "License Type": lic, "Regulator": regs, "Legal Form": lf, "Entity Size": es}
for q in qs:
	if q["section"] not in sections:
		err(f"seed {q['question_code']}: section")
	if q.get("topic") and q["topic"] not in topics:
		err(f"seed {q['question_code']}: topic {q['topic']}")
	if len(q["options"]) < 2:
		err(f"seed {q['question_code']}: options")
	for r in q.get("rules", []):
		if r["value"] not in dim[r["dimension"]]:
			err(f"seed {q['question_code']}: rule value {r['value']}")
	if q.get("replaces_question") and q["replaces_question"] not in qcodes:
		err(f"seed {q['question_code']}: replaces unknown")
for p in S("profiles"):
	for l in p["lines"]:
		tgt = l.get(l["applies_to"].lower())
		ok = {"Section": sections, "Topic": topics, "Question": qcodes}[l["applies_to"]]
		if tgt not in ok:
			err(f"seed profile {p['profile_name']}: {l['applies_to']} {tgt}")
	for f, pool in (("industry_type", inds), ("industry_sector", secs), ("company_nationality", nats)):
		if p.get(f) and p[f] not in pool:
			err(f"seed profile {p['profile_name']}: {f}")
if sum(1 for p in S("profiles") if p.get("is_global")) != 1:
	err("seed: exactly one global profile required")
themes = {t["theme_name"] for t in S("themes")}
for b in S("brands"):
	if b["theme"] not in themes:
		err(f"seed brand theme {b['theme']}")
if len(S("questions")) != 46:
	err("seed: expected 46 standard questions")

# 5. workspace & report
ws = json.load(open(os.path.join(MOD_DIR, "workspace/grc_maturity/grc_maturity.json")))
for l in ws["links"]:
	if l["type"] == "Link" and l["link_type"] == "DocType" and l["link_to"] not in doctypes:
		err(f"workspace link {l['link_to']}")
for s in ws["shortcuts"]:
	if s["type"] == "DocType" and s["link_to"] not in doctypes:
		err(f"workspace shortcut {s['link_to']}")
for need in ("www/grc-assessment.html", "www/grc-assessment.py", "public/css/grc_assessment.css", "templates/emails/grc_maturity_report.html",
		f"{APP}/print_format/grc_maturity_report/grc_maturity_report.json", f"{APP}/report/grc_maturity_summary/grc_maturity_summary.py",
		"modules.txt", "patches.txt", "translations/ar.csv", "www/grc-register.html", "www/grc-register.py", "public/js/grc_register.js",
		"templates/emails/grc_maturity_otp.html", "templates/emails/grc_maturity_registration_status.html"):
	if not os.path.exists(os.path.join(PKG, need)):
		err(f"missing {need}")

# 6. no-blank-answers rule (v1.0.1)
for d, _, files in os.walk(PKG):
	for f in files:
		if f.endswith((".py", ".js", ".json")) and "seed_data" not in d:
			txt = open(os.path.join(d, f), encoding="utf-8").read()
			for banned in ("blank_scores_zero", "all_mandatory", "is_mandatory"):
				if banned in txt:
					err(f"{f}: '{banned}' must not exist (blank answers are never allowed)")
ctrl = open(os.path.join(dt_dir, "grc_maturity_assessment", "grc_maturity_assessment.py")).read()
if 'if self.status != "Draft":' not in ctrl or "validate_complete(self)" not in ctrl:
	err("assessment controller must run validate_complete on every non-Draft save")
if "allQ().filter((q) => !S.answers[q.name])" not in js:
	err("portal must block submit on any blank answer")

if errors:
	print("\n".join("✗ " + e for e in errors))
	sys.exit(1)
print(f"✓ verify_tree: {len(doctypes)} doctypes, {len(paths)} dotted paths, {len(qs)} seeded questions — all checks passed")
