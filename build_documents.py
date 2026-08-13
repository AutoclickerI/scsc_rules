from __future__ import annotations

import re
import subprocess
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
OUT = ROOT / ".build" / "pdf"
OUT.mkdir(parents=True, exist_ok=True)

NORMATIVE = [
    ("rules", "draft/rules_draft.md", "draft/rules_draft.pdf", "개정 회칙 초안"),
    ("A", "draft/subrules/A_decision_rules_draft.md", "draft/subrules/A_decision_rules_draft.pdf", "SCSC 의사결정 세칙안"),
    ("B", "draft/subrules/B_funding_rules_draft.md", "draft/subrules/B_funding_rules_draft.pdf", "SCSC 지원금 및 재정집행 세칙안"),
    ("C", "draft/subrules/C_tax_entity_rules_draft.md", "draft/subrules/C_tax_entity_rules_draft.pdf", "법인으로 보는 단체 SCSC 운영 세칙안"),
    ("D", "draft/subrules/D_discipline_rights_rules_draft.md", "draft/subrules/D_discipline_rights_rules_draft.pdf", "SCSC 징계 및 권리보호 세칙안"),
    ("P1", "draft/policies/P1_membership_registration_OB_access_policy_draft.md", "draft/policies/P1_membership_registration_OB_access_policy_draft.pdf", "회원 등록·OB 접근 운영방침안"),
    ("P2", "draft/policies/P2_dues_collection_policy_draft.md", "draft/policies/P2_dues_collection_policy_draft.pdf", "학기 회비 운영방침안"),
    ("P3", "draft/policies/P3_SIG_competition_administration_policy_draft.md", "draft/policies/P3_SIG_competition_administration_policy_draft.pdf", "SIG·대회 운영방침안"),
    ("P4", "draft/policies/P4_privacy_policy_draft.md", "draft/policies/P4_privacy_policy_draft.pdf", "개인정보 처리방침안"),
]

DERIVATIVES = [
    ("readme", "draft/README.md", "draft/README.pdf", "SCSC 규정 개정안 안내"),
    ("policies_readme", "draft/policies/README.md", "draft/policies/README.pdf", "SCSC 위임 운영방침 초안"),
    ("tf_form", "draft/forms/TF_installation_notice_template.md", "draft/forms/TF_installation_notice_template.pdf", "TF 설치 공고 서식"),
    ("controls", "draft/forms/operations_control_record_templates.md", "draft/forms/operations_control_record_templates.pdf", "SCSC 운영통제 기록 서식"),
    ("manual", "draft/forms/operations_control_manual.md", "draft/forms/operations_control_manual.pdf", "SCSC 운영통제 매뉴얼안"),
    ("revision", "revision_plan.md", "revision_plan.pdf", "SCSC 규정 개정·채택 계획"),
    ("comparison", "web_rules_comparison.md", "web_rules_comparison.pdf", "근거·비교 검토"),
    ("changelog", "CHANGELOG.md", "CHANGELOG.pdf", "변경기록"),
]

DOCS = NORMATIVE + DERIVATIVES

CSS = r"""
@page { size: A4; margin: 13mm 14mm 14mm; }
* { box-sizing: border-box; }
html { font-family: "Noto Sans CJK KR", "Noto Sans KR", sans-serif; color: #15202b; }
body { margin: 0; font-size: 9pt; line-height: 1.47; overflow-wrap: anywhere; }
.doc { page-break-after: always; }
.doc:last-child { page-break-after: auto; }
.label { color: #64748b; font-size: 7.7pt; letter-spacing: .04em; margin-bottom: 5mm; }
h1 { font-size: 18pt; line-height: 1.2; margin: 0 0 7mm; color: #0f3559; }
h2 { font-size: 12.5pt; line-height: 1.25; margin: 8mm 0 3mm; color: #154d75; break-after: avoid-page; }
h3 { font-size: 10.5pt; line-height: 1.3; margin: 5mm 0 2mm; color: #1d5f86; break-after: avoid-page; }
p { margin: 0 0 2.6mm; orphans: 3; widows: 3; }
ul, ol { margin: 1.8mm 0 3mm; padding-left: 5mm; }
li { margin: 0 0 1.1mm; }
blockquote { margin: 2mm 0 4mm; padding: 2.5mm 3.5mm; border-left: 1.2mm solid #5b8fb9; background: #f2f7fb; }
code { font-family: "Noto Sans Mono CJK KR", "Noto Sans Mono", monospace; font-size: .86em; overflow-wrap: anywhere; }
pre { white-space: pre-wrap; background: #f5f7fa; border: .2mm solid #d9e1e8; padding: 3mm; break-inside: avoid; }
table { width: 100%; border-collapse: collapse; margin: 2mm 0 4mm; font-size: 7.5pt; table-layout: fixed; }
th, td { border: .2mm solid #c8d3dc; padding: 1.2mm 1.4mm; vertical-align: top; overflow-wrap: anywhere; }
th { background: #eaf1f7; color: #133b5c; font-weight: 700; }
tr { break-inside: avoid; }
hr { border: 0; border-top: .3mm solid #ccd6de; margin: 5mm 0; }
a { color: inherit; text-decoration: none; }
.readme { font-size: 7.6pt; line-height: 1.3; }
.readme h1 { margin-bottom: 4mm; }
.readme h2 { margin: 4mm 0 1.5mm; }
.readme p { margin-bottom: 1.3mm; }
.readme ul { margin: 1mm 0 1.5mm; }
.readme li { margin-bottom: .3mm; }
.readme table { margin: 1mm 0 2mm; font-size: 6.7pt; }
.changelog { font-size: 8.7pt; line-height: 1.42; }
.changelog h2 { margin-top: 6mm; }
.comparison { font-size: 8pt; line-height: 1.34; }
.comparison h1 { margin-bottom: 5mm; }
.comparison h2 { margin: 5mm 0 2mm; }
.comparison p { margin-bottom: 1.8mm; }
.comparison ul, .comparison ol { margin: 1mm 0 2mm; }
.comparison li { margin-bottom: .5mm; }
.comparison table { margin: 1.5mm 0 2.5mm; font-size: 6.8pt; }
"""


def body_for(source: Path, label: str, key: str = "") -> str:
    rendered = markdown.markdown(
        source.read_text(encoding="utf-8"),
        extensions=["tables", "fenced_code", "sane_lists"],
    )
    return f'<section class="doc {key}"><div class="label">{label}</div>{rendered}</section>'


def html_page(title: str, body: str) -> str:
    return (
        '<!doctype html><html lang="ko"><head><meta charset="utf-8">'
        f"<title>{title}</title><style>{CSS}</style></head><body>{body}</body></html>"
    )


def print_pdf(html: Path, pdf: Path) -> None:
    subprocess.run(
        [
            "google-chrome",
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--print-to-pdf-no-header",
            f"--print-to-pdf={pdf}",
            html.resolve().as_uri(),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=180,
    )


def render_one(key: str, source_rel: str, pdf_rel: str, label: str) -> None:
    source = ROOT / source_rel
    pdf = ROOT / pdf_rel
    html = OUT / f"{key}.html"
    html.write_text(html_page(label, body_for(source, label, key)), encoding="utf-8")
    print_pdf(html, pdf)
    print(f"{source_rel} -> {pdf_rel}")


for spec in DOCS:
    render_one(*spec)

bundle_body = "".join(body_for(ROOT / source, label, key) for key, source, _, label in NORMATIVE)
bundle_html = OUT / "bundle.html"
bundle_html.write_text(html_page("SCSC 규정 개정안", bundle_body), encoding="utf-8")
print_pdf(bundle_html, ROOT / "draft/SCSC_rules_draft_bundle.pdf")
print("nine normative drafts -> draft/SCSC_rules_draft_bundle.pdf")
