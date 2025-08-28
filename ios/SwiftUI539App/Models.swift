import Foundation

struct TrioStat: Codable, Identifiable {
    var id: String { numbers.map(String.init).joined(separator: "-") }
    let numbers: [Int]
    let count: Int
}

struct PairStat: Codable, Identifiable {
    var id: String { numbers.map(String.init).joined(separator: "-") }
    let numbers: [Int]
    let count: Int
}

struct MonthlySecond: Codable {
    let counts: [String:Int]  // number -> count
    let top2: [Int]
}

struct StatsPayload: Codable {
    let generated_at: String
    let source_urls: [String]
    let num_draws: Int
    let top_trio: TopTrio
    let next_draw_top_pair_given_trio: NextPair
    let monthly_first_draw_second_number: MonthlySecond

    struct TopTrio: Codable {
        let numbers: [Int]
        let count: Int
        let top5: [[[Int]]]
    }
    struct NextPair: Codable {
        let trio: [Int]
        let pair: [Int]
        let count: Int
        let top5: [[[Int]]]
    }
}
