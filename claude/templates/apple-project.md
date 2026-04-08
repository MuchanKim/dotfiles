# {{PROJECT_NAME}} — Project Rules

## Project Overview
- **Platform:** {{PLATFORM}}
- **Distribution:** {{DISTRIBUTION}}
- **UI Framework:** {{UI_FRAMEWORK}}
- **Minimum OS:** {{MIN_OS}}
- **Architecture:** {{ARCHITECTURE}}

## SwiftUI View Rules
- When a view body's Stack nesting depth exceeds 2 levels, extract inner stacks into separate subviews immediately.
- Each subview should have a single, clear responsibility.
- Prefer small, composable views over deeply nested view trees.
- Example — this is TOO deep:
  ```swift
  // BAD: 3 levels of stack nesting
  VStack {
      HStack {
          VStack {
              Text("Name")
              Text("Detail")
          }
      }
  }
  ```
  ```swift
  // GOOD: extract inner content into a subview
  VStack {
      HStack {
          NameDetailView()
      }
  }
  ```

## Code Style
- Follow Swift API Design Guidelines for all naming.
- Use Swift Concurrency (async/await, actors) over GCD/completion handlers.
- Prefer value types (struct, enum) over reference types unless shared mutable state is required.
- Mark classes as `final` by default.
- Use `private` access control by default; widen only when needed.

## App Store Compliance ({{DISTRIBUTION}})
{{#IF_APPSTORE}}
- **In-App Purchase:** All digital content/subscriptions MUST use StoreKit. No external payment links or prompts.
- **Privacy:**
  - Declare ALL data collection in App Privacy (nutrition labels) accurately.
  - Request permissions (camera, location, contacts, etc.) only when the feature is actively used — never on launch.
  - Include a privacy policy URL.
- **Content:**
  - User-generated content requires reporting/blocking mechanisms.
  - Age rating must match actual content.
- **Functionality:**
  - App must be fully functional at review time — no placeholder screens, broken links, or demo modes.
  - Do not mention competing platforms (Android, Windows) in UI text.
  - No hidden features or undocumented URL schemes.
- **Design:**
  - Do not mimic system UI (e.g., fake volume/battery indicators).
  - Support Dynamic Type and standard accessibility features.
- **Review before every submission:** Walk through App Store Review Guidelines (https://developer.apple.com/app-store/review/guidelines/) for any new feature.
{{/IF_APPSTORE}}
{{#IF_NOT_APPSTORE}}
- Distribution is not App Store — standard Apple platform guidelines apply but App Store Review is not a constraint.
{{/IF_NOT_APPSTORE}}

## Accessibility
- All interactive elements must have accessibility labels.
- Support Dynamic Type — never use fixed font sizes.
- Ensure minimum touch target of 44x44pt.
- Test with VoiceOver for all primary user flows.

## Code Signing & Provisioning
- Never hardcode signing identities or provisioning profiles in source.
- Use automatic signing for development; manual signing for release.
- Never commit certificates, .p12, or .mobileprovision files to the repository.

## Testing
- Write unit tests for all business logic and view models.
- Use Swift Testing framework (`@Test`, `#expect`) over XCTest for new tests.
- UI tests for critical user flows only — keep them focused and fast.
