# SCSC internal preservation and relocation ledger

> **Status:** internal planning artifact. The files under `draft/` are treated as the current drafting baseline, not as adopted originals. This audit is read-only and recommends relocation without deleting operative outcomes.

## 1. Coverage and ledger contract

The companion CSV contains **475 provision-level rows**. Articles are split into numbered paragraphs where present; forms are split by functional section. Each row contains the current anchor, the full normalized operative proposition, recommended destination, required superior delegation, duplication/cross-reference risks, and scenarios to preserve.

**In scope:** all operative draft Markdown: the 44-article bylaws, three GA subrules, four delegated policies, and both existing form collections. `draft/README.md` and `draft/policies/README.md` were inspected as explanatory hierarchy notes but excluded from provision rows because they disclaim independent operative authority. PDFs and `.build/` text are derivatives, not separate normative sources.

### Baseline counts

| Source | Provision rows |
|---|---:|
| `draft/rules_draft.md` | 180 |
| `draft/subrules/A_decision_rules_draft.md` | 55 |
| `draft/subrules/B_funding_rules_draft.md` | 100 |
| `draft/subrules/C_tax_entity_rules_draft.md` | 50 |
| `draft/policies/P1_membership_registration_OB_access_policy_draft.md` | 20 |
| `draft/policies/P2_dues_collection_policy_draft.md` | 13 |
| `draft/policies/P3_SIG_competition_administration_policy_draft.md` | 16 |
| `draft/policies/P4_privacy_policy_draft.md` | 24 |
| `draft/forms/TF_installation_notice_template.md` | 5 |
| `draft/forms/operations_control_record_templates.md` | 12 |

### Recommended destination counts

| Code | Destination | Rows |
|---|---|---:|
| BYL | Compact bylaws (superior rule) | 109 |
| GOV | GA subrule G — meetings, decisions, elections and TFs | 76 |
| FIN | GA subrule F — finance, funding, assets and contracts | 111 |
| DISC | GA subrule D — conduct, protection, discipline and review | 32 |
| TAX | GA subrule T — tax-entity governance | 50 |
| MEM | Delegated policy M — registration, membership administration and OB access | 20 |
| DUES | Delegated policy U — semester dues administration | 13 |
| ACT | Delegated policy A — SIG, PIG, event and competition administration | 18 |
| PRIV | Delegated policy P — privacy, security and retention | 28 |
| MAN | Operations manual — accounts, handover, safety and routine controls | 1 |
| FORM | Form/register/notice/administrative record | 17 |

## 2. Recommended target hierarchy

1. **Compact bylaws:** identity/purpose; hierarchy and publication; membership and core rights/duties; standing bodies and offices; reserved GA matters and decisive thresholds; election entitlement/result rule; TF authorization and nondelegable matters; finance/debt/asset/contract guardrails; activity rights and non-coercion; conduct categories, available sanctions, due-process/review entitlement; amendment, interpretation, dissolution and transition.
2. **GA subrule G — meetings, decisions, elections and TFs:** notice, agenda, rosters, participation, amendments, period voting, counting, secrecy, conflicts, election administration/challenges, emergency action/ratification, TF notices/reporting and decision-record retention.
3. **GA subrule F — finance, funding, assets and contracts:** budget execution, approval bands, payment separation/reconciliation, evidence/settlement, recovery, support classifications and fixed amounts, project/service controls, asset disposition and independent semester-end review.
4. **GA subrule D — conduct, protection, discipline and review (new, required):** objective misconduct/materiality, intake fallbacks, confidentiality, anti-retaliation, interim measures, neutral investigator, deadlines, reasoned decision, sanction routing and independent reconsideration. A mere manual is insufficient because these provisions burden rights and authorize sanctions.
5. **GA subrule T — tax-entity governance:** retain as a distinct instrument while the tax entity exists; it supports external filings and must not become a mutable executive policy.
6. **Delegated policies M/U/A/P:** registration/OB; dues administration; SIG/PIG/event/competition administration; privacy/security/retention. Each must state adopter, exact superior authority, scope, validity limits, publication/effective-date/history requirements.
7. **Operations manual:** mutable implementation for account recovery tests, handover, safety-plan preparation, routine reconciliation, repositories/services and incident playbooks. It may not be the sole home of rights, sanctions, thresholds, approval authority or monetary limits.
8. **Forms/registers/notices:** keep the two existing collections; split the large control-template collection into named records if usability benefits. Forms capture evidence only and must cite the controlling provision.

## 3. Highest-risk relocations and mandatory preservation tests

| Scenario | Non-negotiable outcome to preserve | Primary homes |
|---|---|---|
| All officers unavailable | Member-triggered reconstruction remains possible; no circular dependence on an absent officer. | Bylaws + G |
| Official channel compromised | Independent fallback activation, notice, seven-day ratification, record synchronization, unchanged notice/quorum rules. | G + incident record |
| Emergency action | Only minimum action; competent actor or stated fallback; notice attempts; 72-hour ratification; unwind/recovery if not ratified; no emergency amendments/elections/discipline/dissolution. | G |
| Election | Fixed electorate, direct secret vote, independent manager/verifier, disagreement fallback, deadlines, recount/revote/invalidation and post-certification special challenge. | Bylaws + G + record |
| Discipline | Objective/material misconduct; correction for simple mistake; protected intake even when president/vice-president conflicted; neutral review; response opportunity; confidentiality; anti-retaliation; interim-measure expiry/review; reasoned final notice; reconsideration; disputed damages not self-collected. | Bylaws + D + protected record |
| Finance | Approved-budget-only spending, no debt/guarantee/collateral, conflict exclusion, two-person verification or prompt reconciliation for single operator, evidence/settlement, recovery efforts, independent semester-end check. | Bylaws + F + records |
| Projects/accounts | External-condition exception, no implied copyright transfer, agreed licences, retained organizational licence on transfer, organization-controlled recovery, semester recovery test, handover/revocation. | Bylaws + F + manual/register |
| Privacy/security | Minimization, purpose/authority inventory, access review, rights response, withheld-record reason/review date, incident containment/evidence/notice/recovery, deletion schedule. | Bylaws + P + records |
| High-risk event | Responsible person, transport/emergency/accessibility plan, school/insurance check, cancellation criteria, voluntary minimal sensitive data and deletion. | Bylaws + A/manual + safety record |
| Tax entity | Tax unit has no independent member governance; representative cannot approve spending/contracts; filing deadlines, restricted access, succession, termination/replacement and no member distribution. | Bylaws + T + administrative ledger |
| Dissolution | GA sets liquidation; conflict/incapacity fallback; liabilities/restricted property/data addressed; no member distribution; recipient fallback and public final report. | Bylaws + liquidation record |

## 4. Duplication and cross-reference controls

- Establish one authoritative home for every **denominator, threshold, deadline, retention period, monetary amount and sanction**. Other instruments should cross-reference rather than restate.
- Keep bylaw reserved matters and final decision bodies above all procedural instruments. A policy or manual cannot supply missing delegation.
- Separate general voting rules from discipline/election exceptions; blanket incorporation risks exposing identities or applying ordinary correction rules to protected proceedings.
- Preserve external-condition exceptions for grants/contracts/licences and do not let general asset language override them.
- Keep privacy-policy retention rules synchronized with G/F/D/T records; event, financial and disciplinary forms must not silently extend collection or retention.
- Revalidate every current article citation after compaction. The existing forms contain many brittle numbered references and must be updated only after the target structure stabilizes.
- Keep transition provisions explicitly labeled as adoption-dependent. The draft effective date and statements purporting to repeal prior rules are not evidence of adoption.

## 5. Document recommendations

- **Yes: create a disciplinary GA subrule, not only a manual.** It should absorb current bylaw Articles 37–39 procedural detail and the discipline-retention clause in decision subrule Article 14(3), while compact bylaws retain protected rights, objective grounds/materiality, sanction menu, final decision allocation, notice/response and one independent review right.
- Retain the **tax-entity subrule** as a dedicated member-enacted instrument due to external/administrative significance.
- Consider renaming the finance instrument to include **finance, funding, assets and contracts**, since its operative scope is much wider than “support.”
- Keep privacy as a delegated policy only if compact bylaws expressly require it and preserve core member rights/security duties; mutable processing schedules belong in its annex/register.
- Split the operations-control template into separate controlled forms/registers, but preserve its disclaimer and ensure each field traces to an operative rule.

## 6. Artifacts and baseline fingerprints

- Machine ledger: `/home/jihoon/SCSC_preservation_relocation_ledger.csv`
- This report: `/home/jihoon/SCSC_preservation_relocation_ledger.md`

| Baseline source | SHA-256 |
|---|---|
| `draft/rules_draft.md` | `51ceb31e3b915b424463f98b36c2b2dc774ca8f44c1abfe09247d2ba6f56b6de` |
| `draft/subrules/A_decision_rules_draft.md` | `80ab7086203f90f7670fcb56852971a0ef12680d589249bd033a5307868ae421` |
| `draft/subrules/B_funding_rules_draft.md` | `63862fb460ace665dedd00822db6f509e6a569de4271531c11d2dfd38370ab14` |
| `draft/subrules/C_tax_entity_rules_draft.md` | `96f2310ef49b5af774632cc848bf10fb0d89b5c380b1273e9e48abdc3377d6e9` |
| `draft/policies/P1_membership_registration_OB_access_policy_draft.md` | `f1f765e04ca3d0348cbab4b5abcf2657a768768f011361d05b334e6fefb9a2da` |
| `draft/policies/P2_dues_collection_policy_draft.md` | `2aa869387d39b67641df5d8953be715b5179fc0ce3b959923e210295ad3ece9d` |
| `draft/policies/P3_SIG_competition_administration_policy_draft.md` | `768001955d2eaf867f3d732e7bb691d7c676e704f012dd76585b9db274fad0ad` |
| `draft/policies/P4_privacy_policy_draft.md` | `51210d36f7c385fa7fc62472a20a56d489b0326afc7e25846f68fb7be4d12d22` |
| `draft/forms/TF_installation_notice_template.md` | `2db09a4e4f5131f64ecb346050b7a10232de19409ca7520c67e17f4ad1efd4d6` |
| `draft/forms/operations_control_record_templates.md` | `fb2096afabef2b3baf751d532d7e930326c36c7aa8caf46b03fe250d9c750448` |

## 7. Acceptance gate for any later rewrite

A compact candidate should not be accepted until every CSV row is mapped to a live target or expressly marked as a non-operative transition/note; all target delegations exist; all cross-references resolve; and the preservation scenarios above produce the same actor, trigger, threshold, exception, deadline, record, review and closure outcome. Compare against these exact draft hashes, while separately verifying any actually adopted originals before claiming legal continuity.
