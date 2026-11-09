/* AlphaX GRC Maturity · registration and email-code sign-in
 * Copyright (c) 2026, IRSAA Business Solution (AlphaX). Proprietary.
 */
(function () {
	"use strict";
	const B = window.AXG_BOOT;
	const root = document.getElementById("axg-app");
	if (!root) return;
	if (!B) {
		root.innerHTML = '<div class="axg-shell axg-center"><h2>The registration page could not start.</h2><p class="axg-muted">The page settings did not load. Ask the administrator to check GRC Maturity Settings and the Error Log.</p></div>';
		return;
	}
	const API = "/api/method/alphax_grc_maturity.api.registration.";
	const P = B.page || {};
	let lang = B.lang || "en";

	const I = {
		en: {
			register: "Register", signin: "Sign in", reg_title: "Register your organization", signin_title: "Sign in with your email",
			org: "Organization name", contact: "Your name", job: "Job title", email: "Work email", mobile: "Mobile", mobile_ph: "+966 5X XXX XXXX",
			cr: "Saudi CR number", cr_opt: "Saudi CR number (optional)", cr_ph: "10 digits", industry: "Industry type", sector: "Industry sector",
			name_sector: "Name the sector", nationality: "Company nationality", city: "City", select: "Select",
			send: "Register and send code", send_signin: "Send sign-in code", code_title: "Check your email",
			code_sent: "We sent a 6-digit code to {e}. It is valid for a few minutes.", verify: "Verify and continue",
			resend: "Resend code", resend_in: "Resend in {s}s", change: "Use a different email",
			pending_h: "Registration received", pending_p: "Your email is verified. A consultant will approve your registration and email you when you can start the assessment.",
			rejected_h: "Registration not active", rejected_p: "This registration is not active. Please contact us.",
			no_account: "New here?", have_account: "Already registered?", work_email_note: "Use your company email address.",
			v_org: "Enter the organization name.", v_contact: "Enter your name.", v_email: "Enter a valid work email.", v_mobile: "Enter your mobile number.",
			v_cr: "The CR number must be 10 digits.", v_ind: "Select the industry type.", v_sec: "Select the industry sector.",
			v_secname: "Name the sector.", v_nat: "Select the company nationality.", v_consent: "Please accept the consent statement to continue.",
			v_code: "Enter the 6-digit code.", exists: "This email is already registered. We switched you to Sign in.", lang_toggle: "العربية",
			signed_in: "Signed in. Opening the assessment…", error: "Something went wrong. Please try again.",
		},
		ar: {
			register: "تسجيل", signin: "تسجيل الدخول", reg_title: "سجّل منشأتك", signin_title: "سجّل الدخول ببريدك الإلكتروني",
			org: "اسم المنشأة", contact: "اسمك", job: "المسمى الوظيفي", email: "البريد الإلكتروني للعمل", mobile: "رقم الجوال", mobile_ph: "+966 5X XXX XXXX",
			cr: "رقم السجل التجاري", cr_opt: "رقم السجل التجاري (اختياري)", cr_ph: "10 أرقام", industry: "نوع النشاط", sector: "القطاع",
			name_sector: "حدد القطاع", nationality: "جنسية الشركة", city: "المدينة", select: "اختر",
			send: "تسجيل وإرسال الرمز", send_signin: "إرسال رمز الدخول", code_title: "تحقق من بريدك",
			code_sent: "أرسلنا رمزًا من 6 أرقام إلى {e}. الرمز صالح لبضع دقائق.", verify: "تحقق ومتابعة",
			resend: "إعادة إرسال الرمز", resend_in: "إعادة الإرسال بعد {s} ث", change: "استخدام بريد آخر",
			pending_h: "تم استلام التسجيل", pending_p: "تم التحقق من بريدك. سيعتمد أحد المستشارين تسجيلك ويرسل لك بريدًا عندما يمكنك بدء التقييم.",
			rejected_h: "التسجيل غير نشط", rejected_p: "هذا التسجيل غير نشط. يرجى التواصل معنا.",
			no_account: "جديد هنا؟", have_account: "مسجّل مسبقًا؟", work_email_note: "استخدم بريد شركتك.",
			v_org: "أدخل اسم المنشأة.", v_contact: "أدخل اسمك.", v_email: "أدخل بريد عمل صحيحًا.", v_mobile: "أدخل رقم الجوال.",
			v_cr: "يجب أن يتكون رقم السجل التجاري من 10 أرقام.", v_ind: "اختر نوع النشاط.", v_sec: "اختر القطاع.",
			v_secname: "حدد اسم القطاع.", v_nat: "اختر جنسية الشركة.", v_consent: "يرجى الموافقة على بيان الموافقة للمتابعة.",
			v_code: "أدخل الرمز المكون من 6 أرقام.", exists: "هذا البريد مسجّل مسبقًا. انتقلنا بك إلى تسجيل الدخول.", lang_toggle: "English",
			signed_in: "تم تسجيل الدخول. جارٍ فتح التقييم…", error: "حدث خطأ. حاول مرة أخرى.",
		},
	};
	const t = (k, v) => { let s = (I[lang] && I[lang][k]) || I.en[k] || k; if (v) Object.keys(v).forEach((x) => (s = s.split("{" + x + "}").join(v[x]))); return s; };
	const L = (o) => (o ? (lang === "ar" && o.label_ar ? o.label_ar : o.label) : "");
	const esc = (x) => String(x == null ? "" : x).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
	const $ = (s) => root.querySelector(s);

	const S = {
		view: P.state === "Pending Approval" ? "pending" : (P.state === "Rejected" || P.state === "Disabled") ? "rejected" : P.mode || "register",
		email: P.email || "", resendAt: 0, timer: null, busy: false,
		f: { organization_name: "", contact_name: "", job_title: "", email: P.email || "", mobile: "", cr_number: "", industry_type: "",
			industry_sector: "", sector_other: "", company_nationality: "", city: "", consent: false },
	};

	async function call(method, args) {
		const body = new URLSearchParams();
		Object.entries(args).forEach(([k, v]) => v != null && body.append(k, typeof v === "object" ? JSON.stringify(v) : v));
		const res = await fetch(API + method, { method: "POST", body, credentials: "same-origin",
			headers: { Accept: "application/json", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
				"X-Frappe-CSRF-Token": (window.frappe && window.frappe.csrf_token) || "" } });
		let data = {};
		try { data = await res.json(); } catch (e) { /* ignore */ }
		if (!res.ok || data.exc_type) {
			let msg = "";
			try { msg = JSON.parse(data._server_messages).map((m) => JSON.parse(m).message).join(" ").replace(/<[^>]+>/g, ""); } catch (e) { /* ignore */ }
			if (res.status === 429) msg = msg || "Too many requests. Please try again later.";
			throw new Error(msg || t("error"));
		}
		return data.message;
	}
	function toast(m, type) {
		const e = document.createElement("div");
		e.className = "axg-toast " + (type || "");
		e.textContent = m;
		$(".axg-toasts").appendChild(e);
		setTimeout(() => e.remove(), 5500);
	}
	const opt = (list, v) => `<option value="">${t("select")}</option>` + list.map((x) => `<option value="${esc(x.value)}"${x.value === v ? " selected" : ""}>${esc(L(x))}</option>`).join("");
	const industry = () => B.industries.find((i) => i.value === S.f.industry_type);

	function render() {
		root.setAttribute("dir", lang === "ar" ? "rtl" : "ltr");
		root.setAttribute("lang", lang);
		const br = B.brand;
		const title = (lang === "ar" && br.title_ar) || br.title || "GRC Maturity Assessment";
		const footer = (lang === "ar" && br.footer_ar) || br.footer || "";
		root.innerHTML = `<div class="axg-shell"><div class="axg-head">
			<div class="axg-brand">${br.logo ? `<img src="${esc(br.logo)}" alt="">` : ""}<div><h1 class="axg-title">${esc(title)}</h1></div></div>
			<div class="axg-tools">${B.arabic ? `<button class="axg-btn axg-btn-outline axg-btn-sm" data-a="lang">${t("lang_toggle")}</button>` : ""}</div></div>
			<div class="axg-narrow" id="axg-body">${body()}</div>
			<div class="axg-footer"><span>${esc(footer)}${br.support_email ? ` · <a href="mailto:${esc(br.support_email)}">${esc(br.support_email)}</a>` : ""}</span>${br.powered_by ? `<span>${esc(br.powered_by)}</span>` : ""}</div>
			</div><div class="axg-toasts"></div>`;
		bind();
	}

	function tabs() {
		return `<div class="axg-tabs" role="tablist"><button class="axg-tab${S.view === "register" ? " on" : ""}" data-a="register" role="tab">${t("register")}</button>
			<button class="axg-tab${S.view === "signin" ? " on" : ""}" data-a="signin" role="tab">${t("signin")}</button></div>`;
	}

	function body() {
		const R = B.reg || {};
		if (S.view === "pending") return `<div class="axg-hero"><h2>✅ ${t("pending_h")}</h2><p>${t("pending_p")}</p></div>`;
		if (S.view === "rejected") return `<div class="axg-hero"><h2>${t("rejected_h")}</h2><p>${t("rejected_p")}</p></div>`;
		if (S.view === "code") {
			return `<div class="axg-card axg-section axg-center"><h2 style="margin:0 0 .5rem">📧 ${t("code_title")}</h2>
				<p class="axg-muted">${esc(t("code_sent", { e: S.email }))}</p>
				<input class="axg-otp" id="r-code" inputmode="numeric" autocomplete="one-time-code" maxlength="6" placeholder="••••••" aria-label="code">
				<div style="margin-top:1rem"><button class="axg-btn axg-btn-primary axg-btn-lg" data-a="verify">${t("verify")}</button></div>
				<div style="margin-top:1rem;display:flex;gap:1.2rem;justify-content:center;flex-wrap:wrap">
					<button class="axg-link" data-a="resend" id="r-resend"></button><button class="axg-link" data-a="change">${t("change")}</button></div></div>`;
		}
		if (S.view === "signin") {
			return tabs() + `<div class="axg-card axg-section"><div class="axg-section-title">${t("signin_title")}</div>
				<div class="axg-field"><label for="r-semail">${t("email")}</label><input type="email" id="r-semail" autocomplete="email" value="${esc(S.email)}"></div>
				<div class="axg-center"><button class="axg-btn axg-btn-primary axg-btn-lg" data-a="send_signin">${t("send_signin")}</button></div></div>`;
		}
		const f = S.f, ind = industry();
		const sec = ind ? ind.sectors.find((s) => s.value === f.industry_sector) : null;
		const intro = (lang === "ar" && B.brand.reg_intro_ar) || B.brand.reg_intro || "";
		const consent = (lang === "ar" && B.brand.consent_ar) || B.brand.consent || "";
		const fld = (k, label, req, attrs, note) => `<div class="axg-field"><label for="r-${k}">${esc(label)}${req ? ' <span class="req">*</span>' : ""}</label>
			<input id="r-${k}" data-f="${k}" value="${esc(f[k])}" ${attrs || 'type="text"'}>${note ? `<div class="axg-muted axg-small">${esc(note)}</div>` : ""}</div>`;
		return tabs() + `<div class="axg-card axg-section"><div class="axg-section-title">${t("reg_title")}</div>
			${intro ? `<div class="axg-muted axg-small" style="margin:.3rem 0 .6rem">${intro}</div>` : ""}
			<div class="axg-grid2">
			${fld("organization_name", t("org"), 1, 'type="text" autocomplete="organization"')}
			${fld("contact_name", t("contact"), 1, 'type="text" autocomplete="name"')}
			${fld("email", t("email"), 1, 'type="email" autocomplete="email"', R.work_email ? t("work_email_note") : "")}
			${fld("mobile", t("mobile"), R.require_mobile, `type="tel" autocomplete="tel" placeholder="${esc(t("mobile_ph"))}"`)}
			${fld("job_title", t("job"), 0, 'type="text" autocomplete="organization-title"')}
			${fld("cr_number", R.require_cr ? t("cr") : t("cr_opt"), R.require_cr, `type="text" inputmode="numeric" maxlength="10" placeholder="${esc(t("cr_ph"))}"`)}
			<div class="axg-field"><label for="r-ind">${t("industry")} <span class="req">*</span></label><select id="r-ind" data-s="industry_type">${opt(B.industries, f.industry_type)}</select></div>
			<div class="axg-field"><label for="r-sec">${t("sector")} <span class="req">*</span></label><select id="r-sec" data-s="industry_sector"${ind ? "" : " disabled"}>${ind ? opt(ind.sectors, f.industry_sector) : `<option>${t("select")}</option>`}</select>
				${sec && sec.is_other ? `<input type="text" style="margin-top:.5rem" data-f="sector_other" value="${esc(f.sector_other)}" placeholder="${esc(t("name_sector"))}">` : ""}</div>
			<div class="axg-field"><label for="r-nat">${t("nationality")} <span class="req">*</span></label><select id="r-nat" data-s="company_nationality">${opt(B.nationalities, f.company_nationality)}</select></div>
			${fld("city", t("city"), 0, 'type="text" autocomplete="address-level2"')}
			</div>
			<label class="axg-consent"><input type="checkbox" id="r-consent"${f.consent ? " checked" : ""}><span>${esc(consent)}</span></label>
			<div class="axg-center" style="margin-top:1.3rem"><button class="axg-btn axg-btn-primary axg-btn-lg" data-a="send">${t("send")}</button></div></div>`;
	}

	function validate() {
		const f = S.f, R = B.reg || {}, ind = industry();
		const sec = ind ? ind.sectors.find((s) => s.value === f.industry_sector) : null;
		if (!f.organization_name.trim()) return t("v_org");
		if (!f.contact_name.trim()) return t("v_contact");
		if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.email.trim())) return t("v_email");
		if (R.require_mobile && !f.mobile.trim()) return t("v_mobile");
		if ((f.cr_number || R.require_cr) && !/^\d{10}$/.test(f.cr_number)) return t("v_cr");
		if (!f.industry_type) return t("v_ind");
		if (!sec) return t("v_sec");
		if (sec.is_other && !f.sector_other.trim()) return t("v_secname");
		if (!f.company_nationality) return t("v_nat");
		if (!f.consent) return t("v_consent");
		return "";
	}

	function tick() {
		const b = $("#r-resend");
		if (!b) return clearInterval(S.timer);
		const left = Math.ceil((S.resendAt - Date.now()) / 1000);
		b.disabled = left > 0;
		b.textContent = left > 0 ? t("resend_in", { s: left }) : t("resend");
	}
	function toCode(email) {
		S.email = email;
		S.view = "code";
		S.resendAt = Date.now() + (B.reg.resend_seconds || 60) * 1000;
		render();
		clearInterval(S.timer);
		S.timer = setInterval(tick, 1000);
		tick();
		$("#r-code").focus();
	}
	async function busy(btn, fn) {
		if (S.busy) return;
		S.busy = true;
		if (btn) btn.disabled = true;
		try { await fn(); } catch (e) { toast(e.message, "error"); } finally { S.busy = false; if (btn && document.body.contains(btn)) btn.disabled = false; }
	}

	function bind() {
		root.querySelectorAll("[data-f]").forEach((el) => (el.oninput = () => {
			let v = el.value;
			if (el.dataset.f === "cr_number") { v = v.replace(/\D/g, ""); el.value = v; }
			S.f[el.dataset.f] = v;
		}));
		root.querySelectorAll("[data-s]").forEach((el) => (el.onchange = () => {
			S.f[el.dataset.s] = el.value;
			if (el.dataset.s === "industry_type") { S.f.industry_sector = ""; S.f.sector_other = ""; }
			if (el.dataset.s !== "company_nationality") render();
		}));
		const c = $("#r-consent");
		if (c) c.onchange = () => (S.f.consent = c.checked);
		const code = $("#r-code");
		if (code) code.oninput = () => { code.value = code.value.replace(/\D/g, "").slice(0, 6); if (code.value.length === 6) $("[data-a=verify]").click(); };
		root.querySelectorAll("[data-a]").forEach((b) => (b.onclick = () => action(b.dataset.a, b)));
		root.querySelectorAll("input").forEach((i) => (i.onkeydown = (e) => {
			if (e.key !== "Enter") return;
			const main = $("[data-a=send],[data-a=send_signin],[data-a=verify]");
			if (main) { e.preventDefault(); main.click(); }
		}));
	}

	function action(a, btn) {
		if (a === "lang") { lang = lang === "ar" ? "en" : "ar"; render(); if (S.view === "code") { clearInterval(S.timer); S.timer = setInterval(tick, 1000); tick(); } return; }
		if (a === "register" || a === "signin") { S.view = a; return render(); }
		if (a === "change") { clearInterval(S.timer); S.view = "register"; return render(); }
		if (a === "send") {
			const e = validate();
			if (e) return toast(e, "warning");
			return busy(btn, async () => {
				const r = await call("register", { data: Object.assign({}, S.f, { language: lang, brand: B.brand.slug }) });
				if (r.state === "exists") { S.view = "signin"; S.email = S.f.email.trim(); render(); return toast(t("exists"), "warning"); }
				toCode(r.email);
			});
		}
		if (a === "send_signin") {
			const email = ($("#r-semail").value || "").trim();
			if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return toast(t("v_email"), "warning");
			return busy(btn, async () => { const r = await call("request_code", { email }); toCode(r.email); });
		}
		if (a === "resend") {
			return busy(btn, async () => { await call("request_code", { email: S.email }); toCode(S.email); });
		}
		if (a === "verify") {
			const code = ($("#r-code").value || "").trim();
			if (!/^\d{6}$/.test(code)) return toast(t("v_code"), "warning");
			return busy(btn, async () => {
				const r = await call("verify", { email: S.email, code, redirect_to: P.redirect });
				clearInterval(S.timer);
				if (r.state === "pending_approval") { S.view = "pending"; return render(); }
				toast(t("signed_in"), "success");
				window.location.href = r.redirect || P.redirect || "/grc-assessment";
			});
		}
	}

	render();
})();
