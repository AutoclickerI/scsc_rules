from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

import markdown
from pypdf import PdfReader, PdfWriter

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
    ("policies_readme", "draft/policies/README.md", "draft/policies/README.pdf", "SCSC 운영방침 초안"),
    ("tf_form", "draft/forms/TF_installation_notice_template.md", "draft/forms/TF_installation_notice_template.pdf", "TF 설치 공고 서식"),
    ("controls", "draft/forms/operations_control_record_templates.md", "draft/forms/operations_control_record_templates.pdf", "SCSC 운영통제 기록 서식"),
    ("manual", "draft/forms/operations_control_manual.md", "draft/forms/operations_control_manual.pdf", "SCSC 운영통제 매뉴얼안"),
    ("revision", "revision_plan.md", "revision_plan.pdf", "SCSC 규정 채택 절차"),
    ("comparison", "web_rules_comparison.md", "web_rules_comparison.pdf", "국내 대학 동아리 규정 체계 비교"),
    ("changelog", "CHANGELOG.md", "CHANGELOG.pdf", "변경기록"),
    ("post_enactment", "규정_시행_후_필수_확인_매뉴얼.md", "규정_시행_후_필수_확인_매뉴얼.pdf", "SCSC 규정 시행 후 필수 확인 매뉴얼"),
]

DOCS = NORMATIVE + DERIVATIVES

HASHED_SOURCES = {
    "현행 회칙": "rules.md",
    "개정 회칙 초안": "draft/rules_draft.md",
    "현행 의사결정 세칙": "A_SCSC_임원진_의사결정과정_세칙.md",
    "개정 의사결정 세칙 초안": "draft/subrules/A_decision_rules_draft.md",
    "현행 지원금 세칙": "B_SCSC_지원금_운영방침_및_신청절차_세칙.md",
    "개정 지원금·재정집행 세칙 초안": "draft/subrules/B_funding_rules_draft.md",
    "세무단체 운영 세칙 초안": "draft/subrules/C_tax_entity_rules_draft.md",
    "징계 및 권리보호 세칙 초안": "draft/subrules/D_discipline_rights_rules_draft.md",
    "P1 회원 등록·OB 접근 운영방침 초안": "draft/policies/P1_membership_registration_OB_access_policy_draft.md",
    "P2 학기 회비 운영방침 초안": "draft/policies/P2_dues_collection_policy_draft.md",
    "P3 SIG·대회 운영방침 초안": "draft/policies/P3_SIG_competition_administration_policy_draft.md",
    "P4 개인정보 처리방침 초안": "draft/policies/P4_privacy_policy_draft.md",
    "운영통제 매뉴얼": "draft/forms/operations_control_manual.md",
    "운영통제 기록 서식": "draft/forms/operations_control_record_templates.md",
    "TF 설치 공고 서식": "draft/forms/TF_installation_notice_template.md",
    "규정 시행 후 필수 확인 매뉴얼": "규정_시행_후_필수_확인_매뉴얼.md",
    "규정 작성 기준과 참고 근거": "research/rule_authoring_practices.md",
}

CSS = r"""
@page { size: A4; margin: 13mm 14mm 14mm; }
* { box-sizing: border-box; }
html { font-family: "Noto Sans CJK KR", "Noto Sans KR", sans-serif; color: #15202b; }
body { margin: 0; font-size: 9pt; line-height: 1.47; word-break: keep-all; overflow-wrap: break-word; }
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
.changelog { font-size: 8.2pt; line-height: 1.36; }
.changelog h2 { margin-top: 5mm; }
.changelog table { font-size: 7.1pt; margin: 1.5mm 0 3mm; }
.comparison { font-size: 8pt; line-height: 1.34; }
.comparison h1 { margin-bottom: 5mm; }
.comparison h2 { margin: 5mm 0 2mm; }
.comparison p { margin-bottom: 1.8mm; }
.comparison ul, .comparison ol { margin: 1mm 0 2mm; }
.comparison li { margin-bottom: .5mm; }
.comparison table { margin: 1.5mm 0 2.5mm; font-size: 6.8pt; }
.rules, .P3 { font-size: 8.7pt; line-height: 1.43; }
.A, .B, .D, .P4 { font-size: 8.2pt; line-height: 1.38; }
.A { line-height: 1.32; }
.A h1 { margin-bottom: 5mm; }
.A h2 { margin: 4mm 0 1.6mm; }
.A p { margin-bottom: 1.2mm; }
.P1 { font-size: 8.2pt; line-height: 1.27; }
.P1 h1 { margin-bottom: 3.5mm; }
.P1 h2 { margin: 3mm 0 1.2mm; }
.P1 p { margin-bottom: .8mm; }
.controls { font-size: 8pt; line-height: 1.26; }
.controls h1 { margin-bottom: 4.5mm; }
.controls h2 { margin: 4mm 0 1.5mm; }
.controls h3 { margin: 2.5mm 0 1mm; }
.controls p { margin-bottom: 1mm; }
.controls ul, .controls ol { margin: .4mm 0 .9mm; }
.controls li { margin-bottom: .1mm; }
.manual { font-size: 8.4pt; line-height: 1.36; }
.manual h1 { margin-bottom: 5mm; }
.manual h2 { margin: 5mm 0 2mm; }
.manual p { margin-bottom: 1.8mm; }
.manual ul, .manual ol { margin: 1mm 0 2mm; }
.manual li { margin-bottom: .5mm; }
.post_enactment { font-size: 8pt; line-height: 1.34; }
.post_enactment h1 { font-size: 16pt; margin-bottom: 5mm; }
.post_enactment h2 { font-size: 11pt; margin: 5mm 0 2mm; }
.post_enactment p { margin-bottom: 1.8mm; }
.post_enactment ol, .post_enactment ul { margin: 1mm 0 2mm; }
.post_enactment li { margin-bottom: .6mm; }
.rules h3, .A h3, .B h3, .C h3, .D h3, .P1 h3, .P2 h3, .P3 h3, .P4 h3 {
  font-size: 1em; line-height: 1.25; margin: 1.8mm 0 .5mm;
}
.rules p, .A p, .B p, .C p, .D p, .P1 p, .P2 p, .P3 p, .P4 p {
  margin: 0 0 .45mm;
}
"""


def body_for(source: Path, label: str, key: str = "") -> str:
    rendered = markdown.markdown(
        source.read_text(encoding="utf-8"),
        extensions=["tables", "fenced_code", "sane_lists"],
    )
    rendered = re.sub(
        r'<a href="(?!(?:https?://|mailto:|#))[^\"]*">(.*?)</a>',
        r"\1",
        rendered,
        flags=re.S,
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
    canonical = pdf.with_suffix(".canonical.pdf")
    reader = PdfReader(pdf)
    writer = PdfWriter(clone_from=reader)
    writer.metadata = None
    writer.add_metadata(
        {
            "/Producer": "SCSC deterministic build",
            "/CreationDate": "D:20260814000000+09'00'",
            "/ModDate": "D:20260814000000+09'00'",
        }
    )
    writer.generate_file_identifiers()
    with canonical.open("wb") as handle:
        writer.write(handle)
    canonical.replace(pdf)


def update_changelog() -> None:
    path = ROOT / "CHANGELOG.md"
    text = path.read_text(encoding="utf-8")
    for label, rel in HASHED_SOURCES.items():
        digest = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        pattern = rf"(- \*\*{re.escape(label)}\*\* — `{re.escape(rel)}`; SHA-256: `)[0-9a-f]{{64}}(`)"
        text, count = re.subn(pattern, rf"\g<1>{digest}\2", text)
        if count != 1:
            raise RuntimeError(f"CHANGELOG hash entry not found: {label}")

    current = (ROOT / "draft/rules_draft.md").read_text(encoding="utf-8")
    nonspace = len(re.sub(r"\s+", "", current))
    lines = len(current.splitlines())
    text = re.sub(r"\| 원문 줄 \| 299줄 \| \d+줄 \|", f"| 원문 줄 | 299줄 | {lines}줄 |", text)
    text = re.sub(r"\| 공백 제외 문자 \| 10,865자 \| [\d,]+자 \|", f"| 공백 제외 문자 | 10,865자 | {nonspace:,}자 |", text)
    reduction = (10865 - nonspace) / 10865 * 100
    text = re.sub(r"\| 공백 제외 문자 감소 \|  \| [\d.]+% \|", f"| 공백 제외 문자 감소 |  | {reduction:.1f}% |", text)
    path.write_text(text, encoding="utf-8")


def render_one(key: str, source_rel: str, pdf_rel: str, label: str) -> None:
    source = ROOT / source_rel
    pdf = ROOT / pdf_rel
    html = OUT / f"{key}.html"
    html.write_text(html_page(label, body_for(source, label, key)), encoding="utf-8")
    print_pdf(html, pdf)
    print(f"{source_rel} -> {pdf_rel}")


update_changelog()

for spec in DOCS:
    render_one(*spec)

bundle_body = "".join(body_for(ROOT / source, label, key) for key, source, _, label in NORMATIVE)
bundle_html = OUT / "bundle.html"
bundle_html.write_text(html_page("SCSC 규정 개정안", bundle_body), encoding="utf-8")
print_pdf(bundle_html, ROOT / "draft/SCSC_rules_draft_bundle.pdf")
print("nine normative drafts -> draft/SCSC_rules_draft_bundle.pdf")
