import SwiftUI
import Charts

struct ContentView: View {
    @EnvironmentObject var store: StatsStore

    var body: some View {
        NavigationView {
            ScrollView {
                if let s = store.stats {
                    VStack(alignment: .leading, spacing: 16) {
                        Text("更新時間：\\(s.generated_at)")
                            .font(.caption)
                            .foregroundStyle(.secondary)

                        GroupBox("Top 共現三連號（全期間）") {
                            VStack(alignment: .leading, spacing: 8) {
                                Text("No.1：\\(s.top_trio.numbers.map { String(format: "%02d", $0) }.joined(separator: ", ")) 次數 \\(s.top_trio.count)")
                                    .font(.headline)
                                Divider()
                                ForEach(Array(s.top_trio.top5.prefix(5)).indices, id: \\.self) { i in
                                    let entry = s.top_trio.top5[i]
                                    let trio = entry[0]
                                    let cnt = entry[1][0]
                                    HStack {
                                        Text("#\\(i+1) \\(trio.map{ String(format: \"%02d\", $0) }.joined(separator: \", \"))")
                                        Spacer()
                                        Text("x\\(cnt)")
                                    }
                                }
                            }
                        }

                        GroupBox("下期最常一起出現的兩連號（條件：上期出現 Top 三連號）") {
                            VStack(alignment: .leading, spacing: 8) {
                                Text("No.1：\\(s.next_draw_top_pair_given_trio.pair.map { String(format: \"%02d\", $0) }.joined(separator: \", \")) 次數 \\(s.next_draw_top_pair_given_trio.count)")
                                    .font(.headline)
                                Divider()
                                ForEach(Array(s.next_draw_top_pair_given_trio.top5.prefix(5)).indices, id: \\.self) { i in
                                    let entry = s.next_draw_top_pair_given_trio.top5[i]
                                    let pair = entry[0]
                                    let cnt = entry[1][0]
                                    HStack {
                                        Text("#\\(i+1) \\(pair.map{ String(format: \"%02d\", $0) }.joined(separator: \", \"))")
                                        Spacer()
                                        Text("x\\(cnt)")
                                    }
                                }
                            }
                        }

                        GroupBox("每月首抽『第二個號碼』分佈（Top2）") {
                            VStack(alignment: .leading, spacing: 8) {
                                Text("最常見：\\(s.monthly_first_draw_second_number.top2.map { String(format: \"%02d\", $0) }.joined(separator: \", \"))")
                                    .font(.headline)
                                let items = s.monthly_first_draw_second_number.counts
                                    .map { (Int($0.key) ?? 0, $0.value) }
                                    .sorted { $0.0 < $1.0 }
                                Chart(items, id: \\.0) { item in
                                    BarMark(x: .value("號碼", item.0), y: .value("次數", item.1))
                                }
                                .frame(height: 220)
                            }
                        }

                        Text("資料來源：")
                            .font(.subheadline).bold()
                        ForEach(store.stats?.source_urls ?? [], id: \\.self) { url in
                            Text(url).font(.footnote).foregroundStyle(.secondary)
                        }
                    }
                    .padding()
                } else if let err = store.error {
                    ContentUnavailableView("連線失敗", systemImage: "wifi.slash", description: Text(err))
                        .padding()
                } else {
                    ProgressView("載入中…").padding()
                }
            }
            .navigationTitle("今彩539 助手")
            .toolbar {
                Button {
                    Task { await store.refresh() }
                } label: {
                    Label("Refresh", systemImage: "arrow.clockwise")
                }
            }
        }
    }
}
