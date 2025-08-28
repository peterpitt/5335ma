import SwiftUI
import UserNotifications

@main
struct SwiftUI539App: App {
    @StateObject private var store = StatsStore()
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(store)
                .task {
                    await store.refresh()
                    await NotificationScheduler.ensureSchedule()
                }
        }
    }
}

enum AppConfig {
    // Replace with your GitHub Pages URL after you deploy, e.g.:
    // static let statsURL = URL(string: "https://<username>.github.io/vibe-539-app-starter/539_stats.json")!
    static let statsURL = URL(string: "https://example.com/539_stats.json")!
}
