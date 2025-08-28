
# iOS SwiftUI App — 今彩539 助手
- Open Xcode > create iOS App (SwiftUI, iOS 16+), product name `SwiftUI539App`.
- Replace the auto-created files with those under `ios/SwiftUI539App/`.
- Add `539_stats.json` to the app target (Copy Bundle Resources).
- Edit `AppConfig.statsURL` to your published GitHub Pages `539_stats.json` URL.
- Run. For App Store: add App Icons, Privacy manifest (no tracking), and fill metadata.
- Background fetch at exact 22:00 is not guaranteed by iOS; we schedule a local reminder at 22:10 Mon–Sat so you can open the app and pull fresh data.
