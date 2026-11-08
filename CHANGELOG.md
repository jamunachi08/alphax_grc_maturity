# Changelog

## 1.1.0 — 2026-11-09
- New registration page `/grc-register` (branded, themed, EN/AR): organization, contact, work email, mobile, CR,
  industry, sector, nationality, city and PDPL consent. Email is verified with a 6-digit code.
- Passwordless sign-in by email code for returning respondents. Codes are hashed, expire (10 min), lock after
  5 wrong tries, resend wait 60 s, and every endpoint is rate limited. Staff accounts are refused (they use /login).
- New DocType GRC Maturity Registration with Approve / Reject / Disable; new website role GRC Maturity Respondent.
- Settings: "Allow Guests" replaced by Respondent Access — Registration Required (default), Registration + Approval,
  or Open. Optional work-email-only rule, required CR, required mobile, code timings.
- Portal: signed-in header with Sign out, new assessments pre-filled from the registration, "My assessments"
  from the server (any device), assessments linked to registration and user. Guests are redirected to register.
- Internal email on each new verified registration; approval and rejection emails to the respondent.

## 1.0.1 — 2026-11-09
- Blank answers are no longer allowed. Removed the "Blank Answers Score Zero" and "Block Submit Until All
  Mandatory Questions Are Answered" settings and the per-question Mandatory flag; replaced with a fixed rule.
- Every question in scope needs A–D, or N/A where allowed, before the assessment can leave Draft
  (Submitted, Reviewed or Closed). Enforced server-side on every non-Draft save, including desk edits,
  so a submitted answer cannot be cleared later. The error lists the missing question codes.
- Portal blocks submit on any blank answer, highlights every missing question and jumps to the first.

## 1.0.0 — 2026-11-08
- First release: question bank with global and conditional questions (7 dimensions), replace-question,
  layered weightage profiles with specificity fallback to Global, snapshot weights, pooled or section-average roll-up.
- White-label portal `/grc-assessment` with brands, 5 themes, light/dark/auto, Cards/Wizard/Compact layouts, EN/AR RTL.
- Report ID + access key, rate-limited saves, email with PDF, hide-score-until-reviewed.
- Seed: 46 questions, 23 industries, 278 sectors, 50 regulators, 4 nationalities from the v1.0 workbook.
- verify_tree.py structural guard.
