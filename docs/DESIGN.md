# AlphaX GRC Maturity — Design

## 1. On what bases do GRC questions vary?

A maturity questionnaire is generic by design (governance, risk and compliance practices apply to every
organization). What changes from one organization to another is **which obligations exist** and **how much
each practice matters**. In KSA those differences come from seven drivers, all of which are now dimensions in
the app:

| Driver | Why questions change | Typical effect | Dimension |
|---|---|---|---|
| **Industry type** | Each industry has a primary regulator with its own rulebook (SAMA, CMA, MOH, CST, REGA…) | Add industry obligations; raise weight of compliance/risk sections | Industry Type |
| **Industry sector** | Within an industry the regulator and the risk differ (Banking vs Accounting; Cloud vs IT consulting) | Sector-specific questions; sector replaces industry regulator list | Industry Sector |
| **Company nationality / ownership** | Foreign ownership brings MISA licensing, local-content and Saudization obligations, sanctions and cross-border data topics | Add MISA questions; raise weight of regulatory mapping and third-party risk | Company Nationality |
| **KSA license held** | A license is the clearest evidence of a specific regulatory perimeter (SAMA license → SAMA CSF; CST license → cloud framework) | Add license-specific questions | License Type |
| **Regulator answered "Yes"** | Self-declared supervision | Optional: only when Settings → "Regulator answers can change questions" is on (off keeps the workbook rule) | Regulator |
| **Legal form** | Listed joint stock companies fall under the CMA Corporate Governance Regulations; sole proprietorships have no Board | Add listed-company disclosure questions; exclude Board questions for very small entities | Legal Form |
| **Entity size** | Proportionality: a 5-person firm is not expected to run an internal audit function | Exclude or down-weight heavy-structure questions | Entity Size |

Cross-cutting obligations that apply to everyone (ZATCA, NCA ECC, PDPL/SDAIA, HRSD, Ministry of Commerce)
stay in the **global** question set.

## 2. Data model

**Masters:** Regulator · Industry Type (+industry regulators) · Industry Sector (+own regulator list that
replaces the industry list) · Nationality (+extra regulators, CR prompt) · License Type · Legal Form · Entity Size.

**Question bank:** Section → Topic → Question. A question has options (A–D by default, points from the global
scale unless overridden), Allow N/A, Mandatory, Default Weight, Framework References, and:

* **Scope = Global** — asked of everyone, unless an *Exclude* rule matches.
* **Scope = Conditional** — asked only when its *Include* rules match.
* **Rules:** OR within a dimension, AND across dimensions; any matching Exclude removes the question.
* **Replaces Question:** a sector/industry version of a global question; when it applies, the global one is dropped.

**Weightage Profile:** Global (exactly one) or scoped by any mix of the seven dimensions. Lines set weights for
a **Section**, **Topic** or **Question**.

## 3. Resolution (questions and weights)

1. Build the context from the assessment profile.
2. Questions: Global questions minus excludes, plus Conditional questions whose includes match, minus replaced ones.
3. Matching profiles are ordered by **specificity** (Sector 64 · Industry 32 · License 16 · Regulator 8 ·
   Nationality 4 · Legal Form 2 · Size 1), then Priority, Global last.
4. Each weight is resolved **independently**: section weight, topic weight and question weight each come from
   the first profile in that order that defines it. Nothing defined → Global → 1 (or the question's default).

So a Banking profile that sets only Q43 still inherits section weights from the Financial Services profile and
everything else from Global. The **Preview Resolution** button on a profile shows the outcome for any context,
including which profile supplied each weight.

Weights are **snapshotted** on the assessment, so later edits to profiles do not silently change submitted reports.
"Rebuild Questionnaire" re-resolves a draft on demand.

## 4. Scoring

* Points per answer from Settings → Answer Scale (A 25 · B 50 · C 75 · D 100), overridable per option.
* N/A removes the question from possible points; blanks score zero (both switchable).
* Section/topic % = Σ(weight × points) ÷ Σ(weight × max points).
* Overall roll-up: **Pooled Points** (default, identical to the workbook when all weights are 1) or
  **Weighted Section Average**.
* Bands from Settings (Critical / Low / Medium / High / Leading), each with colour, icon and EN/AR text.
* Improvement roadmap: answers at or below the threshold (default A, B) list the next level as the target,
  or the option's own Recommendation if one is written.

## 5. Branding, themes and white label

* **Theme:** colours (light and dark), mode (Light / Dark / Auto), layout (Cards / Wizard / Compact), font,
  Arabic font, Google Font, corner radius, density, custom CSS.
* **Brand:** URL key (`/grc-assessment?b=key`), theme, logos, favicon, titles EN/AR, texts, disclaimer,
  sender email account, internal recipients, **White Label** (removes all AlphaX/IRSAA marks), hide score
  until reviewed, show weights.
* Colours are validated server-side before they reach the page; custom CSS is admin-only.

## 6. Respondent portal and security

* Guests allowed by default (Settings). Each assessment gets a report ID (GRC-YYYY-MM-DD-HHMM-NNNN) **plus a
  random access key**; both are needed to reopen it. The ID alone is guessable, so lookup by ID only is not offered.
* Saves are rate limited per IP; submitted assessments are locked.
* On submit: email to respondent (PDF attached unless "hide score" is on) and to internal recipients.

## 7. Desk

Workspace **GRC Maturity**; script report **GRC Maturity Summary** (filters, section averages chart, band
distribution); print format **GRC Maturity Report** (EN/AR, brand colour); roles **GRC Maturity Manager**
and **GRC Maturity Consultant**.
