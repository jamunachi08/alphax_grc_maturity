/* AlphaX GRC Maturity · respondent portal
 * Copyright (c) 2026, IRSAA Business Solution (AlphaX). Proprietary.
 * Vanilla JS, no build step. All data comes from alphax_grc_maturity.api.portal.
 */
(function () {
	"use strict";
	const B = window.AXG_BOOT;
	const root = document.getElementById("axg-app");
	if (!root) return;
	if (!B) {
		root.innerHTML = '<div class="axg-shell axg-center"><h2>The assessment page could not start.</h2><p class="axg-muted">The page settings did not load. Ask the administrator to check GRC Maturity Settings and the Error Log.</p></div>';
		return;
	}
	const API = "/api/method/alphax_grc_maturity.api.portal.";
	const STORE = "axg_saved:" + (B.brand.slug || "default");
	let lang = B.lang || "en";

	// ------------------------------------------------------------------ i18n
	const I = {
		en: {
			start: "▶ Start Assessment", welcome: "Welcome to the Assessment",
			intro_count: "Answer all {q} questions across {s} sections to generate a detailed maturity report.",
			questions: "Questions", sections: "Sections", levels: "Maturity Levels",
			profile: "Organization profile", not_scored: "Not scored. It appears in your report.",
			org: "Organization name", contact_name: "Contact name", contact_email: "Contact email", contact_phone: "Phone",
			industry: "Industry type", sector: "Industry sector", name_sector: "Name the sector", nationality: "Company nationality",
			cr: "Saudi Commercial Registration (CR) number (optional)", cr_ph: "10 digits (optional)",
			legal: "Legal form", size: "Entity size", select: "Select",
			lic_h: "KSA licenses", lic_q: "What type of KSA license does the entity have? (e.g., investment license, SAMA license, CST license)",
			lic_ph: "Type the license types", lic_na: "N/A (no KSA license)",
			lic_rows: "Is each license still valid, and what is its expiry date? (optional, one row per license)",
			lic_type: "License type", lic_name: "License name / number", valid: "Valid?", yes: "Yes", no: "No", add_lic: "+ Add license",
			lic_expired: "This license expired on {d}, so it cannot be marked valid.",
			regs_h: "Regulators: is the entity regulated by each of these?", other_reg: "Other regulator (optional)", type_name: "Type a name",
			cont: "Continue to questions ▶", submit: "✅ Submit & Generate Report", save: "💾 Save", report: "📊 Report", new_a: "＋ New",
			saved_toast: "Progress saved.", saving: "Saving…", saved: "Saved", complete: "{p}% complete", answered: "{d} / {n} answered",
			na: "N/A", na_desc: "It’s not applicable.",
			missing: "Answer all questions before submitting. {n} left, starting with {q}.",
			v_org: "Enter the organization name.", v_ind: "Select the industry type.", v_sec: "Select the industry sector.",
			v_secname: "Name the sector.", v_nat: "Select the company nationality.", v_cr: "The CR number must be 10 digits, or leave it empty.",
			v_lic: "Enter the KSA license type, or tick N/A.", v_licrow: "Complete each license row (name, valid, expiry date), or remove it.",
			v_licvalid: "A license with a past expiry date cannot be marked valid: {n}.", v_email: "Enter a valid contact email.",
			back_q: "◀ Back to questions", back_p: "Edit profile", print: "🖨 Print", pdf: "⬇ Download PDF",
			lookup: "🔍 Open a saved assessment:", id_ph: "Report ID", key_ph: "Access key", load: "Load",
			saved_h: "Saved on this device", keep_key: "Keep this ID and access key to reopen your assessment.",
			rep_title: "Assessment Report", points: "{a} / {p} points", q_answered: "{d} / {n} questions answered", na_count: "{n} N/A",
			topics: "Topics", question: "Question", selected: "Selected", score: "Score", category: "Category",
			roadmap: "Improvement roadmap", current: "Current", target: "Next target",
			interp: "Maturity Interpretation", interp_note: "Questions answered N/A are left out of the score.",
			license: "License", still_valid: "Still valid", expiry: "Expiry date", no_lic: "No KSA license", licenses_lbl: "Licenses",
			thanks_h: "Thank you. Your assessment was submitted.", thanks_p: "Our consultants will review your answers and share the report with you.",
			prev: "◀ Previous", next: "Next ▶", notes: "Consultant notes",
			confirm_profile: "Changing the profile can change which questions apply. Answers to questions that no longer apply are removed.",
			weight: "weight", conditional: "for your profile", src_General: "General", src_Industry: "Industry", src_Sector: "Sector", src_Nationality: "Ownership",
			staff_note: "You are signed in as a staff user, so registration and the email code are skipped. To see what a respondent sees, open {u} in a private (incognito) window.",
			open: "Open", lang_toggle: "العربية", staff_note: "Staff preview: you are signed in as a staff user, so registration and the email code are skipped. Respondents must register at /grc-register. To test that flow, use a private window or sign out.", signout: "Sign out", mine: "My assessments", need_answer: "Answer at least one question first.", error: "Something went wrong. Please try again.",
		},
		ar: {
			start: "◀ ابدأ التقييم", welcome: "مرحبًا بك في التقييم",
			intro_count: "أجب عن جميع الأسئلة البالغ عددها {q} في {s} أقسام للحصول على تقرير نضج مفصل.",
			questions: "الأسئلة", sections: "الأقسام", levels: "مستويات النضج",
			profile: "ملف المنشأة", not_scored: "لا يُحتسب في الدرجة، ويظهر في تقريرك.",
			org: "اسم المنشأة", contact_name: "اسم المسؤول", contact_email: "البريد الإلكتروني", contact_phone: "رقم الجوال",
			industry: "نوع النشاط", sector: "القطاع", name_sector: "حدد القطاع", nationality: "جنسية الشركة",
			cr: "رقم السجل التجاري السعودي (اختياري)", cr_ph: "10 أرقام (اختياري)",
			legal: "الشكل القانوني", size: "حجم المنشأة", select: "اختر",
			lic_h: "التراخيص في المملكة", lic_q: "ما نوع الترخيص الذي تحمله المنشأة في المملكة؟ (مثل ترخيص الاستثمار، ترخيص ساما، ترخيص هيئة الاتصالات)",
			lic_ph: "اكتب أنواع التراخيص", lic_na: "لا ينطبق (لا يوجد ترخيص)",
			lic_rows: "هل كل ترخيص ساري، وما تاريخ انتهائه؟ (اختياري، صف لكل ترخيص)",
			lic_type: "نوع الترخيص", lic_name: "اسم الترخيص أو رقمه", valid: "ساري؟", yes: "نعم", no: "لا", add_lic: "+ إضافة ترخيص",
			lic_expired: "انتهى هذا الترخيص في {d}، لذا لا يمكن اعتباره ساريًا.",
			regs_h: "الجهات التنظيمية: هل تخضع المنشأة لكل من الجهات التالية؟", other_reg: "جهة تنظيمية أخرى (اختياري)", type_name: "اكتب الاسم",
			cont: "متابعة إلى الأسئلة ◀", submit: "✅ إرسال وإنشاء التقرير", save: "💾 حفظ", report: "📊 التقرير", new_a: "＋ جديد",
			saved_toast: "تم حفظ التقدم.", saving: "جارٍ الحفظ…", saved: "تم الحفظ", complete: "مكتمل {p}%", answered: "تمت الإجابة على {d} من {n}",
			na: "لا ينطبق", na_desc: "غير منطبق.",
			missing: "أجب عن جميع الأسئلة قبل الإرسال. متبقٍ {n}، بدءًا من {q}.",
			v_org: "أدخل اسم المنشأة.", v_ind: "اختر نوع النشاط.", v_sec: "اختر القطاع.", v_secname: "حدد اسم القطاع.",
			v_nat: "اختر جنسية الشركة.", v_cr: "يجب أن يتكون رقم السجل التجاري من 10 أرقام، أو اتركه فارغًا.",
			v_lic: "أدخل نوع الترخيص، أو اختر لا ينطبق.", v_licrow: "أكمل كل صف ترخيص (الاسم، السريان، تاريخ الانتهاء) أو احذفه.",
			v_licvalid: "لا يمكن اعتبار ترخيص منتهي التاريخ ساريًا: {n}.", v_email: "أدخل بريدًا إلكترونيًا صحيحًا.",
			back_q: "▶ العودة إلى الأسئلة", back_p: "تعديل الملف", print: "🖨 طباعة", pdf: "⬇ تنزيل PDF",
			lookup: "🔍 فتح تقييم محفوظ:", id_ph: "رقم التقرير", key_ph: "مفتاح الوصول", load: "فتح",
			saved_h: "محفوظ على هذا الجهاز", keep_key: "احتفظ برقم التقرير ومفتاح الوصول لفتح تقييمك لاحقًا.",
			rep_title: "تقرير التقييم", points: "{a} من {p} نقطة", q_answered: "تمت الإجابة على {d} من {n} سؤالًا", na_count: "{n} لا ينطبق",
			topics: "المحاور", question: "السؤال", selected: "الإجابة", score: "الدرجة", category: "الفئة",
			roadmap: "خارطة التحسين", current: "الوضع الحالي", target: "الهدف التالي",
			interp: "تفسير مستويات النضج", interp_note: "الأسئلة المجاب عنها بـ «لا ينطبق» لا تُحتسب في الدرجة.",
			license: "الترخيص", still_valid: "ساري", expiry: "تاريخ الانتهاء", no_lic: "لا يوجد ترخيص", licenses_lbl: "التراخيص",
			thanks_h: "شكرًا لك. تم إرسال تقييمك.", thanks_p: "سيقوم مستشارونا بمراجعة إجاباتك ومشاركة التقرير معك.",
			prev: "▶ السابق", next: "التالي ◀", notes: "ملاحظات المستشار",
			confirm_profile: "قد يؤدي تغيير الملف إلى تغيير الأسئلة المطبقة، وتُحذف إجابات الأسئلة التي لم تعد تنطبق.",
			weight: "الوزن", conditional: "خاص بملفك", src_General: "عامة", src_Industry: "النشاط", src_Sector: "القطاع", src_Nationality: "الملكية",
			staff_note: "أنت مسجّل الدخول بحساب موظف، لذلك يتم تخطي التسجيل ورمز البريد. لمشاهدة ما يراه المستجيب افتح {u} في نافذة خاصة (التصفح المتخفي).",
			open: "فتح", lang_toggle: "English", staff_note: "معاينة الموظف: أنت مسجّل الدخول كموظف، لذا يتم تجاوز التسجيل ورمز البريد. يجب على المستجيبين التسجيل في /grc-register. لتجربة ذلك استخدم نافذة خاصة أو سجّل الخروج.", signout: "تسجيل الخروج", mine: "تقييماتي", need_answer: "أجب عن سؤال واحد على الأقل أولًا.", error: "حدث خطأ. حاول مرة أخرى.",
		},
	};
	const t = (k, v) => {
		let s = (I[lang] && I[lang][k]) || I.en[k] || k;
		if (v) Object.keys(v).forEach((x) => (s = s.split("{" + x + "}").join(v[x])));
		return s;
	};
	const L = (o) => (o ? (lang === "ar" && o.label_ar ? o.label_ar : o.label) : "");
	const esc = (x) => String(x == null ? "" : x).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
	const $ = (s, el) => (el || root).querySelector(s);
	const $$ = (s, el) => Array.from((el || root).querySelectorAll(s));
	const today = () => new Date().toISOString().slice(0, 10);

	// ------------------------------------------------------------------ state
	// Registered respondents start every new assessment with their registration details (still editable).
	function prefill() {
		const p = (B.user && B.user.profile) || {};
		const out = {};
		Object.keys(p).forEach((k) => { if (p[k]) out[k] = p[k]; });
		return out;
	}
	const blankProfile = () => Object.assign({
		organization_name: "", contact_name: "", contact_email: "", contact_phone: "",
		industry_type: "", industry_sector: "", sector_other: "", company_nationality: "", cr_number: "",
		legal_form: "", entity_size: "", license_na: 0, license_types_text: "",
		licenses: [{ license_type: "", license_name: "", is_valid: "", expiry_date: "" }], regulators: {}, other_regulator: "",
	}, prefill());
	const S = { view: "welcome", id: null, k: null, status: "Draft", profile: blankProfile(), answers: {}, sections: [],
		regulators: [], step: 0, rev: 0, timer: null, globalCount: 0, globalSections: 0, report: null };

	// ------------------------------------------------------------------ api
	function errText(data) {
		try {
			if (data._server_messages) {
				return JSON.parse(data._server_messages).map((m) => JSON.parse(m).message).join(" ").replace(/<[^>]+>/g, "");
			}
		} catch (e) { /* ignore */ }
		return (data.exception || "").split(":").slice(1).join(":").trim() || t("error");
	}
	async function call(method, args, post) {
		const params = new URLSearchParams();
		Object.entries(args || {}).forEach(([k, v]) => v != null && params.append(k, typeof v === "object" ? JSON.stringify(v) : v));
		const opts = { method: post ? "POST" : "GET", headers: { Accept: "application/json" }, credentials: "same-origin" };
		let url = API + method;
		if (post) {
			opts.body = params;
			opts.headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8";
			opts.headers["X-Frappe-CSRF-Token"] = (window.frappe && window.frappe.csrf_token) || "";
		} else url += "?" + params.toString();
		const res = await fetch(url, opts);
		let data = {};
		try { data = await res.json(); } catch (e) { /* non-json */ }
		if (!res.ok || data.exc_type) throw new Error(errText(data));
		return data.message;
	}

	// ------------------------------------------------------------------ device store
	const store = {
		all() { try { return JSON.parse(localStorage.getItem(STORE) || "[]"); } catch (e) { return []; } },
		put(a) { try { localStorage.setItem(STORE, JSON.stringify(a.slice(0, 25))); } catch (e) { /* storage off */ } },
		add(id, k, org) { this.put([{ id, k, org, date: new Date().toISOString() }, ...this.all().filter((x) => x.id !== id)]); },
		del(id) { this.put(this.all().filter((x) => x.id !== id)); },
	};

	// ------------------------------------------------------------------ helpers
	function toast(m, type, ms) {
		const box = $(".axg-toasts");
		const e = document.createElement("div");
		e.className = "axg-toast " + (type || "");
		e.textContent = m;
		box.appendChild(e);
		setTimeout(() => e.remove(), ms || 5000);
	}
	const allQ = () => S.sections.flatMap((s) => s.topics.flatMap((tp) => tp.questions));
	const isDark = () => B.theme.mode === "Dark" || (B.theme.mode === "Auto" && window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches);
	const industry = () => B.industries.find((i) => i.value === S.profile.industry_type);
	const nat = () => B.nationalities.find((n) => n.value === S.profile.company_nationality);
	const payload = () => Object.assign({}, S.profile, { language: lang, brand: B.brand.slug, answers: S.answers });
	function setDir() {
		root.setAttribute("dir", lang === "ar" ? "rtl" : "ltr");
		root.setAttribute("lang", lang);
		document.documentElement.setAttribute("lang", lang);
	}

	// ------------------------------------------------------------------ shell
	function shell() {
		const br = B.brand;
		const logo = (isDark() && br.logo_dark) || br.logo;
		const title = (lang === "ar" && br.title_ar) || br.title || "GRC Maturity Assessment";
		const footer = (lang === "ar" && br.footer_ar) || br.footer || "";
		root.innerHTML = `<div class="axg-shell">
			<div class="axg-head">
				<div class="axg-brand">${logo ? `<img src="${esc(logo)}" alt="${esc(br.company || "")}">` : ""}
					<div><h1 class="axg-title">${esc(title)} <small>${esc(B.version)}</small></h1>
					<div class="axg-muted axg-small"><span id="axg-org">${esc(S.profile.organization_name || "")}</span> <span id="axg-savestate" class="axg-saving"></span></div></div></div>
				<div class="axg-tools">
					${B.user ? `<span class="axg-user">👤 ${esc(B.user.full_name || B.user.email)}</span><button class="axg-btn axg-btn-outline axg-btn-sm" data-act="signout">${t("signout")}</button>` : ""}
					${B.arabic ? `<button class="axg-btn axg-btn-outline axg-btn-sm" data-act="lang">${t("lang_toggle")}</button>` : ""}
					<button class="axg-btn axg-btn-outline axg-btn-sm" data-act="new">${t("new_a")}</button>
					<button class="axg-btn axg-btn-primary axg-btn-sm" data-act="save">${t("save")}</button>
					<button class="axg-btn axg-btn-accent axg-btn-sm" data-act="report">${t("report")}</button>
				</div>
			</div>
			<div class="axg-progress"><div class="axg-bar"><div id="axg-bar"></div></div>
				<div class="axg-bar-label"><span id="axg-pct"></span><span id="axg-cnt"></span></div></div>
			${B.user && B.user.staff && B.registration_mode !== "Open (no registration)" ? `<div class="axg-card axg-small axg-noprint" style="border-color:#ffc107;background:#fff8e1;color:#5c4400">⚠ ${t("staff_note")}</div>` : ""}
			<div id="axg-main"></div>
			<div class="axg-lookup axg-noprint">
				<label>${t("lookup")}</label>
				<input type="text" id="axg-lid" placeholder="${esc(t("id_ph"))}" autocomplete="off">
				<input type="text" id="axg-lkey" placeholder="${esc(t("key_ph"))}" autocomplete="off" style="max-width:180px">
				<button class="axg-btn axg-btn-primary axg-btn-sm" data-act="lookup">${t("load")}</button>
			</div>
			<div id="axg-savedwrap" class="axg-noprint"></div>
			<div class="axg-footer"><span>${esc(footer)}${br.support_email ? ` · <a href="mailto:${esc(br.support_email)}">${esc(br.support_email)}</a>` : ""}</span>
				${br.powered_by ? `<span>${esc(br.powered_by)}</span>` : ""}</div>
		</div><div class="axg-toasts"></div>`;
		root.querySelector(".axg-tools").addEventListener("click", onTool);
		$("[data-act=lookup]").onclick = () => openSaved($("#axg-lid").value.trim(), $("#axg-lkey").value.trim());
		renderSaved();
		head();
	}

	function onTool(e) {
		const b = e.target.closest("[data-act]");
		if (!b) return;
		const act = b.dataset.act;
		if (act === "lang") switchLang();
		if (act === "signout") {
			fetch("/api/method/logout", { credentials: "same-origin" }).finally(() => {
				window.location.href = "/grc-register?mode=signin" + (B.brand.slug ? "&b=" + encodeURIComponent(B.brand.slug) : "");
			});
		}
		if (act === "new") {
			if (!b.dataset.c) { b.dataset.c = "1"; const old = b.textContent; b.textContent = lang === "ar" ? "اضغط مرة أخرى للتأكيد" : "Click again to confirm"; setTimeout(() => { delete b.dataset.c; b.textContent = old; }, 3000); return; }
			delete b.dataset.c;
			{ Object.assign(S, { id: null, k: null, status: "Draft", profile: blankProfile(), answers: {}, sections: [], regulators: [], step: 0 }); history.replaceState(null, "", location.pathname + (B.brand.slug ? "?b=" + encodeURIComponent(B.brand.slug) : "")); show("welcome"); } }
		if (act === "save") { if (S.id && S.status === "Draft") saveNow(true); else if (S.view === "profile") onContinue(); }
		if (act === "report") {
			if (S.status !== "Draft") return openReport();
			if (!Object.keys(S.answers).length) return toast(t("need_answer"), "warning");
			onSubmit();
		}
	}

	function head() {
		const q = allQ();
		const d = q.filter((x) => S.answers[x.name]).length;
		const pct = q.length ? Math.round((100 * d) / q.length) : 0;
		const bar = $("#axg-bar");
		if (!bar) return;
		bar.style.width = pct + "%";
		$("#axg-pct").textContent = t("complete", { p: pct });
		$("#axg-cnt").textContent = t("answered", { d, n: q.length });
		$("#axg-org").textContent = S.profile.organization_name || "";
		$(".axg-progress").classList.toggle("axg-hidden", S.view !== "questions");
		$("[data-act=save]").classList.toggle("axg-hidden", !(S.view === "questions" || S.view === "profile") || S.status !== "Draft");
		$("[data-act=report]").classList.toggle("axg-hidden", !S.id);
	}

	async function renderSaved() {
		if (B.user) {
			let rows = [];
			try { rows = await call("mine", {}); } catch (e) { /* ignore */ }
			const w = $("#axg-savedwrap");
			if (!w) return;
			w.innerHTML = rows.length ? `<h3 class="axg-small" style="margin:1rem 0 0">📂 ${t("mine")}</h3><div class="axg-saved">${rows.map((x) =>
				`<div><span>📄 ${esc(x.id)}</span><span class="axg-muted">${esc(x.org || "")} · ${esc(x.status)}${x.maturity_band ? " · " + Math.round(x.overall_percentage) + "% " + esc(x.maturity_band) : ""}</span>
				<button class="axg-btn axg-btn-outline axg-btn-sm" data-open="${esc(x.id)}" data-k="${esc(x.k)}">${t("open")}</button></div>`).join("")}</div>` : "";
			w.querySelectorAll("[data-open]").forEach((b) => (b.onclick = () => openSaved(b.dataset.open, b.dataset.k)));
			return;
		}
		const a = store.all();
		const w = $("#axg-savedwrap");
		if (!a.length) { w.innerHTML = ""; return; }
		w.innerHTML = `<h3 class="axg-small" style="margin:1rem 0 0">📂 ${t("saved_h")}</h3><div class="axg-saved">${a.map((x) =>
			`<div><span>📄 ${esc(x.id)}</span><span class="axg-muted">${esc(x.org || "")} · ${new Date(x.date).toLocaleDateString()}</span>
			<button class="axg-btn axg-btn-outline axg-btn-sm" data-open="${esc(x.id)}">${t("open")}</button>
			<button class="axg-btn axg-btn-outline axg-btn-sm" data-del="${esc(x.id)}">✕</button></div>`).join("")}</div>`;
		$$("[data-open]", w).forEach((b) => (b.onclick = () => { const x = store.all().find((y) => y.id === b.dataset.open); if (x) openSaved(x.id, x.k); }));
		$$("[data-del]", w).forEach((b) => (b.onclick = () => { store.del(b.dataset.del); renderSaved(); }));
	}

	function show(v) {
		S.view = v;
		const m = $("#axg-main");
		if (v === "welcome") m.innerHTML = welcome();
		if (v === "profile") renderProfile();
		if (v === "questions") renderQuestions();
		if (v === "report") m.innerHTML = reportHtml(S.report);
		if (v === "thanks") m.innerHTML = thanksHtml();
		bindView();
		head();
		window.scrollTo(0, 0);
	}

	// ------------------------------------------------------------------ welcome
	function welcome() {
		const br = B.brand;
		const intro = (lang === "ar" && br.intro_ar) || br.intro || "";
		const staff = B.user && B.user.staff && B.registration_mode !== "Open (no registration)"
			? `<div class="axg-card axg-small" style="border-color:#e0b252;background:color-mix(in srgb,#ffc107 12%,var(--axg-surface))">ℹ️ ${esc(t("staff_note", { u: location.origin + "/grc-register" }))}</div>` : "";
		return staff + `<div class="axg-hero"><h2>${t("welcome")}</h2><div class="axg-intro">${intro}</div>
			<p class="axg-intro">${t("intro_count", { q: S.globalCount || "—", s: S.globalSections || "—" })}</p>
			<button class="axg-btn axg-btn-primary axg-btn-lg" data-go="profile">${t("start")}</button></div>
			<div class="axg-tiles"><div class="axg-tile"><b>${S.globalCount || "—"}</b><span class="axg-muted axg-small">${t("questions")}</span></div>
			<div class="axg-tile"><b>${S.globalSections || "—"}</b><span class="axg-muted axg-small">${t("sections")}</span></div>
			<div class="axg-tile"><b>${B.bands.length}</b><span class="axg-muted axg-small">${t("levels")}</span></div></div>`;
	}

	// ------------------------------------------------------------------ profile
	function opt(list, v) {
		return `<option value="">${t("select")}</option>` + list.map((x) => `<option value="${esc(x.value)}"${x.value === v ? " selected" : ""}>${esc(L(x))}</option>`).join("");
	}
	function renderProfile() {
		const p = S.profile, F = B.flags, ind = industry(), n = nat();
		const sec = ind ? ind.sectors.find((s) => s.value === p.industry_sector) : null;
		const field = (id, label, input, req) => `<div class="axg-field"><label for="${id}">${esc(label)}${req ? ' <span class="req">*</span>' : ""}</label>${input}</div>`;
		const txt = (id, key, ph, type) => `<input type="${type || "text"}" id="${id}" data-p="${key}" value="${esc(p[key] || "")}" placeholder="${esc(ph || "")}">`;
		let h = `<div class="axg-card axg-section"><div class="axg-section-title">${t("profile")}</div><div class="axg-muted axg-small">${t("not_scored")}</div>
			<div class="axg-grid2">
			${field("f-org", t("org"), txt("f-org", "organization_name"), 1)}
			${field("f-cname", t("contact_name"), txt("f-cname", "contact_name"))}
			${field("f-email", t("contact_email"), txt("f-email", "contact_email", "", "email"), F.require_email)}
			${field("f-phone", t("contact_phone"), txt("f-phone", "contact_phone", "", "tel"))}
			${field("f-ind", t("industry"), `<select id="f-ind" data-s="industry_type">${opt(B.industries, p.industry_type)}</select>`, 1)}
			${field("f-sec", t("sector"), `<select id="f-sec" data-s="industry_sector"${ind ? "" : " disabled"}>${ind ? opt(ind.sectors, p.industry_sector) : `<option>${t("select")}</option>`}</select>` +
				(sec && sec.is_other ? `<input type="text" style="margin-top:.5rem" data-p="sector_other" value="${esc(p.sector_other)}" placeholder="${esc(t("name_sector"))}">` : ""), 1)}
			${field("f-nat", t("nationality"), `<select id="f-nat" data-s="company_nationality">${opt(B.nationalities, p.company_nationality)}</select>`, 1)}
			${n && n.ask_cr ? field("f-cr", t("cr"), `<input type="text" id="f-cr" data-p="cr_number" inputmode="numeric" maxlength="10" value="${esc(p.cr_number || "")}" placeholder="${esc(t("cr_ph"))}">`) : ""}
			${F.ask_legal_form ? field("f-lf", t("legal"), `<select id="f-lf" data-s="legal_form">${opt(B.legal_forms, p.legal_form)}</select>`) : ""}
			${F.ask_entity_size ? field("f-es", t("size"), `<select id="f-es" data-s="entity_size">${opt(B.entity_sizes.map((e) => ({ ...e, label: e.label + (e.description ? " (" + e.description + ")" : "") })), p.entity_size)}</select>`) : ""}
			</div>`;
		if (F.ask_licenses) {
			const freeText = F.license_mode !== "Pick from License Types";
			const pickType = F.license_mode !== "Free Text";
			h += `<h3 style="margin:1.3rem 0 .4rem">${t("lic_h")}</h3>
			<div class="axg-field"><label>${esc(t("lic_q"))} <span class="req">*</span></label>
			${freeText ? `<input type="text" data-p="license_types_text" value="${esc(p.license_types_text || "")}" placeholder="${esc(t("lic_ph"))}"${p.license_na ? " disabled" : ""}>` : ""}
			<label class="axg-pill${p.license_na ? " sel" : ""}" style="display:inline-flex;gap:.4rem;margin-top:.5rem;align-items:center"><input type="checkbox" id="f-licna"${p.license_na ? " checked" : ""}> ${t("lic_na")}</label></div>`;
			if (!p.license_na) {
				h += `<div class="axg-field"><label>${esc(t("lic_rows"))}</label>`;
				p.licenses.forEach((l, i) => {
					const bad = l.is_valid === "Yes" && l.expiry_date && l.expiry_date < today();
					h += `<div class="axg-lic">
						${pickType ? `<select data-l="${i}" data-k="license_type"><option value="">${t("lic_type")}</option>${B.license_types.map((x) => `<option value="${esc(x.value)}"${x.value === l.license_type ? " selected" : ""}>${esc(L(x))}</option>`).join("")}</select>` : "<span></span>"}
						<input type="text" data-l="${i}" data-k="license_name" value="${esc(l.license_name || "")}" placeholder="${esc(t("lic_name"))}">
						<select data-l="${i}" data-k="is_valid"><option value="">${t("valid")}</option><option value="Yes"${l.is_valid === "Yes" ? " selected" : ""}>${t("yes")}</option><option value="No"${l.is_valid === "No" ? " selected" : ""}>${t("no")}</option></select>
						<input type="date" data-l="${i}" data-k="expiry_date" value="${esc(l.expiry_date || "")}">
						<button class="axg-btn axg-btn-outline axg-btn-sm" data-dellic="${i}">✕</button>
						${bad ? `<div class="axg-warn">${esc(t("lic_expired", { d: l.expiry_date }))}</div>` : ""}</div>`;
				});
				h += `<button class="axg-btn axg-btn-outline axg-btn-sm" data-addlic style="margin-top:.6rem">${t("add_lic")}</button></div>`;
			}
		}
		if (F.ask_regulators) {
			h += `<h3 style="margin:1.3rem 0 .4rem">${t("regs_h")}</h3><div id="axg-regs">${regsHtml()}</div>
				<div class="axg-field"><label>${t("other_reg")}</label><input type="text" data-p="other_regulator" value="${esc(p.other_regulator || "")}" placeholder="${esc(t("type_name"))}"></div>`;
		}
		h += `<div style="text-align:center;margin-top:1.5rem"><button class="axg-btn axg-btn-primary axg-btn-lg" data-act2="continue">${t("cont")}</button></div></div>`;
		$("#axg-main").innerHTML = h;
	}
	function regsHtml() {
		return S.regulators.map((r, i) => {
			const v = S.profile.regulators[r.regulator] || "";
			return `<div class="axg-row"><span>${esc(r.label || r.regulator)}<span class="axg-src">${esc(t("src_" + r.source))}</span></span><span class="axg-pills">${["Yes", "No"].map((o) =>
				`<span class="axg-pill${v === o ? " sel" : ""}" data-reg="${i}" data-v="${o}" role="radio" tabindex="0" aria-checked="${v === o}">${t(o.toLowerCase())}</span>`).join("")}</span></div>`;
		}).join("");
	}
	let regTimer = null;
	function refreshRegulators(alsoProfile) {
		clearTimeout(regTimer);
		regTimer = setTimeout(async () => {
			try {
				const r = await call("resolve", { profile: payload(), lang });
				S.regulators = r.regulators;
				const keep = new Set(r.regulators.map((x) => x.regulator));
				Object.keys(S.profile.regulators).forEach((k) => !keep.has(k) && delete S.profile.regulators[k]);
				if (alsoProfile) renderProfile(), bindView();
				else if ($("#axg-regs")) { $("#axg-regs").innerHTML = regsHtml(); bindRegs(); }
			} catch (e) { toast(e.message, "error"); }
		}, 150);
	}
	function bindRegs() {
		$$("[data-reg]").forEach((el) => {
			const fire = () => {
				const r = S.regulators[+el.dataset.reg];
				S.profile.regulators[r.regulator] = el.dataset.v;
				$$(`[data-reg="${el.dataset.reg}"]`).forEach((x) => { x.classList.toggle("sel", x === el); x.setAttribute("aria-checked", x === el); });
			};
			el.onclick = fire;
			el.onkeydown = (e) => (e.key === " " || e.key === "Enter") && (e.preventDefault(), fire());
		});
	}
	function validateProfile() {
		const p = S.profile, F = B.flags, ind = industry();
		const sec = ind ? ind.sectors.find((s) => s.value === p.industry_sector) : null;
		if (!p.organization_name.trim()) return t("v_org");
		if (F.require_email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(p.contact_email || "")) return t("v_email");
		if (!p.industry_type) return t("v_ind");
		if (!sec) return t("v_sec");
		if (sec.is_other && !(p.sector_other || "").trim()) return t("v_secname");
		if (!p.company_nationality) return t("v_nat");
		if (p.cr_number && !/^\d{10}$/.test(p.cr_number)) return t("v_cr");
		if (F.ask_licenses && !p.license_na) {
			const rows = p.licenses.filter((l) => l.license_type || l.license_name || l.is_valid || l.expiry_date);
			if (!(p.license_types_text || "").trim() && !rows.some((l) => l.license_type)) return t("v_lic");
			for (const l of rows) {
				const name = l.license_name || l.license_type;
				if (!name || !l.is_valid || !l.expiry_date) return t("v_licrow");
				if (l.is_valid === "Yes" && l.expiry_date < today()) return t("v_licvalid", { n: name });
			}
		}
		return "";
	}
	async function onContinue() {
		const e = validateProfile();
		if (e) return toast(e, "warning");
		const btn = $("[data-act2=continue]");
		if (btn) btn.disabled = true;
		try {
			await saveNow(false);
			show("questions");
		} catch (err) { toast(err.message, "error"); }
		finally { if (btn) btn.disabled = false; }
	}

	// ------------------------------------------------------------------ questions
	function qHtml(q) {
		const sel = S.answers[q.name] || "";
		const opts = q.options.concat(q.allow_na ? [{ value: "NA", label: t("na"), desc: t("na_desc"), na: true }] : []);
		return `<div class="axg-q" id="q-${esc(q.name)}" data-q="${esc(q.name)}">
			<span class="axg-q-label"><span class="axg-q-id">${esc(q.code)}</span> ${esc(q.text)}${q.conditional ? `<span class="axg-chip">${t("conditional")}</span>` : ""}${q.weight != null ? `<span class="axg-chip">${t("weight")} ${q.weight}</span>` : ""}</span>
			${q.guidance ? `<div class="axg-guidance">${esc(q.guidance)}</div>` : ""}
			<div class="axg-opts" role="radiogroup">${opts.map((o) =>
				`<label class="axg-opt${o.na ? " na" : ""}${sel === o.value ? " sel" : ""}"><input type="radio" name="${esc(q.name)}" value="${esc(o.value)}"${sel === o.value ? " checked" : ""}>
				<span class="axg-opt-top">${o.na ? "" : `<b>${esc(o.value)}</b>`}${esc(o.label)}</span><span class="axg-opt-desc">${esc(o.desc || "")}</span></label>`).join("")}</div></div>`;
	}
	function sectionHtml(s) {
		const qs = s.topics.flatMap((tp) => tp.questions);
		const d = qs.filter((q) => S.answers[q.name]).length;
		return `<div class="axg-card axg-section" data-sec="${esc(s.id)}"><div class="axg-section-title"><span>${esc(s.label)}</span><span class="axg-count" data-sc="${esc(s.id)}">${d}/${qs.length}</span></div>
			<div class="axg-muted axg-small" style="margin-bottom:.4rem">${qs.map((q) => esc(q.code)).join(" · ")}</div>
			${s.topics.map((tp) => (tp.label ? `<div class="axg-topic">${esc(tp.label)}<span class="axg-count">${tp.questions.length}</span></div>` : "") + tp.questions.map(qHtml).join("")).join("")}</div>`;
	}
	function renderQuestions() {
		const layout = B.theme.layout;
		let h = `<div class="axg-noprint" style="margin-bottom:.8rem"><button class="axg-btn axg-btn-outline axg-btn-sm" data-go="profile">✎ ${t("back_p")}</button></div>`;
		if (layout === "Wizard") {
			S.step = Math.min(S.step, S.sections.length - 1);
			h += `<div class="axg-steps">${S.sections.map((s, i) => {
				const qs = s.topics.flatMap((tp) => tp.questions);
				const done = qs.every((q) => S.answers[q.name]);
				return `<span class="axg-step${i === S.step ? " on" : ""}${done ? " done" : ""}" data-step="${i}">${esc(s.label)}</span>`;
			}).join("")}</div>`;
			h += sectionHtml(S.sections[S.step]);
			h += `<div style="display:flex;justify-content:space-between;gap:.6rem;flex-wrap:wrap">
				<button class="axg-btn axg-btn-outline" data-step="${S.step - 1}"${S.step === 0 ? " disabled" : ""}>${t("prev")}</button>
				${S.step < S.sections.length - 1 ? `<button class="axg-btn axg-btn-primary" data-step="${S.step + 1}">${t("next")}</button>` : `<button class="axg-btn axg-btn-accent axg-btn-lg" data-act2="submit">${t("submit")}</button>`}</div>`;
		} else {
			h += `<div class="${layout === "Compact" ? "axg-compact" : ""}">${S.sections.map(sectionHtml).join("")}</div>
				<div style="text-align:center;margin:2rem 0 .5rem"><button class="axg-btn axg-btn-accent axg-btn-lg" data-act2="submit">${t("submit")}</button></div>`;
		}
		$("#axg-main").innerHTML = h;
	}
	function counts() {
		S.sections.forEach((s) => {
			const qs = s.topics.flatMap((tp) => tp.questions);
			const el = $(`[data-sc="${CSS.escape(s.id)}"]`);
			if (el) el.textContent = qs.filter((q) => S.answers[q.name]).length + "/" + qs.length;
		});
	}
	function onAnswer(input) {
		S.answers[input.name] = input.value;
		S.rev++;
		const box = input.closest(".axg-q");
		box.classList.remove("axg-missing");
		$$(".axg-opt", box).forEach((x) => x.classList.toggle("sel", x.contains(input)));
		counts();
		head();
		scheduleSave();
	}

	// ------------------------------------------------------------------ save / submit
	function scheduleSave() {
		if (!S.id || S.status !== "Draft") return;
		clearTimeout(S.timer);
		S.timer = setTimeout(() => saveNow(false).catch((e) => toast(e.message, "error")), 1200);
	}
	function apply(st, takeAnswers) {
		S.id = st.id; S.k = st.k; S.status = st.status;
		S.sections = st.sections; S.regulators = st.regulators;
		if (takeAnswers) S.answers = Object.assign({}, st.answers);
		store.add(S.id, S.k, S.profile.organization_name);
		const u = new URL(location.href);
		u.searchParams.set("id", S.id); u.searchParams.set("k", S.k);
		history.replaceState(null, "", u.toString());
		renderSaved();
	}
	async function saveNow(announce) {
		clearTimeout(S.timer);
		const ss = $("#axg-savestate");
		if (ss) ss.textContent = "· " + t("saving");
		const sentRev = S.rev;
		const st = await call("save", { payload: payload(), id: S.id, k: S.k }, true);
		apply(st, sentRev === S.rev);
		if (ss) ss.textContent = "· " + t("saved");
		if (announce) toast(t("saved_toast"), "success", 2500);
		head();
		return sentRev;
	}
	async function onSubmit() {
		if (S.view !== "questions") { show("questions"); }
		// Blank answers are never allowed: every question needs A–D or N/A (the server enforces the same rule).
		const miss = allQ().filter((q) => !S.answers[q.name]);
		if (miss.length) {
			toast(t("missing", { n: miss.length, q: miss[0].code }), "warning");
			if (B.theme.layout === "Wizard") {
				S.step = S.sections.findIndex((s) => s.topics.some((tp) => tp.questions.some((q) => q.name === miss[0].name)));
				renderQuestions(); bindView();
			}
			miss.forEach((q) => { const el = document.getElementById("q-" + q.name); if (el) el.classList.add("axg-missing"); });
			const f = document.getElementById("q-" + miss[0].name);
			if (f) f.scrollIntoView({ behavior: "smooth", block: "center" });
			return;
		}
		try {
			const r = await call("submit", { id: S.id, k: S.k, payload: payload() }, true);
			S.status = "Submitted";
			showReport(r);
		} catch (e) { toast(e.message, "error"); }
	}
	function showReport(r) {
		if (r && r.hidden) { S.status = r.status; return show("thanks"); }
		S.report = r; S.status = r.status;
		show("report");
	}
	async function openReport() {
		try { showReport(await call("report", { id: S.id, k: S.k })); } catch (e) { toast(e.message, "error"); }
	}
	async function openSaved(id, k) {
		if (!id) return;
		try {
			const st = await call("load", { id, k });
			S.profile = Object.assign(blankProfile(), st.profile);
			if (!S.profile.licenses.length) S.profile.licenses = blankProfile().licenses;
			S.profile.regulators = st.profile.regulators || {};
			if (st.profile.language && st.profile.language !== lang && B.arabic) { lang = st.profile.language; setDir(); shell(); }
			S.rev++; apply(st, true);
			if (st.status === "Draft") show("questions");
			else await openReport();
		} catch (e) { toast(e.message, "error"); }
	}
	async function switchLang() {
		lang = lang === "ar" ? "en" : "ar";
		setDir();
		const view = S.view;
		shell();
		try {
			if (S.id && S.status === "Draft") await saveNow(false);
			else if (S.id) { const st = await call("load", { id: S.id, k: S.k }); S.sections = st.sections; S.regulators = st.regulators; }
			else if (view === "profile") { const r = await call("resolve", { profile: payload(), lang }); S.regulators = r.regulators; }
			if (view === "report") return openReport();
		} catch (e) { toast(e.message, "error"); }
		show(view);
	}

	// ------------------------------------------------------------------ report
	const pctBar = (pct, color) => `<div class="axg-sbar"><div style="width:${Math.max(0, Math.min(100, pct))}%;background:${esc(color || "var(--axg-primary)")}"></div></div>`;
	const card = (r) => `<div class="axg-scard"><div class="n">${esc(r.section_label ? r.section_label + " · " : "")}${esc(r.label)}</div>
		<div class="v"><span>${r.pct}%</span><span class="axg-muted axg-small">${r.answered}/${r.total}</span></div>${pctBar(r.pct, r.color)}
		<div class="axg-small axg-muted">${esc(r.band || "")}</div></div>`;
	function reportHtml(r) {
		if (!r) return "";
		const p = r.profile;
		const regs = p.regulators.map((x) => x.name + ": " + (x.response === "Yes" ? t("yes") : x.response === "No" ? t("no") : "—")).concat(p.other_regulator ? [p.other_regulator] : []);
		const icon = (B.bands.find((b) => b.key === r.band_key) || {}).icon || "";
		return `<div class="axg-result" style="--axg-band:${esc(r.band_color || "")}"><div>
				<div class="axg-muted axg-small" style="text-transform:uppercase;letter-spacing:.5px">${t("rep_title")}</div>
				<div class="lvl">${esc(icon)} ${esc(r.band || "")}</div>
				<div class="axg-keybox axg-noprint" title="${esc(t("keep_key"))}">🔑 <code>${esc(r.id)}</code> · <code>${esc(r.key)}</code></div>
				<div class="axg-muted axg-small" style="margin-top:.3rem">${esc(t("keep_key"))}</div></div>
			<div style="text-align:end"><div class="big">${r.overall}<small style="font-size:1.2rem;color:var(--axg-muted)">%</small></div>
				<div class="axg-muted axg-small">${t("points", { a: r.earned, p: r.possible })}</div>
				<div class="axg-muted axg-small">${t("q_answered", { d: r.answered, n: r.total })}${r.na ? " · " + t("na_count", { n: r.na }) : ""}</div></div></div>
			<div class="axg-card axg-small"><b>${esc(p.org)}</b> · ${esc(p.industry)} · ${esc(p.sector)} · ${esc(p.nationality)}${p.cr ? " · CR " + esc(p.cr) : ""}
				${p.legal_form ? " · " + esc(p.legal_form) : ""}${p.entity_size ? " · " + esc(p.entity_size) : ""}
				· ${p.license_na ? t("no_lic") : t("licenses_lbl") + ": " + esc(p.license_text || p.licenses.map((l) => l.name).join(", "))}
				<div class="axg-muted" style="margin-top:.3rem">${regs.map(esc).join(" | ")}</div></div>
			${!p.license_na && p.licenses.length ? `<h3>${t("lic_h")}</h3><div class="axg-table-wrap"><table><thead><tr><th>${t("license")}</th><th>${t("still_valid")}</th><th>${t("expiry")}</th></tr></thead><tbody>${p.licenses.map((l) =>
				`<tr><td>${esc(l.name)}</td><td>${l.valid === "Yes" ? t("yes") : l.valid === "No" ? t("no") : ""}</td><td>${esc(l.exp)}</td></tr>`).join("")}</tbody></table></div>` : ""}
			<h3>${t("sections")}</h3><div class="axg-cards">${r.sections.map(card).join("")}</div>
			${r.topics.length ? `<h3>${t("topics")}</h3><div class="axg-cards">${r.topics.map(card).join("")}</div>` : ""}
			${r.roadmap.length ? `<h3>${t("roadmap")}</h3><div class="axg-table-wrap"><table><thead><tr><th></th><th>${t("question")}</th><th>${t("current")}</th><th>${t("target")}</th></tr></thead><tbody>${r.roadmap.map((x) =>
				`<tr><td><b>${esc(x.code)}</b></td><td>${esc(x.text)}</td><td>${esc(x.current)}</td><td>${esc(x.target)}</td></tr>`).join("")}</tbody></table></div>` : ""}
			<div class="axg-table-wrap"><table><thead><tr><th>${t("question")}</th><th style="text-align:center">${t("selected")}</th><th style="text-align:center">${t("score")}</th><th>${t("category")}</th></tr></thead><tbody>${r.questions.map((q) =>
				`<tr><td><b>${esc(q.code)}</b></td><td style="text-align:center">${q.value === "NA" ? t("na") : esc(q.value || "—")}</td><td style="text-align:center">${q.score == null ? "—" : esc(q.score) + "/" + esc(q.max)}</td><td>${esc(q.category)}</td></tr>`).join("")}</tbody></table></div>
			${r.consultant_notes ? `<div class="axg-card"><b>${t("notes")}</b><div>${r.consultant_notes}</div></div>` : ""}
			<div class="axg-card axg-small"><b>${t("interp")}</b><ul style="margin:.3rem 0 0;padding-inline-start:1.2rem">${r.bands.map((b) =>
				`<li><b>${esc(b.label)} (${b.min}–${Math.round(b.max)}%)</b>: ${esc(b.text || "")}</li>`).join("")}</ul>
				<div class="axg-muted" style="margin-top:.5rem">${t("interp_note")}</div>${r.disclaimer ? `<div class="axg-muted" style="margin-top:.4rem">${esc(r.disclaimer)}</div>` : ""}</div>
			<div class="axg-noprint" style="margin-top:1rem;display:flex;gap:.6rem;flex-wrap:wrap">
				<button class="axg-btn axg-btn-primary" data-act2="print">${t("print")}</button>
				<a class="axg-btn axg-btn-outline" href="${API}pdf?id=${encodeURIComponent(r.id)}&k=${encodeURIComponent(r.key)}">${t("pdf")}</a></div>`;
	}
	function thanksHtml() {
		return `<div class="axg-hero"><h2>${t("thanks_h")}</h2><p>${t("thanks_p")}</p>
			<div class="axg-keybox">🔑 <code>${esc(S.id)}</code> · <code>${esc(S.k)}</code></div><p class="axg-muted axg-small" style="margin-top:.5rem">${t("keep_key")}</p></div>`;
	}

	// ------------------------------------------------------------------ bindings
	function bindView() {
		const m = $("#axg-main");
		m.onchange = null;
		$$("[data-go]", m).forEach((b) => (b.onclick = () => {
			if (b.dataset.go === "profile" && S.id && Object.keys(S.answers).length) toast(t("confirm_profile"), "warning", 6000);
			if (b.dataset.go === "profile" && !S.regulators.length) refreshRegulators(false);
			show(b.dataset.go);
		}));
		if (S.view === "profile") {
			$$("[data-p]", m).forEach((el) => (el.oninput = () => {
				let v = el.value;
				if (el.dataset.p === "cr_number") { v = v.replace(/\D/g, ""); el.value = v; }
				S.profile[el.dataset.p] = v;
				if (el.dataset.p === "organization_name") head();
			}));
			$$("[data-s]", m).forEach((el) => (el.onchange = () => {
				const key = el.dataset.s;
				S.profile[key] = el.value;
				if (key === "industry_type") { S.profile.industry_sector = ""; S.profile.sector_other = ""; S.profile.regulators = {}; }
				if (key === "company_nationality" && !(nat() || {}).ask_cr) S.profile.cr_number = "";
				refreshRegulators(true);
			}));
			const na = $("#f-licna", m);
			if (na) na.onchange = () => { S.profile.license_na = na.checked ? 1 : 0; renderProfile(); bindView(); };
			$$("[data-l]", m).forEach((el) => (el.onchange = el.oninput = (ev) => {
				S.profile.licenses[+el.dataset.l][el.dataset.k] = el.value;
				if (ev.type === "change" && el.dataset.k !== "license_name") { renderProfile(); bindView(); if (el.dataset.k === "license_type" && B.flags.regulators_drive) refreshRegulators(false); }
			}));
			$$("[data-dellic]", m).forEach((b) => (b.onclick = () => {
				S.profile.licenses.splice(+b.dataset.dellic, 1);
				if (!S.profile.licenses.length) S.profile.licenses = blankProfile().licenses;
				renderProfile(); bindView();
			}));
			const add = $("[data-addlic]", m);
			if (add) add.onclick = () => { S.profile.licenses.push({ license_type: "", license_name: "", is_valid: "", expiry_date: "" }); renderProfile(); bindView(); };
			bindRegs();
			const c = $("[data-act2=continue]", m);
			if (c) c.onclick = onContinue;
		}
		if (S.view === "questions") {
			m.onchange = (e) => { if (e.target.matches(".axg-opt input")) onAnswer(e.target); };
			$$("[data-step]", m).forEach((b) => (b.onclick = () => { S.step = +b.dataset.step; renderQuestions(); bindView(); window.scrollTo(0, 0); }));
			$$("[data-act2=submit]", m).forEach((b) => (b.onclick = onSubmit));
		}
		if (S.view === "report") {
			const p = $("[data-act2=print]", m);
			if (p) p.onclick = () => window.print();
		}
	}

	// ------------------------------------------------------------------ boot
	async function boot() {
		setDir();
		shell();
		show("welcome");
		try {
			const r = await call("resolve", { profile: { brand: B.brand.slug }, lang });
			S.globalCount = r.question_count;
			S.globalSections = r.sections.length;
			if (S.view === "welcome") show("welcome");
		} catch (e) { /* welcome still works */ }
		const u = new URL(location.href);
		if (u.searchParams.get("id")) openSaved(u.searchParams.get("id"), u.searchParams.get("k"));
	}
	boot();
})();
