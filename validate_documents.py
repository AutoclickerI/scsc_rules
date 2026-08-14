from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

import markdown
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
OUT = ROOT / ".build" / "pdf-text"
OUT.mkdir(parents=True, exist_ok=True)

PROTECTED = {
    "rules.md": "8a371b785f1c4bd9d8e3526f68eb5357c7896dba570e624d2b5ae6ecab45e00b",
    "A_SCSC_임원진_의사결정과정_세칙.md": "1da061dfe2e8a9cbb752f01a9e15af18b5e40911e989181f84642d0a181503c8",
    "B_SCSC_지원금_운영방침_및_신청절차_세칙.md": "14a689b7cf2528829f16100f2eb5f0e84350bd2983b0074ac00188cc20f2e25d",
}

DOCUMENTS = {
    "SCSC 회칙": "draft/rules_draft.md",
    "SCSC 의사결정 세칙": "draft/subrules/A_decision_rules_draft.md",
    "SCSC 지원금 및 재정집행 세칙": "draft/subrules/B_funding_rules_draft.md",
    "법인으로 보는 단체 SCSC 운영 세칙": "draft/subrules/C_tax_entity_rules_draft.md",
    "SCSC 징계 및 권리보호 세칙": "draft/subrules/D_discipline_rights_rules_draft.md",
    "SCSC 회원 등록 및 OB 접근 운영방침": "draft/policies/P1_membership_registration_OB_access_policy_draft.md",
    "SCSC 학기 회비 운영방침": "draft/policies/P2_dues_collection_policy_draft.md",
    "SCSC SIG·대회 운영방침": "draft/policies/P3_SIG_competition_administration_policy_draft.md",
    "SCSC 개인정보 처리방침": "draft/policies/P4_privacy_policy_draft.md",
}

PDFS = {
    "draft/rules_draft.pdf": ["SCSC 회칙안", "제34조", "명시되지 않은 운영 권한도 임원회의에 속한다"],
    "draft/subrules/A_decision_rules_draft.pdf": ["SCSC 의사결정 세칙안", "제18조", "의결 기준은"],
    "draft/subrules/B_funding_rules_draft.pdf": ["SCSC 지원금 및 재정집행 세칙안", "제38조", "300,000원"],
    "draft/subrules/C_tax_entity_rules_draft.pdf": ["법인으로 보는 단체 SCSC 운영 세칙안", "제21조"],
    "draft/subrules/D_discipline_rights_rules_draft.pdf": ["SCSC 징계 및 권리보호 세칙안", "제17조"],
    "draft/policies/P1_membership_registration_OB_access_policy_draft.pdf": ["SCSC 회원 등록 및 OB 접근 운영방침안", "제8조"],
    "draft/policies/P2_dues_collection_policy_draft.pdf": ["SCSC 학기 회비 운영방침안", "제7조"],
    "draft/policies/P3_SIG_competition_administration_policy_draft.pdf": ["SCSC SIG·대회 운영방침안", "제9조"],
    "draft/policies/P4_privacy_policy_draft.pdf": ["SCSC 개인정보 처리방침안", "제9조"],
    "draft/policies/README.pdf": ["SCSC 운영방침 초안", "P4 개인정보 처리"],
    "draft/README.pdf": ["SCSC 규정 개정안 안내", "그 밖의 모든 운영 사항"],
    "draft/forms/TF_installation_notice_template.pdf": ["TF 설치 공고 서식", "최종보고 기한"],
    "draft/forms/operations_control_record_templates.pdf": ["SCSC 운영통제 기록 서식", "해산·청산"],
    "draft/forms/operations_control_manual.pdf": ["SCSC 운영통제 매뉴얼안", "해산·청산"],
    "revision_plan.pdf": ["SCSC 규정 채택 절차", "총회는 회칙과 시행일을 의결한다"],
    "web_rules_comparison.pdf": ["국내 대학 동아리 규정 체계 비교", "조 제목 35개"],
    "CHANGELOG.pdf": ["SCSC 회칙 전면개정 변경기록", "공백 제외 문자 감소"],
    "규정_시행_후_필수_확인_매뉴얼.pdf": ["SCSC 규정 시행 후 필수 확인 매뉴얼", "시행일부터 14일 안에"],
    "draft/SCSC_rules_draft_bundle.pdf": ["SCSC 회칙안", "SCSC 징계 및 권리보호 세칙안", "SCSC 개인정보 처리방침안"],
}

INVARIANTS = {
    "draft/rules_draft.md": [
        '"회원발의"란 회원 15명이 공동으로 요구하거나 발의하는 것을 말한다',
        "총회 공고 시각의 의결권자 수를 기준으로 그 10분의 1에 5명을 더하고 소수점 이하는 올린 수",
        "회장·부회장·회계·관리자 각 한 명",
        "회비 납부를 해당 학기의 등록 요건으로 공고한 경우",
        "부회장·회계·관리자를 해임할 수 있다",
        "후보자를 두 차례 정하지 못하면 총회가 임명한다",
        "제15조제1항을 제외한 본회의 모든 운영 사항을 결정하고 집행한다",
        "명시되지 않은 운영 권한도 임원회의에 속한다",
        "임원 두 명 이상이 참여하며 두 명 이상이 찬성하고 찬성표가 반대표보다 많으면 의결한다",
        "복수 후보는 한 명을 선택하여 투표하고",
        "득표 순위 상위 두 명을 대상으로 결선투표한다",
        "그 밖의 임원회의 결정도 총회에 재검토하도록 요구할 수 있다",
        "이해관계자 거래, 중요 자산·권리의 처분",
        "회원 권리 제한, 이해관계자 거래와 중요 자산·권리의 처분은 총회가 원결정의 유지를 의결하지 않으면 효력을 잃는다",
        "회칙의 제정·개정·폐지, 회장 선출·탄핵, 회원 제명과 본회의 해산",
        "총회의 발의·발언·표결권과 회장 선거권",
        "총회의 발의·발언·표결권과 임원회의 표결권을 제한할 수 없다",
        "같은 행위나 위험에 대한 연속·관련 제한은 기간을 합산한다",
        "재적회원 과반수가 참여하고 참여자의 2분의 1 이상이 찬성하면 해산을 의결한다",
        "수령단체를 직접·간접으로 지배하거나 이전·재이전으로 중대한 개인적 이익을 얻어서는 안 된다",
        "임기는 2026년 12월 31일에 끝난다",
        "이후의 등록·탈퇴·임원 인사나 직무 변경은 해당 탄핵안에 영향을 주지 않는다",
        "총회 성립 정족수는 제2항의 의결권자를 기준으로 계산한다",
    ],
    "draft/subrules/A_decision_rules_draft.md": [
        "대한민국 표준시와 공식 채널의 기록 시각을 기준",
        "정당한 이유 없이 24시간 안에 처리하지 않으면",
        "임원이 아닌 대체 확인자 두 명 이상",
        "각 공동발의자의 의사를 직접 확인하고",
        "심의·표결·집행에 참여하려는 사람 중",
        "심의·표결·집행에서 회피한다",
        "고위험 행사 안전계획에도 같은 기준을 적용한다",
        "결정의 효력과 회원발의 재검토는 「SCSC 회칙」 제16조제3항·제4항에 따른다",
        "표결 기간에는 이 세칙 제7조제1항을 적용한다",
        "요청일부터 14일 안에 제공을 마친다",
        "총회 기간투표는 48시간 이상",
        "긴급결정으로 규정을 바꾸거나 선거·탄핵·징계·제명·해산을 결정하거나",
        "72시간 안에 추인하지 않으면",
        "공식 채널 밖의 행위나 합의를 추인할 때",
    ],
    "draft/subrules/B_funding_rules_draft.md": [
        "회계의 단독 승인 한도는 건별 300,000원",
        "30일 동안 학기 누계 500,000원",
        "컴퓨터 관련 SIG는 학기당 50,000원",
        "실제 참석 회원 수에 10,000원을 곱한 금액",
        "기초 SIG당 150,000원",
        "실제 참가 회원 수에 20,000원을 곱한 금액",
        "신청 분할을 금지한다",
        "선정에 관여하지 않은 사람이 공개된 근거와 동의를 다시 확인한다",
        "재산의 재이전 금지 등 회칙의 제한을 지키겠다는 서면 동의",
    ],
    "draft/subrules/D_discipline_rights_rules_draft.md": [
        "자료가 부족하다는 이유만으로 접수를 거부할 수 없다",
        "발의·발언·표결권과 임원회의 표결권은 제한할 수 없다",
        "원결정에 관여하지 않은",
        "새 총회가 유지·변경·취소를 결정한다",
        "이 요구에는 회원발의가 필요하지 않다",
        "독립 확인을 거치지 않은 제재의 비례성",
        "당사자는 언제든 축소·해제를 요청할 수 있다",
    ],
    "draft/policies/P1_membership_registration_OB_access_policy_draft.md": [
        "공고한 명부 접수 마감까지 보완을 마친 신청을 모두 처리한 뒤",
    ],
    "draft/policies/P2_dues_collection_policy_draft.md": [
        "회비 납부를 해당 학기 등록의 요건으로 정할 수 있다",
        "등록이나 총회·선거가 공고된 뒤 소급하여 바꿀 수 없다",
    ],
    "draft/policies/P4_privacy_policy_draft.md": [
        "외부 신고의무와 관계없이 영향받은 사람에게 지체 없이",
        "통지를 미루면 사유와 재검토일을 기록한다",
    ],
}

issues: list[str] = []

for rel, expected in PROTECTED.items():
    actual = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
    if actual != expected:
        issues.append(f"{rel}: protected original changed ({actual})")

editable_markdown = [path for path in ROOT.rglob("*.md") if path.relative_to(ROOT).as_posix() not in PROTECTED]
for path in editable_markdown:
    rel = path.relative_to(ROOT).as_posix()
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    if b"\r\n" in raw:
        issues.append(f"{rel}: CRLF line endings")
    if not raw.endswith(b"\n"):
        issues.append(f"{rel}: missing final newline")
    for number, line in enumerate(text.splitlines(), 1):
        if "\t" in line:
            issues.append(f"{rel}:{number}: tab character")
        trailing = len(line) - len(line.rstrip(" "))
        if trailing not in (0, 2):
            issues.append(f"{rel}:{number}: use zero or exactly two trailing spaces")
    rendered = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    for paragraph in re.findall(r"<p>(.*?)</p>", rendered, re.S):
        lines = paragraph.strip().splitlines()
        if any(not re.search(r"<br\s*/?>\s*$", line) for line in lines[:-1]):
            issues.append(f"{rel}: rendered soft break lacks two-space marker")
            break

for rel in DOCUMENTS.values():
    lines = (ROOT / rel).read_text(encoding="utf-8").splitlines()
    in_article = False
    for index, line in enumerate(lines, 1):
        stripped = line.rstrip(" ").strip()
        trailing = len(line) - len(line.rstrip(" "))
        if re.match(r"^### 제", stripped):
            in_article = True
            if trailing != 2:
                issues.append(f"{rel}:{index}: article heading lacks two-space break")
            continue
        if stripped.startswith("#"):
            in_article = False
            continue
        if in_article and stripped and trailing != 2:
            issues.append(f"{rel}:{index}: rule line lacks two-space break")

articles_by_document: dict[str, dict[int, str]] = {}
for name, rel in DOCUMENTS.items():
    text = (ROOT / rel).read_text(encoding="utf-8").split("## 부칙", 1)[0]
    starts = list(re.finditer(r"^### 제(\d+)조(?:의\d+)?(?:\([^\n]+\))?", text, re.M))
    articles: dict[int, str] = {}
    primary_numbers: list[int] = []
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        number = int(match.group(1))
        articles.setdefault(number, "")
        articles[number] += text[match.end():end]
        if "조의" not in match.group(0):
            primary_numbers.append(number)
    expected = list(range(1, max(primary_numbers) + 1)) if primary_numbers else []
    if primary_numbers != expected:
        issues.append(f"{rel}: non-continuous article numbering {primary_numbers}")
    articles_by_document[name] = articles

cross_reference = re.compile(r"「([^」]+)」 제(\d+)조(?:제(\d+)항)?")
paragraph_marks = "①②③④⑤⑥⑦⑧⑨⑩"
for source_name, rel in DOCUMENTS.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for target_name, article_text, paragraph_text in cross_reference.findall(text):
        if target_name not in articles_by_document:
            continue
        article = int(article_text)
        target = articles_by_document[target_name]
        if article not in target:
            issues.append(f"{rel}: missing target 「{target_name}」 제{article}조")
        elif paragraph_text and paragraph_marks[int(paragraph_text) - 1] not in target[article]:
            issues.append(f"{rel}: missing target 「{target_name}」 제{article}조제{paragraph_text}항")

    local_text = re.sub(r"「[^」]+」\s*제\d+조(?:의\d+)?(?:제\d+항)?", "", text)
    for article_text, paragraph_text in re.findall(r"제(\d+)조제(\d+)항", local_text):
        article = int(article_text)
        target = articles_by_document[source_name]
        if article not in target:
            issues.append(f"{rel}: missing same-document 제{article}조")
        elif int(paragraph_text) > len(paragraph_marks) or paragraph_marks[int(paragraph_text) - 1] not in target[article]:
            issues.append(f"{rel}: missing same-document 제{article}조제{paragraph_text}항")

for rel, phrases in INVARIANTS.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in text:
            issues.append(f"{rel}: missing invariant: {phrase}")

stale_terms = ["특별의결", "불신임", "회원발의 정족수", "참여자 과반수", "재적회원이 75명 이상이면"]
for rel in DOCUMENTS.values():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for term in stale_terms:
        if term in text:
            issues.append(f"{rel}: stale term: {term}")
    if "“" in text or "”" in text:
        issues.append(f"{rel}: curly double quote")

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
        issues.append(f"{rel}: unreadable pdfinfo")
        continue
    pages = int(pages_match.group(1))
    if "594" not in size_match.group(1) or "841" not in size_match.group(1):
        issues.append(f"{rel}: non-A4 page size {size_match.group(1)}")
    reader = PdfReader(path)
    metadata = reader.metadata or {}
    if metadata.get("/Producer") != "SCSC deterministic build":
        issues.append(f"{rel}: noncanonical PDF producer")
    if metadata.get("/CreationDate") != "D:20260814000000+09'00'":
        issues.append(f"{rel}: noncanonical PDF creation date")
    for page_number, page in enumerate(reader.pages, 1):
        for annotation_ref in page.get("/Annots", []):
            annotation = annotation_ref.get_object()
            action = annotation.get("/A")
            uri = str(action.get("/URI", "")) if action else ""
            if re.search(r"^(?:file:|about:)|localhost|/home/|\\\\", uri, re.I):
                issues.append(f"{rel}: page {page_number}: local PDF URI {uri}")
    text_path = OUT / (rel.replace("/", "__") + ".txt")
    subprocess.run(["pdftotext", "-layout", str(path), str(text_path)], check=True)
    text = text_path.read_text(encoding="utf-8", errors="replace")
    if len([page for page in text.split("\f") if page.strip()]) != pages:
        issues.append(f"{rel}: blank or textless page")
    for phrase in phrases:
        if phrase not in text:
            issues.append(f"{rel}: missing expected PDF text: {phrase}")
    if re.search(r"file://|localhost|about:blank", text, re.I):
        issues.append(f"{rel}: browser residue")

if issues:
    print("FAIL")
    for issue in issues:
        print(f"- {issue}")
    raise SystemExit(1)

print(f"PASS: protected originals, {len(DOCUMENTS)} normative sources, references, invariants, and {len(PDFS)} PDFs validated.")
