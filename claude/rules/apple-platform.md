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

## Swift Concurrency — Approachable Concurrency
- In `SWIFT_APPROACHABLE_CONCURRENCY = YES` projects, do NOT manually add `nonisolated`, `@preconcurrency`, or `MainActor.assumeIsolated` to Obj-C protocol delegate methods.
- The compiler automatically infers MainActor isolation for Obj-C delegate methods in @MainActor classes.
- Manual annotations override the compiler's inference and can cause issues.
- Pure data structs that explicitly conform to `Sendable` automatically suppress default MainActor isolation (SE-0466).
- Test targets must match `SWIFT_DEFAULT_ACTOR_ISOLATION` setting of the main target.

## Extension File Separation
- If an external framework import is added → separate into `Type+Context.swift`
- No external dependency + uses private members in the same file → keep in same file with `// MARK: -`
- No external dependency + no private member access → prefer same file (consider splitting if >300 lines)
- If an extension in the same file doesn't need external exposure → declare as `private extension`
- If a single type exceeds 300 lines → consider splitting by feature into `Type+Feature.swift`

## Access Control
- **Prefer private**: Declare all properties and methods at the narrowest access level possible. Use `private` unless there's a reason to expose.
- Same-file only access → `private`. Cross-file within same module → `internal` (default, can be omitted).
- If an entire extension doesn't need external exposure → declare as `private extension`.
- For test access, use `@testable import` to reach `internal` — never widen access level just for tests.

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
