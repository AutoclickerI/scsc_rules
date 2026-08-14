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
    "revision_plan.pdf": ["SCSC 규정 채택 절차", "총회는 회칙·시행일"],
    "web_rules_comparison.pdf": ["국내 대학 동아리 규정 체계 비교", "조 제목 35개"],
    "CHANGELOG.pdf": ["SCSC 회칙 전면개정 변경기록", "공백 제외 문자 감소"],
    "규정_시행_후_필수_확인_매뉴얼.pdf": ["SCSC 규정 시행 후 필수 확인 매뉴얼", "시행일부터 14일 안에"],
    "draft/SCSC_rules_draft_bundle.pdf": ["SCSC 회칙안", "SCSC 징계 및 권리보호 세칙안", "SCSC 개인정보 처리방침안"],
}

INVARIANTS = {
    "draft/rules_draft.md": [
        '"회원발의"란 회원 15명이 공동으로 요구하거나 발의하는 것을 말한다',
        "총회 공고 시각의 의결권자 수를 기준으로 그 10분의 1에 5명을 더하고 소수점 이하는 올린 수",
        '"회장단"은 회장·부회장·회계를 말한다',
        '"임원진"은 회장단과 그 밖의 현직 임원 전체를 말하며',
        "회장과 회계는 각 한 명으로 한다",
        "부회장과 그 밖의 임원 수는 임원회의가 정한다",
        "직책 수 변경이나 업무분장으로 현직 임원의 직위·임기 또는 주요 업무·권한을 없애거나 해임과 실질적으로 같은 결과를 만들 수 없으며",
        "그러한 변경에는 제10조제2항을 적용한다",
        "임원은 재임 중 회원 자격을 유지해야 하며 그 자격이 끝나면 임원직도 끝난다",
        "회비 납부를 해당 학기의 등록 요건으로 공고한 경우",
        "회장을 제외한 임원을 해임할 수 있다",
        "직책 수 변경과 그에 따른 임명은 하나의 결정으로 공고하고 재검토한다",
        "임원회의가 후보자를 두 차례 정하지 못하거나",
        "최초 또는 후속 추천기한까지 후보자가 추천되지 않으면",
        "부회장 현황과 회장 직무대행 순서를 공고한다",
        "순서 변경은 공고 7일 뒤 효력이 생기며",
        "탄핵안 제출 시각의 순서는 각각 해당 직무대행과 탄핵 절차가 끝날 때까지 유지한다",
        "공고한 순서의 부회장, 임원회의가 본인의 동의를 받아 정한 회원 순으로 대행한다",
        "제15조제1항을 제외한 본회의 모든 운영 사항을 결정하고 집행한다",
        "명시되지 않은 운영 권한도 임원회의에 속한다",
        "임원 두 명 이상이 참여하며 두 명 이상이 찬성하고 찬성표가 반대표보다 많으면 의결한다",
        "복수 후보는 한 명을 선택하여 투표하고",
        "득표 순위 상위 두 명을 대상으로 결선투표한다",
        "그 밖의 임원회의 결정도 총회에 재검토하도록 요구할 수 있다",
        "이해관계자 거래, 중요 자산·권리의 처분",
        "임원의 임명·해임이나 직책 수 확대, 회장 직무대행 순서 변경, 회원 권리 제한",
        "총회가 원결정의 유지를 의결할 때까지 집행하지 않고, 유지 의결하지 않으면 효력을 잃는다",
        "제16조제4항 단서의 대상 결정을 재검토하는 총회를 제외하고 기간을 줄일 수 있으며",
        "재검토 대상 결정을 집행하거나 사실상 같은 효과를 내는 데 이용할 수 없다",
        "공식 채널·채널 담당 임원·비공개 신고·대체 소집 방법의 지정·교체",
        "핵심 계정·인증수단의 관리·복구권한 부여·이전",
        "세무단체 후속 관리 단위의 지정 및 그에 따른 관리·기록·자산·권리·계좌·접근권한의 이전",
        "이 소집에는 회원발의가 필요하지 않으며 비공개 정보는 공개하지 않는다",
        "회칙의 제정·개정·폐지, 회장 선출·탄핵, 회원 제명과 본회의 해산",
        "총회의 발의·발언·표결권과 회장 선거권",
        "총회의 발의·발언·표결권과 임원회의 표결권을 제한할 수 없다",
        "같은 행위나 위험에 대한 연속·관련 제한은 기간을 합산한다",
        "최종결정위원회가 제명을 제외한 범위에서 임원회의를 대신하여 결정할 수 있다",
        "세 명 전원의 찬성으로 절차와 비례성을 함께 확인한 결정에는 별도의 확인을 요구하지 않는다",
        "재적회원 과반수가 참여하고 참여자의 2분의 1 이상이 찬성하면 해산을 의결한다",
        "수령단체를 직접·간접으로 지배하거나 이전·재이전으로 중대한 개인적 이익을 얻어서는 안 된다",
        "임기는 2026년 12월 31일에 끝난다",
        "시행 당시 부회장·회계의 직위는 남은 임기 동안 유지하고",
        "시행 당시 현직자의 직위를 보전하는 최초 부회장·그 밖의 임원 수",
        "시행일부터 30일 안에 임원회의는 「법인으로 보는 단체 SCSC 운영 세칙」 제6조부터 제8조까지에 따라",
        "재량적 권한은 그 권한의 심사·인계를 마친 때와 시행일부터 30일이 지난 때 중 먼저 도래한 때",
        "후임 지정이 효력을 얻고 실제 통제가 이전될 때까지",
        "종전 권한자가 직무를 수행할 수 없거나 협조하지 않으면 서로 다른 현직 임원 두 명",
        "3일 안에 공동관리 보완 또는 새 지정 절차를 시작하여 14일 안에 마친다",
        "14일 안에 마치지 못하면 총회가 새 지정을 결정하고",
        "시행과 동시에 적용할 임시 주 공식 채널, 하나 이상의 예비 채널",
        "이 회칙과 함께 공고한 「SCSC 의사결정 세칙」",
        "이후의 등록·탈퇴·임원 인사나 직무 변경은 해당 탄핵안에 영향을 주지 않는다",
        "총회 성립 정족수는 제2항의 의결권자를 기준으로 계산한다",
    ],
    "draft/subrules/A_decision_rules_draft.md": [
        "대한민국 표준시와 공식 채널의 기록 시각을 기준",
        "정당한 이유 없이 24시간 안에 처리하지 않으면",
        "통지부터 참여기한까지의 기간은 24시간 이상 7일 이하로 한다",
        "임원회의 투표는 제6조제1항의 통지부터 참여기한까지 실시하고",
        "회장을 제외한 한 명 이상의 채널 담당 임원을 지정하고",
        "우회 대상자의 협조·계정 권한·인증 비밀 없이 활성화하거나",
        "접근할 수 없으면 제1항의 절차로 대체 채널을 지정할 수 있다",
        "지정·교체안을 기존 채널과 제안 채널에 모두 공고하고",
        "임원이 아닌 대체 확인자 두 명 이상",
        "각 공동발의자의 의사를 직접 확인하고",
        "두 사람이 모두 확인한 공동발의자 수를 확정한다",
        "요구 내용, 대상 결정과 공고일, 15명 이상인 발의 인원과 제출 시각",
        "관련 기한이 끝나기 전에 한 게시마다 관련 기한을 확인이 끝날 때까지 임시 정지하고",
        "확인 중에는 「SCSC 회칙」 제16조제4항 단서의 대상 결정을 집행할 수 없다",
        "동일 대표자 또는 실질적으로 같은 공동발의자 구성의 미성립 게시로는 같은 결정의 기한을 한 차례만 정지한다",
        "심의·표결·집행에 참여하려는 사람 중",
        "심의·표결·집행에서 회피한다",
        "고위험 행사 안전계획에도 같은 기준을 적용한다",
        "결정의 효력과 회원발의 재검토는 「SCSC 회칙」 제16조제3항·제4항에 따른다",
        "표결 기간에는 이 세칙 제7조제1항을 적용한다",
        "요청일부터 14일 안에 제공을 마친다",
        "총회 기간투표는 48시간 이상",
        "회수할 수 없는 지출은 사람의 즉각적인 안전에 필요하고 승인 예산 안인 최소 금액",
        "그 밖의 지출은 취소하거나 전액 환급받을 수 있어야 한다",
        "긴급결정으로 규정을 바꾸거나 선거·탄핵·징계·제명·해산을 결정하거나",
        "72시간 안에 추인하지 않으면",
        "공식 채널 밖의 행위나 합의를 추인할 때",
        "보호 대상인 근거 조항과 분류, 공고 시각, 가장 이른 효력 발생 시각",
        "이 내용을 갖춘 공고가 제2조의 공식 채널에서 회원에게 접근 가능하게 된 때부터 7일",
        "임명직 임원 후보자를 추천한다",
        "추천했다는 사유만으로는 임명 여부 결정에서 제외하지 않는다",
        "부결되거나 그 기한 안에 결정하지 못한 때를 임명 실패 한 차례로 센다",
        "그 후속 추천기한까지 후보자가 없거나 두 번째 후보자도 부결되거나 7일 안에 결정하지 못하면",
        "부회장 또는 회계가 공석이면",
        "회장 직무대행과 임원진 재구성은 「SCSC 회칙」 제11조제2항·제3항에 따른다",
        "제출 시각에 「SCSC 회칙」 제9조제3항에 따라 확정된 순서",
        "공동발의자들이 정한 다른 회원발의 대표가 접수·공고하고 최초 제출 시각을 접수 시각으로 본다",
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
        "「SCSC 회칙」 제33조제3항에 열거된 사람들을 위한 재이전 금지",
        "임원회의가 정한 자산·계정 담당 임원",
        "현직 임원 두 명의 참여를 기술적으로 요구한다",
        "독립된 임원에 대한 즉시 경보와 시험된 복구경로를 포함한 보완통제",
    ],
    "draft/subrules/C_tax_entity_rules_draft.md": [
        "현직 부회장이 없으면 회장·회계로 한다",
        "부회장은 제1항의 한 명을 넘을 수 없다",
        "「SCSC 회칙」 제16조제3항의 세무단체 사항은 임원회의가 의결하고 같은 조 제4항에 따른다",
        "후속 관리 단위의 지정과 인계 결정의 효력·재검토에는 「SCSC 회칙」 제16조제3항·제4항을 적용한다",
        "후임자의 권한이 효력을 얻을 때까지 종전 대표자가 직무를 수행할 수 있으면",
        "회계, 회장, 공고된 회장 직무대행 순서의 부회장, 자산·계정 담당 임원 순으로",
        "계약, 자산 이전, 계정·복구권한 변경 또는 새로운 재량 거래를 할 수 없고",
        "대표자·회계 또는 관련 업무 담당 임원이 바뀌면",
    ],
    "draft/subrules/D_discipline_rights_rules_draft.md": [
        "자료가 부족하다는 이유만으로 접수를 거부할 수 없다",
        "발의·발언·표결권과 임원회의 표결권은 제한할 수 없다",
        "원결정에 관여하지 않은",
        "새 총회가 유지·변경·취소를 결정한다",
        "이 요구에는 회원발의가 필요하지 않다",
        "독립 확인을 거치지 않은 제재의 비례성",
        "당사자는 언제든 축소·해제를 요청할 수 있다",
        "임원이 아니고 임원진과 이해관계가 없는 회원 두 명 이상",
        "모든 채널 담당 임원이 직무를 수행할 수 없거나 어느 담당 임원도 공고하지 않으면",
        "임원진의 협조나 계정 권한 없이 이용할 수 있고 공고자를 확인할 수 있는 대체 소집 방법",
        "대체 접수자와 방법은 다음 지정이 효력을 얻을 때까지 유지하며",
        "비공개 접수 방법이 지정되지 않았거나 기술적으로 사용할 수 없거나 접근이 거부되거나 피신고자가 통제하거나 침해된 때",
        "신고 후 24시간 안에 접수 사실을 통지받지 못하면",
        "사건 내용을 공개하지 않는 일회성 비공개 접수 방법을 공동으로 정할 수 있다",
        "「SCSC 회칙」을 채택한 총회는 제4조제1항의 최초 대체 접수자 두 명 이상, 비공개 접수 방법과 대체 소집 방법을 함께 정한다",
        "이 세칙에 따라 임원회의가 절차 담당자를 선임해야 하면 선임 사유가 생긴 날부터 3일 안에 정한다",
        "다음 접수자에게 한 차례 넘긴다",
        "다음 접수자가 없거나 그 기한 안에 통지하지 않으면 제4조제3항을 적용한다",
        "심사자 또는 확인자가 기본기한 또는 적법하게 연장한 기한의 마지막 날까지",
        "임시 접수자 두 명이 임원진의 협조·계정 권한·인증 비밀 없이",
        "결정기구가 기본기한 또는 적법하게 연장한 기한의 마지막 날까지 결정하지 않으면",
        "한 차례의 후속 총회가 결정하고",
        "그 밖의 사건은 제2조제6항의 최종결정위원회가 결정한다",
        "원결정기구는 돌려받은 날부터 7일 안에 다시 결정하며",
        "최종결정위원회가 필요하면 직무를 수행할 수 있는 대체 접수자 두 명이",
        "위원회를 기한 안에 구성하지 못하거나 위원회가 결정하지 못하면",
        "세 명 모두가 참여하여 사실·절차·비례성을 확인하고 찬성하여야 한다",
        "위원회의 결정이나 종결을 3일 안에 당사자에게 통지한다",
        "제2조제6항의 최종결정위원회가 마지막으로 재검토한다",
        "침묵을 인용이나 기각으로 보지 않는다",
    ],
    "draft/forms/operations_control_manual.md": [
        "임원 임명·해임·직책 수 확대가 재검토되면 총회의 유지 의결 전에는 시행하지 않는다",
        "직책 수나 업무분장 변경으로 해임 절차를 우회하지 않는다",
        "임원진의 협조·계정 권한 없이 쓸 수 있는 대체 소집 방법",
        "세무단체의 부회장 구성원이 한 명을 넘지 않는지 확인한다",
        "공식 채널 지정·교체는 기존 채널과 제안 채널에 공고하고",
        "회원발의 대표·공동발의자 한 명이 우회 대상자의 협조·계정 권한·인증 비밀 없이 예비 채널을 활성화하거나 대체 채널을 지정할 수 있는지도 시험한다",
        "회수할 수 없는 지출은 사람의 즉각적인 안전에 필요한 승인 예산 안의 최소 금액만 허용하고",
        "대표자 공석부터 후임 효력 발생까지 종전 대표자 또는 회계·회장·공고된 직무대행 순서",
        "현직 임원 두 명이 기술적으로 필요하게 한다",
        "회칙 제33조제3항에 열거된 사람들을 위한 재이전 금지",
        "후속 추천이 없거나 두 차례 실패하면 총회 임명 절차를 시작한다",
        "보호 근거·분류, 공고 시각, 가장 이른 효력일",
        "동일 대표자·실질적으로 같은 구성의 미성립 횟수",
        "직무대행 순서는 효력일과 적용 기준 시각을 기록하고, 변경이 재검토되면 총회의 유지 의결 전에는 적용하지 않는다",
        "기본·연장 최종기한",
        "한 차례의 후속 총회로 회부하고",
        "최종결정위원회의 21일 기한",
        "위원 세 명 전원의 사실·절차·비례성 확인",
        "누락·장애·접근 거부·피신고자 통제·침해 또는 24시간 접수 확인 실패",
        "후임 효력·실제 통제 이전까지 유지하는 제한된 2인 공동관리",
        "3일·14일 보완·재지정과 총회 전환",
        "종료·교체·후속 관리 단위 지정과 관리·기록·자산·권리·계좌·접근권한 이전",
    ],
    "draft/forms/operations_control_record_templates.md": [
        "회원발의 재검토·유지 의결 필요 여부·결과",
        "직무대행 순서·효력일·적용 기준 시각",
        "부회장 구성원 수(0명 또는 1명)",
        "기존·제안 채널 공고·기존 채널 유지기간",
        "임원 두 명·회원발의 대표와 공동발의자의 독립 활성화 또는 대체 채널 지정 시험·증명",
        "관리·복구권한 보유자·부여·이전·회수 내역",
        "서비스상 2인 통제 또는 단독 통제 방지 보완통제·독립 경보·복구시험",
        "회수 불가 지출이면 즉각적인 사람 안전·승인 예산·최소 금액 근거",
        "대표자 공석·제한된 연속관리인·다른 임원 확인·금지행위·자동 종료",
        "수령단체의 회칙 제33조제3항상 내부자를 위한 재이전 금지",
        "절차 담당자 선임 실패·대체 소집·총회",
        "최종 확인자 선정·확인기한·공통 확인 인원",
        "대상 결정·공고일·15명 이상 표시·비공개 확인자료 동시 제출",
        "보호 근거·분류·공고 시각·가장 이른 효력일",
        "부결·7일 미결정 횟수·후속 추천기한",
        "비공개 방법 누락·장애·거부·피신고자 통제·침해·24시간 확인 실패",
        "최종 기한 초과·직무불능·기록 이전·후임",
        "한 차례 후속 총회·최종결정위원회 구성·21일 결정",
        "최종 실패·제재 없는 종결 또는 원제재 효력 상실",
        "독립 확인 대상 제재의 위원 3인 전원 사실·절차·비례성 확인",
        "시행 후 재구성·종전 위임과 권한 재승인·30일 기한",
        "미승인 재량권 종료일·후임 효력·실제 통제 이전·2인 공동관리·1인 비재량 보전·3일·14일·총회 전환",
    ],
    "규정_시행_후_필수_확인_매뉴얼.md": [
        "새로운 권한·의무·제재·기한을 만들지 않으며",
        "공고된 회장 직무대행 순서와 효력일",
        "보호된 결정 공고에 근거·분류·공고 시각·가장 이른 효력일",
        "회장 직무대행 순서 변경, 임원 임명·해임·직책 수 확대",
        "행정상 목표로 시행일부터 14일 안에 마치고",
        "기본·연장 최종기한 초과 시 담당자 교체·기록 이전·반송 뒤 재결정",
        "최초·후속 추천기한, 부결·7일 미결정의 실패 횟수",
        "미승인 재량권은 심사·인계 완료와 30일 중 이른 때 종료하되",
        "후임 지정의 효력 발생과 실제 통제 이전까지 제한된 2인 공동관리",
        "누락·장애·접근 거부·피신고자 통제·침해 또는 24시간 접수 확인 실패",
        "한 차례 후속 총회·최종결정위원회가 작동하는지 확인한다",
        "최종 실패 때 제재 없는 종결 또는 원제재 효력 상실",
        "독립 확인 대상 제재의 위원 3인 전원 확인",
        "현직 임원 두 명이 기술적으로 필요한지 시험한다",
        "대표자 공석부터 후임 효력 발생까지 종전 대표자 또는 자동 순서의 임시 대리인이",
    ],
    "revision_plan.md": [
        "회칙, 세칙 4종, 운영방침 4종과 변경기록·작성 기준을 총회 7일 전에 공개한다",
        "임시 주·예비 공식 채널·채널 담당 임원·확인·독립 활성화 방법",
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

def extract_articles(text: str) -> tuple[dict[int, str], list[int]]:
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
    return articles, primary_numbers


articles_by_document: dict[str, dict[int, str]] = {}
supplement_articles_by_document: dict[str, dict[int, str]] = {}
for name, rel in DOCUMENTS.items():
    full_text = (ROOT / rel).read_text(encoding="utf-8")
    main_text, separator, supplement_text = full_text.partition("## 부칙")
    articles, primary_numbers = extract_articles(main_text)
    expected = list(range(1, max(primary_numbers) + 1)) if primary_numbers else []
    if primary_numbers != expected:
        issues.append(f"{rel}: non-continuous article numbering {primary_numbers}")
    articles_by_document[name] = articles
    supplement_articles_by_document[name] = extract_articles(supplement_text)[0] if separator else {}

cross_reference = re.compile(r"「([^」]+)」 (부칙 )?제(\d+)조(?:제(\d+)항)?")
paragraph_marks = "①②③④⑤⑥⑦⑧⑨⑩"
for source_name, rel in DOCUMENTS.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for target_name, supplement_marker, article_text, paragraph_text in cross_reference.findall(text):
        if target_name not in articles_by_document:
            continue
        article = int(article_text)
        target = supplement_articles_by_document[target_name] if supplement_marker else articles_by_document[target_name]
        label = "부칙 " if supplement_marker else ""
        if article not in target:
            issues.append(f"{rel}: missing target 「{target_name}」 {label}제{article}조")
        elif paragraph_text and paragraph_marks[int(paragraph_text) - 1] not in target[article]:
            issues.append(f"{rel}: missing target 「{target_name}」 {label}제{article}조제{paragraph_text}항")

    local_text = re.sub(r"「[^」]+」\s*(?:부칙\s*)?제\d+조(?:의\d+)?(?:제\d+항)?", "", text)
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

obsolete_officer_phrases = [
    "회장·부회장·회계·관리자",
    "부회장·회계·관리자",
    "회장과 관리자가",
    "회계와 관리자는",
    "대표자·회계·관리자",
    "관리자에게 임시 접수자",
]
officer_role_surfaces = list(DOCUMENTS.values()) + [
    "draft/forms/operations_control_manual.md",
    "draft/forms/operations_control_record_templates.md",
    "규정_시행_후_필수_확인_매뉴얼.md",
]
for rel in officer_role_surfaces:
    text = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in obsolete_officer_phrases:
        if phrase in text:
            issues.append(f"{rel}: obsolete fixed administrator office: {phrase}")

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
