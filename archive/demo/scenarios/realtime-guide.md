# SpecGate 실시간 가이드 시뮬레이션

## 🎯 개발자 코드 작성 시 실시간 지원

### 시나리오 1: 올바른 코드 작성

```
┌─────────────────────────────────────────────────────────┐
│ 📄 UserController.java - SpecGate 룰 적용됨             │
├─────────────────────────────────────────────────────────┤
│ @RestController  ← 🚪 SpecGate 룰 적용                 │
│ @RequestMapping("/api/v1/users")                        │
│ public class UserController {                           │
│                                                         │
│   @GetMapping("/{id}")  ← RESTful 패턴 제안            │
│   public ResponseEntity<User> getUser(                  │
│       @PathVariable Long id) {                          │
│     // SpecGate가 제안한 스니펫                          │
│     return userService.findById(id);                    │
│   }                                                      │
│                                                         │
│   @PostMapping  ← POST 메서드 자동완성                  │
│   public ResponseEntity<User> createUser(               │
│       @RequestBody User user) {                         │
│     // SpecGate가 제안한 스니펫                          │
│     return userService.save(user);                      │
│   }                                                      │
│ }                                                        │
│                                                         │
│ 💡 SpecGate: RULE-API-001 적용됨 - RESTful 원칙 준수    │
│ 💡 SpecGate: RULE-API-002 적용됨 - 표준 응답 형식 사용  │
│ 💡 SpecGate: RULE-ARCH-001 적용됨 - Service 계층 호출   │
└─────────────────────────────────────────────────────────┘
```

### 시나리오 2: 스니펫 자동완성

```
┌─────────────────────────────────────────────────────────┐
│ 💡 SpecGate 스니펫 제안                                 │
├─────────────────────────────────────────────────────────┤
│ @GetMapping("/{id}")                                    │
│ public ResponseEntity<User> getUser(@PathVariable Long id) { │
│     User user = userService.findById(id);               │
│     return ResponseEntity.ok(user);                     │
│ }                                                        │
│                                                         │
│ [적용하기] [다른 패턴 보기] [도움말]                    │
└─────────────────────────────────────────────────────────┘
```

### 시나리오 3: 실시간 가이드

```
┌─────────────────────────────────────────────────────────┐
│ 💡 SpecGate 실시간 가이드                               │
├─────────────────────────────────────────────────────────┤
│ RULE-API-001: RESTful 원칙 준수                         │
│                                                         │
│ 현재 작성 중인 메서드가 RESTful 원칙을 잘 따르고 있습니다. │
│                                                         │
│ ✅ GET /users/{id} - 리소스 조회                        │
│ ✅ @PathVariable 사용 - 경로 변수 처리                  │
│ ✅ ResponseEntity 반환 - 표준 응답 형식                 │
│                                                         │
│ [더 자세히 보기] [다음 단계]                            │
└─────────────────────────────────────────────────────────┘
```
