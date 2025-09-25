# SpecGate Confluence 정책 및 운영 가이드

## 📋 개요

이 문서는 SpecGate 시스템과 연동되는 Confluence 환경의 설정, 라벨 체계, 그리고 문서 수집 정책을 정의합니다.
Confluence 관리자와 프로젝트 매니저가 SpecGate와 효율적으로 연동할 수 있도록 표준화된 가이드라인을 제공합니다.

## 🎯 정책 목적

- **자동화된 수집**: SpecGate가 정확한 문서를 자동으로 찾고 수집
- **품질 관리**: 표준화된 라벨 체계를 통한 문서 품질 보장
- **접근 제어**: 권한 기반의 안전한 문서 접근 관리
- **확장성**: 프로젝트 증가에 따른 유연한 확장 가능

## 🏷️ **라벨 체계 (Label System)**

### 1. 기본 라벨 구조
```
specgate:[카테고리]:[값]
```

### 2. 필수 라벨 카테고리

#### 2.1 프로젝트 라벨 (필수)
```
specgate:project:[프로젝트명]
```
**예시:**
- `specgate:project:specgate` - SpecGate 프로젝트
- `specgate:project:ecommerce` - 이커머스 프로젝트  
- `specgate:project:mobile_app` - 모바일 앱 프로젝트

**규칙:**
- 프로젝트명은 소문자, 언더스코어 사용
- 공백 대신 언더스코어 사용
- 특수문자 금지 (하이픈, 언더스코어만 허용)

#### 2.2 문서 유형 라벨 (필수)
```
specgate:type:[문서유형]
```
**표준 문서 유형:**
- `specgate:type:api-design` - API 설계서
- `specgate:type:data-model` - 데이터 모델 설계서
- `specgate:type:architecture` - 아키텍처 설계서
- `specgate:type:security` - 보안 설계서
- `specgate:type:performance` - 성능 설계서

#### 2.3 상태 라벨 (필수)
```
specgate:status:[상태]
```
**표준 상태:**
- `specgate:status:draft` - 초안 (수집 제외)
- `specgate:status:review` - 검토 중 (수집 제외)
- `specgate:status:approved` - 승인됨 (수집 대상)
- `specgate:status:deprecated` - 폐기됨 (수집 제외)

### 3. 선택적 라벨 카테고리

#### 3.1 우선순위 라벨
```
specgate:priority:[우선순위]
```
- `specgate:priority:high` - 높음 (우선 수집)
- `specgate:priority:medium` - 보통
- `specgate:priority:low` - 낮음

#### 3.2 버전 라벨
```
specgate:version:[버전]
```
- `specgate:version:v1.0` - 메이저 버전
- `specgate:version:v1.1` - 마이너 버전
- `specgate:version:latest` - 최신 버전

## 📁 **스페이스 및 폴더 구조**

### 1. 권장 스페이스 구조
```
[프로젝트명] (스페이스)
├── 📋 API Design/
│   ├── User API 설계서
│   ├── Payment API 설계서
│   └── Auth API 설계서
├── 🗄️ Data Model/
│   ├── User 데이터 모델
│   ├── Order 데이터 모델
│   └── Product 데이터 모델
├── 🏗️ Architecture/
│   ├── 마이크로서비스 아키텍처
│   ├── 데이터베이스 아키텍처
│   └── 배포 아키텍처
├── 🔐 Security/
│   ├── 인증 보안 정책
│   ├── 데이터 암호화 정책
│   └── API 보안 가이드
└── ⚡ Performance/
    ├── 캐싱 전략
    ├── 데이터베이스 최적화
    └── 모니터링 가이드
```

### 2. 스페이스 명명 규칙
- **스페이스 키**: 대문자, 언더스코어 사용 (예: `SPECGATE`, `ECOMMERCE`)
- **스페이스 이름**: 의미있는 전체 이름 (예: "SpecGate Project", "E-Commerce Platform")

## 🔍 **문서 수집 정책**

### 1. 기본 수집 규칙

#### 1.1 수집 대상 필터링
```cql
label = "specgate:project:[프로젝트명]" 
AND label = "specgate:status:approved"
AND space = "[스페이스키]"
```

**SpecGate가 현재 사용하는 CQL 생성 로직:**
```python
# 스페이스 지정시
cql = f'label = "{label}" AND space = "{space_key}"'

# 스페이스 미지정시  
cql = f'label = "{label}"'
```

#### 1.2 수집 제외 조건
- `specgate:status:draft` - 초안 문서
- `specgate:status:review` - 검토 중인 문서
- `specgate:status:deprecated` - 폐기된 문서
- 비활성화된 스페이스의 문서
- 권한이 없는 문서

### 2. 수집 우선순위
1. **High Priority**: `specgate:priority:high` 라벨 문서
2. **최신 버전**: `specgate:version:latest` 라벨 문서  
3. **일반 문서**: 기본 조건을 만족하는 모든 문서

### 3. 성능 최적화
- **페이지 제한**: 기본 10개, 최대 100개
- **필드 확장**: `body.storage,version,space,ancestors,metadata.labels`
- **캐싱**: 동일한 검색은 1시간 캐시 (권장)

## 🔐 **권한 및 보안 정책**

### 1. API 접근 권한

#### 1.1 필수 Confluence 권한
- **콘텐츠 읽기**: 모든 대상 스페이스
- **메타데이터 읽기**: 라벨, 버전, 공간 정보 접근
- **검색 권한**: CQL 쿼리 실행

#### 1.2 권장 계정 설정
```json
{
  "account_type": "service_account",
  "permissions": [
    "confluence-content:read",
    "confluence-space:read", 
    "confluence-search:use"
  ],
  "restrictions": [
    "no_write_access",
    "no_admin_access"
  ]
}
```

### 2. 환경변수 보안
```bash
# 필수 환경변수
CONFLUENCE_DOMAIN=your-domain.atlassian.net
CONFLUENCE_EMAIL=service-account@company.com  
CONFLUENCE_API_TOKEN=your-api-token

# 선택적 환경변수
CLIENT_WORK_DIR=/path/to/project
CONFLUENCE_CACHE_TTL=3600  # 1시간
```

**보안 주의사항:**
- API 토큰을 코드에 하드코딩 금지
- 환경변수 파일 (.env) 를 git에서 제외
- 정기적인 API 토큰 갱신 (3개월마다 권장)

## 📊 **모니터링 및 운영**

### 1. 수집 성능 지표
- **수집 성공률**: 95% 이상 유지
- **평균 응답 시간**: 5초 이내
- **에러율**: 5% 미만
- **캐시 적중률**: 60% 이상

### 2. 문서 품질 지표  
- **표준 준수율**: 90% 이상 (90점 이상 문서 비율)
- **필수 라벨 누락**: 0%
- **HITL 검토율**: 10% 미만 (70-89점 문서 비율)

### 3. 알림 및 대응

#### 3.1 자동 알림 조건
- 24시간 내 수집 실패율 20% 초과
- API 토큰 만료 7일 전
- 새로운 프로젝트 라벨 감지
- 비표준 라벨 사용 감지

#### 3.2 대응 절차
1. **수집 실패**: Confluence 연결 상태 확인 → API 토큰 확인 → 권한 확인
2. **품질 저하**: 문서 작성자에게 개선 요청 → Authoring Guide 공유
3. **라벨 불일치**: 관리자에게 표준화 요청 → 정책 문서 업데이트

## 🚀 **구현 가이드**

### 1. 신규 프로젝트 설정

#### 1.1 Confluence 설정
```bash
# 1. 스페이스 생성
Space Name: "MyProject Design Docs"
Space Key: "MYPROJECT"
Description: "MyProject 설계 문서 저장소"

# 2. 권한 설정
Service Account: specgate-service@company.com
Permissions: Read access to space

# 3. 라벨 템플릿 준비
specgate:project:myproject
specgate:type:api-design
specgate:status:approved
```

#### 1.2 SpecGate 설정
```bash
# MCP 설정 (mcp.json)
{
  "mcpServers": {
    "SpecGate": {
      "env": {
        "CONFLUENCE_DOMAIN": "company.atlassian.net",
        "CONFLUENCE_EMAIL": "specgate-service@company.com",
        "CONFLUENCE_API_TOKEN": "...",
        "CLIENT_WORK_DIR": "/path/to/myproject"
      }
    }
  }
}
```

### 2. 테스트 시나리오

#### 2.1 기본 수집 테스트
```bash
# SpecGate 도구 호출 테스트
confluence_fetch(
    label="specgate:project:myproject",
    space_key="MYPROJECT", 
    limit=5
)
```

#### 2.2 라벨 조합 테스트
```bash
# API 설계서만 수집
confluence_fetch(
    label="specgate:type:api-design",
    space_key="MYPROJECT"
)

# 승인된 문서만 수집  
confluence_fetch(
    label="specgate:status:approved",
    space_key="MYPROJECT"
)
```

### 3. 마이그레이션 가이드

#### 3.1 기존 문서 라벨링
```python
# 일괄 라벨 추가 스크립트 (Confluence Admin 권한 필요)
pages_to_update = [
    {"id": "123456", "labels": ["specgate:project:legacy", "specgate:type:api-design"]},
    {"id": "789012", "labels": ["specgate:project:legacy", "specgate:type:data-model"]}
]

for page in pages_to_update:
    confluence.add_labels(page["id"], page["labels"])
```

## 📚 **참조 자료**

### 관련 문서
- [SpecGate Authoring Guide](./authoring-guide.md) - 문서 작성 표준
- [Confluence API 공식 문서](https://developer.atlassian.com/cloud/confluence/rest/v2/)
- [CQL 쿼리 가이드](https://developer.atlassian.com/cloud/confluence/advanced-searching-using-cql/)

### 구현 코드 참조
- `development/mcp-server/confluence_fetch/client.py` - CQL 쿼리 생성 로직
- `development/mcp-server/confluence_fetch/service.py` - 수집 서비스 로직
- `development/mcp-server/confluence_fetch/transformer.py` - 데이터 변환 로직

## ❓ **FAQ**

**Q: 기존 Confluence에 이미 다른 라벨 체계가 있다면?**
A: SpecGate 라벨과 기존 라벨을 병행 사용 가능. `specgate:` prefix로 구분됨.

**Q: 라벨을 추가하려면 어떤 권한이 필요한가?**
A: 해당 페이지의 편집 권한 또는 스페이스 관리자 권한.

**Q: 하나의 문서에 여러 프로젝트 라벨을 붙일 수 있나?**  
A: 가능하지만 권장하지 않음. 문서 소유권이 명확하지 않아 관리 복잡도 증가.

**Q: CQL 쿼리가 너무 복잡해지면?**
A: 현재는 단순 라벨 검색만 지원. 복잡한 검색은 향후 확장 예정.

---
**SpecGate Team** | 버전 1.0 | 생성일: 2024-01-15
