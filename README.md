# AlphaX GRC Maturity

**Publisher:** IRSAA Business Solution · **Brand:** AlphaX · **Contact:** grc.audit.assessment@irsaa.com
**Version:** 1.1.1 · **Frappe:** v15 and v16 · **Depends on:** frappe only (ERPNext optional)

A GRC maturity assessment for KSA organizations. Questions and weightage are defined
**globally** and can be specialised by **industry type, industry sector, company nationality,
KSA license, regulator, legal form and entity size**. Anything not defined for a specific
profile falls back to the global definition. The respondent portal is white-label, themeable
and bilingual (English / Arabic RTL).

## Install

```bash
bench get-app https://github.com/jamunachi08/alphax_grc_maturity
bench --site <site> install-app alphax_grc_maturity
```

On Frappe Cloud: push to the linked branch; `after_migrate` seeds missing masters automatically.

Then:
1. **GRC Maturity Settings** → check the default brand (IRSAA), scale, bands and roll-up.
2. **Email Account** → add an outgoing account for `grc.audit.assessment@irsaa.com` and pick it on the IRSAA brand.
3. Respondents register at **/grc-register** (email code), then take the assessment at **/grc-assessment** (or `/grc-assessment?b=<brand key>` for another brand).

## What is seeded

| Master | Count | Source |
|---|---|---|
| Questions (Global) | 46 | Questionnaire v1.0 workbook |
| Sample conditional questions | 7 (disabled) | AlphaX examples: financial, AML, healthcare, foreign ownership, cloud, listed JSC, AI (replaces Q31) |
| Sections / topics | 4 / 13 | Workbook, with Arabic labels |
| Industry types / sectors | 23 / 278 | Workbook Lists + Regulators + SectorRegulators |
| Regulators | 50 | Workbook + MISA, with Arabic names |
| Nationalities | 4 | Workbook Config §5 (CR prompt, MISA rule) |
| License types, legal forms, entity sizes | 17 / 10 / 4 | AlphaX |
| Weightage profiles | Global (enabled) + 4 samples (disabled) | AlphaX |
| Themes | 5 | AlphaX Navy (workbook look), IRSAA Emerald, Desert Sand, Midnight, Slate Minimal |
| Brand | IRSAA | grc.audit.assessment@irsaa.com |

The seeder only inserts what is missing. It never overwrites a record you edited.
Settings → Tools → **Re-run Seeder** restores anything deleted.

See `docs/DESIGN.md` for the data model, resolution rules and the question-variation analysis.

## Quality gate

```bash
python3 verify_tree.py
```
