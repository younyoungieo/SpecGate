# SpecGate 발표자료 목차 (Keynote용)

## **"문을 만들어준다" - 설계와 코드 사이의 자동 연결고리**

---

## 📋 **발표자료 구성 (총 18분 + Q&A 7분)**

### **1. 문제 인식 (2분)**
**슬라이드 1: SpecGate - 설계와 코드 사이의 자동 연결고리**
- 🚪 SpecGate 로고 + "문을 만들어준다" 메타포
- **메인 타이틀**: "SpecGate"
- **서브타이틀**: "설계와 코드 사이에 자동으로 문을 만들어주는 플랫폼"
- **핵심 메시지**: "Confluence 설계 문서를 자동으로 룰·스니펫·테스트로 변환"
- **발표자 정보**: 이름, 날짜, 조직
- **시각적 요소**: SpecGate 로고, 깔끔한 흰색 배경, SpecGate 브랜드 컬러 (#2563EB)

**슬라이드 2: 현재 상황 - "문이 없는 상태"**
- **시각적 구성**: 
  - 📄 Confluence 설계 문서 (왼쪽) - "API 설계서", "아키텍처 문서", "ERD 다이어그램"
  - 💻 GitHub 실제 코드 (오른쪽) - "UserService.java", "UserController.java", "UserRepository.java"
  - ❌ **직접 연결 불가능** (중간에 큰 X 표시)
- **핵심 메시지**: "시간이 지날수록 설계와 코드의 괴리 심화"
- **구체적 문제**: 
  - 설계 문서는 Confluence에, 코드는 GitHub에 분리 저장
  - 개발자가 설계를 기억하고 수동으로 준수해야 함
  - 시간이 지날수록 문서와 코드 불일치 증가

**슬라이드 3: 기존 방식의 한계**
- **📝 문서 작성만으로는 지속적 준수 어려움**
  - Confluence에 설계 문서 작성 후 방치
  - 개발자가 문서를 찾아보고 수동으로 준수
  - 시간이 지날수록 문서와 코드 불일치 심화
- **👥 코드 리뷰에서 수동 지적 → 비용 크고 누락 잦음**
  - 리뷰어가 설계 문서를 기억하고 수동으로 검토
  - 설계 위반 사항을 놓치기 쉬움
  - 리뷰 시간 증가, 품질 관리 비용 상승
- **🤖 IDE 도우미만으로는 설계 밖 코드 생성 위험**
  - ChatGPT, Copilot 등은 일반적인 코드 패턴만 제안
  - 프로젝트별 설계 규칙을 반영하지 못함
  - 설계와 무관한 코드 생성으로 오히려 문제 악화

---

### **2. 솔루션: SpecGate (3분)**
**슬라이드 4: SpecGate가 만드는 "문"**
- **시각적 표현**: 
  - 📄 Confluence 설계 문서 (왼쪽)
  - 🚪 SpecGate 플랫폼 (중앙) - "자동 변환 엔진"
  - ⚡ 실행 가능한 코드 (오른쪽)
  - 화살표로 연결: "자동으로 문을 만들어줌"
- **핵심 메시지**: "설계 문서와 코드 사이의 자동 연결고리"
- **구체적 기능**:
  - Confluence 문서를 자동으로 분석
  - 설계 규칙을 룰·스니펫·테스트로 변환
  - 개발 단계와 PR/CI 단계에서 자동 적용

**슬라이드 5: 3단계 문 구조**
- **Phase 1: 문서 수집 문** 📄 → 📋
  - Confluence API로 설계 문서 자동 수집
  - SpecLint로 품질 검사 (0-100점)
  - HTML→MD 변환으로 정규화
- **Phase 2: 변환 문** 📋 → ⚡
  - DesignRuleSpec 중간 표현 DSL 생성
  - Cursor IDE용 .mdc 룰 파일 자동 생성
  - 실시간 스니펫, 가이드, 위반 감지
- **Phase 3: 검증 문** ⚡ → ✅
  - ArchUnit, Semgrep, OpenAPI Diff 테스트 자동 생성
  - Drift Score로 설계-코드 괴리 정도 측정 (0-100점)
  - PR 차단 및 Drift Radar 시각적 피드백

**슬라이드 6: SpecGate의 핵심 가치**
- **IDE 단계**: 실시간 가이드로 설계 준수 유도
  - Cursor IDE에서 실시간 룰 적용
  - 코드 작성 시 자동 스니펫 제안
  - 설계 위반 시 즉시 알림 및 수정 가이드
- **PR/CI 단계**: 자동 검사·게이트 차단으로 강제력 확보
  - GitHub Actions에서 자동 테스트 실행
  - Drift Score 임계치 초과 시 PR 자동 차단
  - 설계 준수율을 객관적 수치로 측정
- **PR 화면**: Drift Radar로 위반 내역 시각화
  - 전체 Drift Score와 영역별 점수 표시
  - 위반 사항별 상세 카드 및 수정 방법 제시
  - 리뷰어가 쉽게 확인할 수 있는 시각적 인터페이스

---

### **3. 핵심 기능: 3단계 문의 작동 원리 (4분)**
**슬라이드 7: Phase 1: 문서 수집 및 정규화**
- **confluence.fetch**: 라벨/경로 기준으로 설계 문서 자동 수집
  - "API 설계", "아키텍처", "데이터 모델" 라벨 기반 수집
  - 첨부파일(ERD, OpenAPI 스펙) 자동 캐시
- **speclint.lint**: 문서 품질 검사 (0-100점)
  - 표준 템플릿 준수 여부 검사
  - 품질 70점 미만 시 GitHub Issues 자동 생성
  - HITL(Human-in-the-Loop) 프로세스로 신뢰도 확보
- **정규화**: HTML→MD 변환으로 설계 규칙 추출에 최적화

**슬라이드 8: Phase 2: 규칙 추출 및 IDE 룰 생성**
- **rules.extract**: DesignRuleSpec 중간 표현 DSL 생성
  - Azure OpenAI GPT-4로 자연어에서 구조화된 규칙 추출
  - RULE-[영역]-[번호] 형식의 표준 DSL 생성
  - 규칙 신뢰성 평가 및 충돌 해결
- **rules.generate.mdc**: Cursor IDE용 .mdc 룰 파일 자동 생성
  - DesignRuleSpec을 .cursor/rules/*.mdc로 변환
  - 적용 범위 설정 패턴 자동 생성
- **실시간 개발 지원**:
  - snippet.generate: 코드 작성 시 스니펫 자동완성
  - realtime.guide: 실시간 가이드 및 권장사항
  - violation.detect: 규칙 위반 시 실시간 감지 및 알림

**슬라이드 9: Phase 3: 자동 테스트 및 CI 검증**
- **tests.generate**: ArchUnit, Semgrep, OpenAPI Diff 테스트 자동 생성
  - DesignRuleSpec을 .specgate/semgrep/, .specgate/archtest/로 변환
  - Java 아키텍처 규칙, 보안 취약점, API 스펙 변경사항 검사
- **drift.score**: 설계-코드 괴리 정도 측정 (0-100점)
  - 0점: 완벽한 설계 준수, 100점: 심각한 설계 위반
  - 영역별 가중치: API(40%) > 아키텍처(35%) > 보안(20%) > 성능(10%) > 데이터(10%)
- **PR 관리**:
  - workflow.generate: .github/workflows/design-guard.yml 자동 생성
  - github.comment: Drift Radar 코멘트 자동 생성
  - 임계치 초과 시 PR 자동 차단

---

### **4. 아키텍처 (4분)**
**슬라이드 10: 시스템 아키텍처**
- **메인 다이어그램**: SpecGate_flow_architecture.png
  - Developer Workflow → SpecGate MCP Server → GitHub Actions → PR
  - External Integrations (Confluence API) → MCP Server
  - Security & Compliance (TLS, Audit Logging, ZTNA) → Azure Key Vault
- **MCP Server 중심의 통합 시스템**:
  - Phase 1: confluence.fetch, speclint.lint
  - Phase 2: rules.extract, rules.generate.mdc, snippet.generate, realtime.guide, violation.detect
  - Phase 3: tests.generate, drift.score, github.comment, workflow.generate
- **데이터 흐름**: Confluence → 정규화된 문서 → DesignRuleSpec → IDE 룰/테스트 → CI 검증

**슬라이드 11: 기술 스택**
- **MCP (Model Context Protocol)**: AI 모델과 외부 도구 간의 표준화된 통신 프로토콜
- **FastMCP**: Python 기반 MCP Server로 11개 도구 통합 제공
- **Azure OpenAI**: GPT-4 기반 자연어에서 설계 규칙 추출
- **Cursor IDE**: 실시간 개발 지원 및 MCP 프로토콜 연동
- **GitHub Actions**: 자동 CI/CD 파이프라인 및 PR 게이트 관리
- **보안**: TLS 암호화, 감사 로깅, ZTNA 인증, Azure Key Vault 연동

---

### **5. 시나리오: 실제 사용 예시 (3분)**
**슬라이드 12: 개발 단계: 실시간 가이드**
- **MCP 연결**: Cursor IDE에서 SpecGate MCP Server 연결
  - "SpecGate MCP 서버 연결됨" 상태 표시
  - Confluence 문서 수집 완료: 5개 문서
  - Phase 1 완료: 문서 정규화 및 품질 검사
- **실시간 개발 지원**:
  - 코드 작성 시 자동 스니펫 제안 (API 설계 규칙 기반)
  - 실시간 가이드: "UserService는 Manager 계층을 거쳐야 합니다"
  - 위반 감지: "직접 Repository 호출은 금지됩니다" 알림
- **화면 목업**: Cursor IDE 인터페이스에 SpecGate 기능 통합 표시

**슬라이드 13: PR/CI 단계: 자동 검증 및 Drift Radar**
- **PR 생성**: 설계 위반 코드로 PR 생성 (GitHub 화면 목업)
  - "UserService가 Repository 직접 호출" 위반 코드
  - "API 응답 형식 불일치" 위반 코드
- **GitHub Actions 자동 실행**: design-guard.yml 워크플로우 실행
  - ArchUnit 실행: 아키텍처 규칙 검사
  - Semgrep 검사: 보안 취약점 검사
  - OpenAPI Diff: API 스펙 변경사항 검사
- **Drift Radar 표시**: GitHub PR 코멘트로 자동 생성
  - 전체 Drift Score: 65/100 (⚠️ 주의)
  - 영역별 점수: API(15점), 아키텍처(8점), 보안(0점), 성능(0점), 데이터(0점)
  - 위반 사항별 상세 카드: 구체적인 수정 방법과 예시 코드 제시
- **CI 결과**: Drift Score 65점 > 임계치 30점 → PR 자동 차단

---

### **6. 기대효과 (2분)**
**슬라이드 14: 개발자 경험 혁신**
- **실시간 가이드로 개발 속도 향상**
  - Cursor IDE에서 실시간 스니펫 제안
  - 설계 규칙을 기억할 필요 없이 자동 가이드
  - 코드 작성 시간 30% 단축 예상
- **설계 준수 코드 자동 작성**
  - DesignRuleSpec 기반 자동 스니펫 생성
  - 위반 코드 작성 시 즉시 알림 및 수정 가이드
  - 설계 준수율 90% 이상 달성
- **리뷰 효율성 증대**
  - Drift Radar로 위반 사항 시각화
  - 구체적인 수정 방법과 예시 코드 제공
  - 리뷰 시간 50% 단축 예상

**슬라이드 15: 품질 관리 혁신**
- **설계 준수도를 객관적 수치로 측정**
  - Drift Score 0-100점으로 설계-코드 괴리 정도 측정
  - 영역별 가중치 기반 정확한 평가
  - 시간에 따른 품질 변화 추적 가능
- **자동 검증으로 위반 사항 사전 차단**
  - PR 단계에서 자동 테스트 실행
  - 임계치 초과 시 PR 자동 차단
  - 프로덕션 배포 전 설계 위반 사전 차단
- **문서-코드 동기화 자동화**
  - Confluence 문서 변경 시 자동으로 룰 업데이트
  - 설계 변경사항이 코드에 자동 반영
  - 문서와 코드 간 불일치 문제 근본 해결
- **신규 투입자 온보딩 속도 향상**
  - 실시간 가이드로 프로젝트 설계 규칙 학습
  - 설계 문서를 찾아볼 필요 없이 IDE에서 바로 확인
  - 온보딩 시간 50% 단축 예상

---

### **7. 로드맵 (1분)**
**슬라이드 16: 로드맵 및 구현 계획**
- **Phase별 단계적 구현**
  - Phase 1: Confluence 연동 및 문서 표준화 (2주)
  - Phase 2: DesignRuleSpec 추출 및 IDE 룰 생성 (3주)
  - Phase 3: CI/CD 통합 및 Drift Radar 구현 (2주)
- **파일럿 프로젝트 적용**
  - 소규모 팀에서 1개 프로젝트 파일럿 운영
  - 사용자 피드백 수집 및 개선사항 반영
  - 3개월 파일럿 후 전체 조직 확산
- **조직 확산 전략**
  - 팀별 교육 및 가이드 제공
  - Confluence 템플릿 표준화
  - GitHub Actions 워크플로우 자동 설정

**슬라이드 17: 결론 및 Q&A**

#### **핵심 메시지**
> **"설계와 구현을 연결하는 문"**

#### **SpecGate의 가치**
- **설계와 코드 사이의 자동 연결고리**
- **3-Phase 자동화**: 문서 수집 → 변환 → 검증
- **실시간 가이드**: 개발 중 즉시 설계 준수 지원

#### **기대 효과**
- **개발 생산성 향상**: 리뷰 시간 50% 단축
- **품질 관리 혁신**: 설계-코드 동기화 자동화
- **팀 협업 강화**: 설계 의도 공유 및 준수

#### **마지막 장표**
```
┌─────────────────────────────────────────┐
│                                         │
│  🚪 SpecGate                            │
│                                         │
│  "설계와 구현을 연결하는 문"              │
│                                         │
│  📋 Confluence  →  🔄 변환  →  💻 코드   │
│                                         │
│  지금 바로 시작하세요!                    │
│                                         │
└─────────────────────────────────────────┘
```

**Q&A 안내**: "궁금한 점이 있으시면 언제든 질문해주세요!"

---

### **8. Q&A (7분)**
**핵심 질문 5개와 답변 준비**

**Q1: 기존 개발 프로세스를 바꿔야 하나요?**
- A: **기존 프로세스 그대로**: 개발자는 기존 방식대로 개발하면 됩니다
- **자동으로 보완**: SpecGate가 자동으로 설계 준수 가이드 및 검증을 제공합니다
- **최소한의 설정**: Cursor IDE와 GitHub Actions에만 추가 설정하면 됩니다
- **점진적 도입**: 팀별로 단계적으로 도입할 수 있습니다

**Q2: 다른 비슷한 도구들과의 차별점은 무엇인가요?**
- A: **기존 도구들**: SonarQube(코드 품질), ArchUnit(아키텍처 테스트), Semgrep(보안 검사) 등은 **개별적 검증**
- **SpecGate 차별점**: **설계 문서→코드 자동 연결**하는 **통합 플랫폼**
- **실시간 가이드**: 개발 중 즉시 설계 준수 코드 작성 지원
- **Drift Radar**: PR에서 설계 위반을 시각적으로 표시하고 수정 가이드 제공

**Q3: 사내망 보안과 배포는 어떻게 처리하나요?**
- A: **Azure 클라우드 배포**: 사내에서 구독 중인 Azure 서비스에 MCP 서버 배포
- **ZTNA 보안**: Zero Trust Network Access로 사내망에서만 접근 가능
- **Cursor IDE 연동**: ZTNA 활성화 시 Cursor에서 MCP 서버 등록하여 사용
- **데이터 보안**: Confluence, GitHub API만 접근, 외부 데이터 전송 없음
- **권한 관리**: 기존 Confluence/GitHub 권한 체계 그대로 활용

**Q4: Drift Score가 너무 엄격해서 개발 속도가 느려질 수 있나요?**
- A: **조정 가능**: Drift Score 임계값을 팀별로 설정 (기본 30점 이하)
- **실시간 가이드**: 개발 중 사전에 설계 준수 코드 작성 유도
- **오히려 가속화**: 리뷰 시간 50% 단축, 버그 감소 30%로 전체 개발 속도 향상
- **점진적 도입**: 초기에는 경고만, 점차 엄격하게 조정 가능

**Q5: 다른 IDE나 버전 관리 시스템도 지원하나요?**
- A: **현재 최적화**: Cursor IDE와 GitHub에 최적화되어 있음
- **MCP 기반 확장**: MCP 프로토콜 기반이므로 VS Code, IntelliJ 등으로 확장 가능
- **플랫폼 확장**: GitLab, Bitbucket 등 다른 플랫폼도 MCP 서버만 추가하면 지원
- **점진적 확장**: 사용자 요구에 따라 단계적으로 지원 범위 확대

---

## 🎨 **시각적 구성 요소**

### **핵심 다이어그램**
1. **"문이 없는 상태"** vs **"SpecGate가 만드는 문"** 비교
2. **3단계 문 구조** 플로우차트
3. **MCP 기반 통합 시스템** 아키텍처
4. **Phase별 데이터 흐름** 시퀀스 다이어그램
5. **Drift Radar** 실제 화면 예시

### **애니메이션 효과**
- **문 생성 과정**: Phase별로 순차적 애니메이션
- **데이터 흐름**: 화살표로 흐름 표현
- **Drift Score 변화**: 수정 전후 점수 변화

### **실제 화면 목업**
- **Cursor IDE**: 룰 적용 및 실시간 가이드 (목업)
- **GitHub PR**: Drift Radar 코멘트 (목업)
- **CI 결과**: ArchUnit, Semgrep 검사 결과 (시뮬레이션)

---

## 💡 **핵심 메시지 정리**

### **문제**: "문이 없는 개발팀"
- 설계 문서와 코드가 분리
- 시간이 지날수록 괴리 심화

### **해결**: "SpecGate가 문을 만들어줌"
- 자동으로 설계와 코드 연결
- 3단계 문을 통한 안전한 변환

### **결과**: "완벽한 문이 있는 개발팀"
- 설계와 코드 실시간 동기화
- 품질과 생산성 동시 향상
