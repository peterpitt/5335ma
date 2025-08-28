import Foundation
import UserNotifications

enum NotificationScheduler {
    static func ensureSchedule() async {
        let center = UNUserNotificationCenter.current()
        let granted = try? await center.requestAuthorization(options: [.alert, .badge, .sound])
        guard granted == true else { return }
        // Clear existing
        await center.removeAllPendingNotificationRequests()
        // Schedule Mon-Sat 22:10 local reminder
        for weekday in 2...7 { // Monday=2 ... Saturday=7
            var date = DateComponents()
            date.weekday = weekday
            date.hour = 22
            date.minute = 10
            let trigger = UNCalendarNotificationTrigger(dateMatching: date, repeats: true)
            let content = UNMutableNotificationContent()
            content.title = "今彩539 更新時間到"
            content.body = "點開 App 以更新今晚開獎與統計（iOS 限制無法準點後台抓取）。"
            let req = UNNotificationRequest(identifier: "reminder-\\(weekday)", content: content, trigger: trigger)
            await center.add(req)
        }
    }
}
