import Foundation

@MainActor
final class StatsStore: ObservableObject {
    @Published var stats: StatsPayload? = nil
    @Published var error: String? = nil

    func refresh() async {
        do {
            let (data, _) = try await URLSession.shared.data(from: AppConfig.statsURL)
            let decoded = try JSONDecoder().decode(StatsPayload.self, from: data)
            self.stats = decoded
            self.error = nil
        } catch {
            self.error = "讀取失敗，請檢查網路或設定的 stats URL。\\n\\(error.localizedDescription)"
            // Fallback: load bundled sample
            if let url = Bundle.main.url(forResource: "539_stats", withExtension: "json"),
               let data = try? Data(contentsOf: url),
               let decoded = try? JSONDecoder().decode(StatsPayload.self, from: data) {
                self.stats = decoded
            }
        }
    }
}
