from __future__ import annotations

import re
import subprocess
import hashlib
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
    "draft/policies/P3_SIG_competition_administration_policy_draft.pdf": ["SCSC SIG·대회 운영방침안", "제9조"],
    "draft/policies/P4_privacy_policy_draft.pdf": ["SCSC 개인정보 처리방침안", "제9조"],
    "draft/policies/README.pdf": ["SCSC 운영방침 초안", "P4 개인정보 처리"],
    "draft/README.pdf": ["SCSC 규정 개정안 안내", "개인정보 처리"],
    "draft/forms/TF_installation_notice_template.pdf": ["TF 설치 공고 서식", "최종보고 기한"],
    "draft/forms/operations_control_record_templates.pdf": ["SCSC 운영통제 기록 서식", "개인정보 처리업무 대장"],
    "draft/forms/operations_control_manual.pdf": ["SCSC 운영통제 매뉴얼안", "해산·청산"],
    "revision_plan.pdf": ["SCSC 규정 채택 절차", "총회는 회칙과 시행일을 의결한다"],
    "web_rules_comparison.pdf": ["국내 대학 동아리 규정 체계 비교", "조 제목 35개"],
    "CHANGELOG.pdf": ["SCSC 회칙 전면개정 변경기록", "층위별 이전 기록", "R-16"],
    "규정_시행_후_필수_확인_매뉴얼.pdf": ["SCSC 규정 시행 후 필수 확인 매뉴얼", "시행일부터 14일 안에"],
    "draft/SCSC_rules_draft_bundle.pdf": ["SCSC 회칙안", "SCSC 징계 및 권리보호 세칙안", "SCSC 개인정보 처리방침안"],
}

OUT = ROOT / ".build" / "pdf-text"
OUT.mkdir(parents=True, exist_ok=True)
issues: list[str] = []

SOURCE_PHRASES = {
    "draft/rules_draft.md": [
        "재적회원 수의 5분의 1을 올린 수와 15명 중 적은 수",
        "회장·부회장·회계·관리자 각 한 명",
        "회장은 다른 임원직을 겸할 수 없고",
        "임원회의는 현직 임원 전체로 구성한다",
        "모든 현직 임원은 회의에 참석하여 의견을 내고 표결할 수 있다",
        "총회는 회칙을, 임원회의는 세칙과 운영방침을 제정·개정·폐지한다",
        "예산·결산·회비·지출·계약, 시설·자산·계정, 세무단체와 대외 업무를 의결한다",
        "공고일 재적회원이 10명 미만이면 그 과반수로 한다",
        "그 전에 회원발의로 총회 재검토를 요구하면",
        "후원·조건부 외부 재원, 이해관계자 거래",
        "회계 단독 승인 한도를 넘는 지출, 신규·갱신 계약·계속 의무",
        "계약 체결·갱신, 지급·인도, 자산·권리·계정 이전",
        "회칙의 제정·개정·폐지와 제명은 총회 성립 정족수 이상의 회원이 참여하고 참여자 과반수의 찬성으로 의결한다",
        "해산은 재적회원의 2분의 1 이상이 참여하고 참여자 과반수의 찬성으로 의결한다",
        "임원직·회원권·총회 표결권이나 임원회의 표결권을 정지시키지 않는다",
        "접근 제한은 7일을 넘기거나 같은 사유로 반복할 수 없고",
        "확인위원회가 확인한 뒤 효력이 생긴다",
        "회칙의 제정·개정·폐지를 발의할 수 있다",
        "의결권자의 2분의 1 이상이 참여하고 참여자 과반수가 찬성하면 탄핵안은 가결된다",
        "총회가 함께 정한 사람이 직무를 대행한다",
    ],
    "draft/subrules/A_decision_rules_draft.md": [
        "의결권자는 「SCSC 회칙」 제16조제3항에 따라 확정하고",
        "일부 임원을 통지 대상에서 뺀 의결은 효력이 없다",
        "임원회의는 「SCSC 회칙」 제16조제2항의 참여·찬성 기준으로 의결한다",
        "회장이 공고하지 않으면 회원발의 대표가 공고한다",
        "접수·공고·명부 확인을 방해하거나 자료·채널 접근을 끊어도 절차는 중단되지 않으며",
        "추인 총회는 예비 채널에서 공고·표결할 수 있으며",
        "표결은 48시간 이상의 기간투표로 한다",
        "담당자 부재만으로 표결을 미룰 수 없다",
        "회장 궐위일부터 7일 안에 보궐선거 일정·담당자가 공고되지 않거나",
        "예비 채널에 같은 자료를 게시하고 그 시각에 제출된 것으로 본다",
        "회원발의 대표는 등록 업무와 탄핵안에 관여하지 않은 회원 한 명을 명부 검증자로 지정하여 공고한다",
        "본인의 동의를 받은 이해관계 없는 재적회원 중에서 대행자를 정한다",
        "활성화 요청을 24시간 동안 정당한 이유 없이 처리하지 않으면",
        "회장과 관리자가 각각 앞 문장의 사유 중 어느 하나에 해당하면 이해관계 없는 임원 두 명이 활성화한다",
        "회장과 탄핵안에 이해관계가 있는 임원은 접수·확인·명부 작성·총회 진행에 관여하지 않는다",
        "대표가 공식 채널에 요구 내용과 발의 인원만 게시한 때 회원발의가 성립한다",
        "회원발의 접수 수단과 회장·관리자 외의 대체 확인자를 상시 공고한다",
        "대표가 활성화한 예비 채널에 같은 내용을 게시한 때 회원발의가 성립하고",
        "확인자는 24시간 안에 접수 여부를 알리고 2일 안에 인원만 확인한다",
        "등록 처리 지연으로 발의권을 제한할 수 없다",
        "7일의 공고기간을 지켜 총회를 다시 공고한다",
        "총회는 요구일부터 21일 안에 원결정의 유지·변경·취소와 이미 집행한 사항의 처리 방법을 정한다",
        "기한 안에 총회가 성립하지 않거나 어느 안도 의결하지 못하면 재검토는 끝나고",
        "임명과 회원발의 재검토에는 「SCSC 회칙」 제10조제1항을 적용한다",
        "직무대행자는 지정 의결에서 회피한다",
        "당선 확정 후 7일과 그 기간에 제기된 이의의 처리가 끝날 때까지 보존한다",
        "총회는 공고일부터 14일 안에 결정한다",
        "후보 등록 준비·선거운동·공개 지지에 참여하지 않은 회원",
        "앞의 이의 처리 절차를 따른다",
        "회원발의가 분리 의결을 요구한 경우에도 같다",
        "제2항의 삭제 보류 사유가 있으면 폐기일을 연기한다",
        "안건을 요청한 운영진이나 회원 한 명이 공고한다",
        "신규·갱신 계약·계속 의무, 필수적이지 않은 개인정보 제공",
        "서로 직접 관련되지 않은 회원권·선거·징계·재정·기관 권한의 변경은 나누어 의결한다",
        "일반 안건은 기명으로 표결한다",
        "임원의 임명·해임 등 개인 인사 안건은 무기명으로 표결한다",
        "임원 한 명이 요청한 임원회의 안건도 무기명으로 표결한다",
    ],
    "draft/policies/P1_membership_registration_OB_access_policy_draft.md": [
        "재확인이 끝나지 않으면 명부에 남긴다",
        "특정 안건에 반대한다는 이유로 회원을 뺄 수 없다",
        "학기 중 한 차례 이상 추가 신청 기간을 두거나 상시 신청 방법을 운영한다",
        "이 요건을 확인하면 OB로 등록한다",
        "독자적인 계약·지출 승인은 위임할 수 없다",
    ],
    "draft/subrules/D_discipline_rights_rules_draft.md": [
        "회장·부회장을 거치지 않는 비공개 접수 경로",
        "보호조치로 총회의 발의·발언·표결권을 제한할 수 없다",
        "회원·OB 또는 본회 활동과 관련하여 회원·OB의 행위로 피해를 입었다고 주장하는 사람",
        "자료가 부족하다는 이유만으로 접수를 거부해서는 안 된다",
        "핵심 직무 전체를 제한하려면 7일 안에 총회의 승인을 받아야 한다",
        "확인에 참여한 사람은 같은 사건의 재검토에서 회피한다",
        "심사와 소명 절차를 생략할 수 없다",
        "관련 자료의 삭제를 보류하고",
    ],
    "draft/policies/P4_privacy_policy_draft.md": [
        "별표에 공개하지 않은 처리업무는 시작할 수 없다",
        "운영통제 기록 서식의 공개 항목에 따라 작성하여",
    ],
    "draft/forms/operations_control_record_templates.md": [
        "근거: 「SCSC 회칙」 제9조제4항",
    ],
    "draft/subrules/B_funding_rules_draft.md": [
        "세부 확인 항목은 운영통제 기록 서식으로 정한다",
        "학기 중 한 차례, 30일 동안 학기 누계 500,000원 한도",
        "세부 확인 항목은 운영통제 기록 서식으로, 청산 절차는 운영통제 매뉴얼로 정한다",
    ],
    "draft/subrules/C_tax_entity_rules_draft.md": [
        "SCSC 회칙과 권한 있는 회의체의 적법한 의결을 우선 적용한다",
        "결정에 관여하지 않은 사람이 내용을 확인한 뒤 이전한다",
        "직무 권한과 접근 권한을 즉시 회수한다",
        "임원회의는 명칭·소재지에 관한 조문을 함께 개정하고",
        "임원회의는 3영업일 안에 후임자를 선출한다",
    ],
}

for rel, phrases in SOURCE_PHRASES.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in text:
            issues.append(f"{rel}: missing governance invariant {phrase}")

stale_terms = [
    "불" + "신임",
    "특별" + "의결",
    "회원발의 " + "정족수",
    "3분의 " + "2",
    "2" + "/3",
    "삼분의 " + "이",
    "징계 사유" + "이다",
    "의결권 있는 현직 임원의 " + "절반 이상이 참여해야 하며",
]
curly_quotes = (chr(0x201C), chr(0x201D))

for path in (ROOT / "draft").rglob("*.md"):
    text = path.read_text(encoding="utf-8")
    for term in stale_terms:
        if term in text:
            issues.append(f"{path.relative_to(ROOT)}: stale term {term}")
    if any(mark in text for mark in curly_quotes):
        issues.append(f"{path.relative_to(ROOT)}: curly double quote")

changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
for label, rel, digest in re.findall(r"- \*\*(.+?)\*\* — `([^`]+)`; SHA-256: `([0-9a-f]{64})`", changelog):
    path = ROOT / rel
    if not path.exists():
        issues.append(f"CHANGELOG.md: missing hashed source {rel}")
    elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        issues.append(f"CHANGELOG.md: stale hash for {label}")

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
