---
paths: ["**/*.swift"]
---

# Swift Naming Conventions

Based on Apple Swift API Design Guidelines. **Clarity at the point of use** is the top priority.

## Case Rules
- **UpperCamelCase**: Types (struct/class/enum), Protocols
- **lowerCamelCase**: Functions, variables, properties, enum cases, constants (let)

## Types / Protocols
- Types are nouns: `UserProfile`, `NetworkManager`, `ConnectionState`
- Protocols describing capability use `-able/-ible/-ing`: `Equatable`, `Sendable`, `ProgressReporting`
- Protocols describing roles use nouns: `DataSource`, `Collection`

## Functions / Methods
- With side effects — imperative verb: `array.sort()`, `list.append(item)`
- Without side effects — noun phrase or `-ed/-ing`: `array.sorted()`, `x.distance(to: y)`
- Factory methods use `make` prefix: `makeIterator()`, `makeBody()`

## Variables / Properties
- Name by role, never repeat the type: `greeting: String` O, `string: String` X
- Booleans use `is/has/can/should/will` prefix: `isEmpty`, `hasContent`, `canEdit`

## Enum Cases
- lowerCamelCase: `.connecting`, `.north`, `.idle`

## Abbreviations
- Only widely accepted abbreviations: URL, HTTP, ID, JSON, API
- At the start of a name: all lowercase (`urlString`, `httpMethod`, `id`)
- In the middle or end of a name: all uppercase (`baseURL`, `userID`, `toJSON`)
- Arbitrary abbreviations are forbidden: `btn` X -> `button` O, `bg` X -> `background` O

## Files
- Filename = primary type name: `UserProfile.swift`
- Extensions: `Type+Protocol.swift` (e.g., `MapCoordinate+NMapsMap.swift`)
- One primary type per file.
