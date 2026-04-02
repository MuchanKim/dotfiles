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

## Project Structure

Separate source code and resources at the top level:

```
AppName/
├── Sources/          # All Swift source files
│   ├── App/          # Entry point, Coordinator, Factory
│   ├── Models/
│   ├── Services/
│   ├── Protocols/
│   ├── Utilities/
│   ├── Theme/
│   └── Presentation/ # Feature modules (see below)
├── Resources/        # Assets, localization, non-code files
└── Tests/
```

## Architecture: MVVM + Coordinator + Factory

### Coordinator
- `AppCoordinator` manages navigation state via a published route array.
- `AppRoute` enum defines all navigable destinations.
- Views trigger navigation through the coordinator, not via direct `NavigationLink(destination:)`.

```swift
@MainActor @Observable
final class AppCoordinator {
    var path: [AppRoute] = []
    func push(_ route: AppRoute) { path.append(route) }
    func pop() { path.removeLast() }
    func popToRoot() { path.removeAll() }
}
```

### Factory
- `ModuleFactory` is the single DI entry point. It creates views with injected dependencies.
- Define a protocol (`ModuleFactoryProtocol`) for testability.
- Use lazy properties for shared instances (ViewModels, managers).

```swift
@MainActor
protocol ModuleFactoryProtocol {
    func makeFeedView() -> FeedView
    func makeDetailView(item: Item) -> DetailView
}
```

### ViewModel
- One ViewModel per feature screen.
- Mark `@MainActor @Observable final class`.
- Use `private(set) var` for state exposed to views.
- Constructor-based dependency injection.
- Async/await for all asynchronous work.

### View ↔ ViewModel Binding
- View owns ViewModel via `@State private var viewModel = SomeViewModel()`.
- View reads state reactively; calls ViewModel methods for actions.
- No business logic in Views — delegate to ViewModel.

## Feature Module Structure

Each feature is a self-contained folder under `Presentation/`:

```
Presentation/
└── Feed/
    ├── View/
    │   ├── FeedView.swift           # Main view
    │   └── SubView/
    │       ├── FeedCardView.swift   # Extracted subview
    │       └── FeedHeaderView.swift
    └── ViewModel/
        └── FeedViewModel.swift
```

## Subview Extraction Rules
- When a VStack/HStack/ZStack nests **2+ levels deep**, extract the inner content into a named subview file under `SubView/`.
- Subviews communicate via: **Binding** (two-way state), **closure callbacks** (actions), or **plain properties** (read-only data).
- Do NOT pass the entire ViewModel to a subview. Pass only the specific data/actions it needs.

## App Store Compliance (General)

These apply to any App Store distributed app:
- Display "AI-generated" labels on all AI output.
- Gracefully degrade AI features on unsupported devices.
- Provide in-app account deletion if the app has login (Guideline 5.1.1v).
- All features must work at submission — no placeholder/TODO screens (Guideline 2.1).
- Re-evaluate ATT requirements when adding any analytics/tracking SDK.
