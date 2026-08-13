from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PDFS = {
    "draft/rules_draft.pdf": ["SCSC 회칙안", "제34조"],
    "draft/subrules/A_decision_rules_draft.pdf": ["SCSC 의사결정 세칙안", "제18조"],
    "draft/subrules/B_funding_rules_draft.pdf": ["SCSC 지원금 및 재정집행 세칙안", "제38조"],
    "draft/subrules/C_tax_entity_rules_draft.pdf": ["법인으로 보는 단체 SCSC 운영 세칙안", "제21조"],
    "draft/subrules/D_discipline_rights_rules_draft.pdf": ["SCSC 징계 및 권리보호 세칙안", "제17조"],
    "draft/policies/P1_membership_registration_OB_access_policy_draft.pdf": ["SCSC 회원 등록 및 OB 접근 운영방침안", "제8조"],
    "draft/policies/P2_dues_collection_policy_draft.pdf": ["SCSC 학기 회비 운영방침안", "제7조"],
    "draft/policies/P3_SIG_competition_administration_policy_draft.pdf": ["SCSC SIG·대회 운영방침안", "제8조"],
    "draft/policies/P4_privacy_policy_draft.pdf": ["SCSC 개인정보 처리방침안", "제9조"],
    "draft/policies/README.pdf": ["SCSC 위임 운영방침 초안", "P4 개인정보 처리"],
    "draft/README.pdf": ["SCSC 규정 개정안 안내", "개인정보 처리"],
    "draft/forms/TF_installation_notice_template.pdf": ["TF 설치 공고 서식", "최종보고 기한"],
    "draft/forms/operations_control_record_templates.pdf": ["SCSC 운영통제 기록 서식", "개인정보 처리업무 대장"],
    "draft/forms/operations_control_manual.pdf": ["SCSC 운영통제 매뉴얼안", "해산·청산"],
    "revision_plan.pdf": ["SCSC 규정 개정·채택 계획", "2026년 8월 15일"],
    "web_rules_comparison.pdf": ["SCSC 규정 층위 비교·정비 보고서", "조 제목 35개"],
    "CHANGELOG.pdf": ["SCSC 회칙 전면개정 변경기록", "층위별 이전 기록", "R-16"],
    "draft/SCSC_rules_draft_bundle.pdf": ["SCSC 회칙안", "SCSC 징계 및 권리보호 세칙안", "SCSC 개인정보 처리방침안"],
}

OUT = ROOT / ".build" / "pdf-text"
OUT.mkdir(parents=True, exist_ok=True)
issues: list[str] = []

for rel, phrases in PDFS.items():
    path = ROOT / rel
    if not path.exists():
        issues.append(f"missing {rel}")
        continue
    info = subprocess.run(["pdfinfo", str(path)], check=True, text=True, capture_output=True).stdout
    pages_match = re.search(r"^Pages:\s+(\d+)", info, re.M)
    size_match = re.search(r"^Page size:\s+([^\n]+)", info, re.M)
    if pages_match is None or size_match is None:
        issues.append(f"{rel}: unreadable pdfinfo output")
        continue
    pages = int(pages_match.group(1))
    size = size_match.group(1)
    if "594" not in size or "841" not in size:
        issues.append(f"{rel}: non-A4 page size {size}")
    txt = OUT / (rel.replace("/", "__") + ".txt")
    subprocess.run(["pdftotext", "-layout", str(path), str(txt)], check=True)
    text = txt.read_text(encoding="utf-8", errors="replace")
    if len([page for page in text.split("\f") if page.strip()]) != pages:
        issues.append(f"{rel}: blank or textless page")
    for phrase in phrases:
        if phrase not in text:
            issues.append(f"{rel}: missing phrase {phrase}")
    if re.search(r"file://|localhost|about:blank", text, re.I):
        issues.append(f"{rel}: browser residue")

if issues:
    print("FAIL")
    for issue in issues:
        print(f"- {issue}")
    raise SystemExit(1)

print(f"PASS: {len(PDFS)} PDFs are A4, text-bearing, and contain the expected content.")
