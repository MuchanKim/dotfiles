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
