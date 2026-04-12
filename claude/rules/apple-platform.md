---
paths: ["**/*.swift", "**/*.xcodeproj/**", "**/*.xcworkspace/**"]
---

# Apple Platform Development Rules

## MCP
- Use **apple-docs MCP** when consulting Apple documentation or resolving framework errors.
- Register at project level if not present:
  `claude mcp add apple-docs --project -- npx -y @kimsungwhee/apple-docs-mcp@latest`

## Build Verification
- After any code modification, run `xcodebuild` to verify no build errors.

## Framework
- SwiftUI is the primary UI framework. UIKit is acceptable when SwiftUI cannot achieve the goal (e.g., `UIViewRepresentable` wrappers).

## Credentials
- Store all tokens and secrets in Keychain. Never use UserDefaults for sensitive data.

## Swift Concurrency — Approachable Concurrency 환경
- `SWIFT_APPROACHABLE_CONCURRENCY = YES` 프로젝트에서 Obj-C protocol delegate 메서드에 `nonisolated`, `@preconcurrency`, `MainActor.assumeIsolated`를 수동으로 붙이지 않는다
- 컴파일러가 @MainActor 클래스의 Obj-C delegate 메서드를 자동으로 MainActor-isolated로 추론한다
- 수동 annotation은 컴파일러의 추론을 override하여 오히려 문제를 만든다
- 순수 데이터 struct가 `Sendable`을 명시적으로 conform하면 default MainActor isolation이 자동 suppress된다 (SE-0466)
- 테스트 타겟에도 `SWIFT_DEFAULT_ACTOR_ISOLATION` 설정이 메인 타겟과 일치해야 한다

## Extension 파일 분리 기준
- 외부 프레임워크 import가 추가되면 → `타입+컨텍스트.swift`로 분리
- 외부 의존 없고 같은 파일에서 private 멤버를 사용하면 → 같은 파일에 `// MARK: -`로 구분
- 외부 의존 없고 private 멤버도 안 쓰면 → 같은 파일 선호 (파일이 300줄 넘으면 분리 검토)
- 같은 파일 내 extension이 외부에 노출할 필요 없는 기능이면 → `private extension`으로 선언
- 하나의 타입이 300줄을 넘기면 → 기능 단위로 `타입+기능.swift` 분리 검토

## Access Control
- **private 우선 원칙**: 모든 프로퍼티, 메서드는 가능한 한 가장 좁은 접근 수준으로 선언. 외부에서 쓸 이유가 없으면 `private`.
- 같은 파일 내에서만 접근하면 `private`, 같은 모듈 내 다른 파일에서 접근하면 `internal` (기본값이므로 생략 가능)
- extension 전체가 외부 노출 불필요하면 `private extension`으로 선언
- 테스트에서 접근해야 하는 경우 `@testable import`로 `internal`에 접근 가능하므로, 테스트를 위해 접근 수준을 올리지 않는다

## Documentation Comments (Based on Swift API Design Guidelines)

### Format
- Use `///` only. Never use `/** */`.
- For non-documentation comments, use `//` only. Never use `/* */`.

### Summary Rules
- Start with a single sentence and end with a period.
- Pattern varies by declaration type:
  - **Function/Method**: What it does — `/// Sorts the collection in ascending order.`
  - **Initializer**: What it creates — `/// Creates a circle overlay with the given center and radius.`
  - **Property**: What it is — `/// The center coordinate of the overlay.`
  - **Type**: What the type is — `/// A wrapper around NMFMarker that manages map markers.`
- A good summary is often all you need. Omit null effects and Void returns.

### Where to Write
- All public/package/internal type declarations
- Methods and properties with non-obvious behavior
- Initializers with automatic computation or side effects
- Add `- Parameter:` when parameter meaning is not clear from the name alone

### Where NOT to Write (Don't repeat what the code already says)
- Self-explanatory properties/methods — `isHidden`, `removeFromMap()`, etc.
- Overrides that don't change behavior (inherits parent documentation)
- Private members with sufficiently descriptive names
- Obvious protocol conformance extensions

### Structured Documentation Tags
- Tag order: `- Parameter(s):` → `- Returns:` → `- Throws:`
- Omit tags when the summary alone conveys parameter/return meaning.
- One parameter: `/// - Parameter element: The element to insert.`
- Multiple parameters:
  ```swift
  /// - Parameters:
  ///   - x: The horizontal coordinate.
  ///   - y: The vertical coordinate.
  ```
- `- Complexity:`: Recommended for collection/algorithm methods.

### Anti-patterns
- **Tautology**: Restating code as comment — `/// The user's name.` + `var userName: String`
- **"This method" prefix**: `/// This method sorts...` → `/// Sorts the collection.`
- **What comments**: Don't comment "what" if code already expresses it. Only comment "why".
- **Stale comments**: A wrong comment is worse than no comment. Update comments when code changes.

## Subview Extraction Rules
- When a VStack/HStack/ZStack nests **2+ levels deep**, extract the inner content into a named subview.
- Subviews communicate via: **Binding** (two-way state), **closure callbacks** (actions), or **plain properties** (read-only data).
- Do NOT pass the entire ViewModel to a subview. Pass only the specific data/actions it needs.

## App Store Compliance (General)

These apply to any App Store distributed app:
- Display "AI-generated" labels on all AI output.
- Gracefully degrade AI features on unsupported devices.
- Provide in-app account deletion if the app has login (Guideline 5.1.1v).
- All features must work at submission — no placeholder/TODO screens (Guideline 2.1).
- Re-evaluate ATT requirements when adding any analytics/tracking SDK.
