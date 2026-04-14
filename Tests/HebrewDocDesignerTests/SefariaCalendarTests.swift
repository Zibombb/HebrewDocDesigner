import XCTest
@testable import HebrewDocDesigner

final class SefariaCalendarTests: XCTestCase {
    func test_decodesCalendarResponse_andFindsParasha() throws {
        let json = """
        {
          "date": "2024-01-20",
          "timezone": "Asia/Jerusalem",
          "calendar_items": [
            {
              "title": {"en": "Parashat Hashavua", "he": "פרשת השבוע"},
              "displayValue": {"en": "Shemot", "he": "שמות"},
              "url": "Exodus.1.1-6.1",
              "ref": "Exodus 1:1-6:1",
              "heRef": "שמות א׳:א׳-ו׳:א׳",
              "order": 1,
              "category": "Tanakh"
            },
            {
              "title": {"en": "Haftarah", "he": "הפטרה"},
              "displayValue": {"en": "Isaiah 27:6-28:13; 29:22-23", "he": "ישעיהו כ״ז:ו׳-כ״ח:י״ג; כ״ט:כ״ב-כ״ג"},
              "url": "Isaiah.27.6-28.13",
              "ref": "Isaiah 27:6-28:13",
              "heRef": "ישעיהו כ״ז:ו׳-כ״ח:י״ג",
              "order": 2,
              "category": "Tanakh"
            }
          ]
        }
        """.data(using: .utf8)!

        let decoded = try JSONDecoder().decode(SefariaCalendarResponse.self, from: json)
        XCTAssertEqual(decoded.calendarItems.count, 2)

        let parasha = try XCTUnwrap(decoded.parashaItem)
        XCTAssertEqual(parasha.displayValue.he, "שמות")
        XCTAssertEqual(parasha.displayValue.en, "Shemot")
        XCTAssertEqual(parasha.ref, "Exodus 1:1-6:1")

        let haftarah = try XCTUnwrap(decoded.haftarahItem)
        XCTAssertEqual(haftarah.ref, "Isaiah 27:6-28:13")
    }

    func test_parashaItem_returnsNilWhenMissing() throws {
        let json = """
        {
          "date": "2024-01-20",
          "calendar_items": [
            {
              "title": {"en": "Daf Yomi", "he": "דף יומי"},
              "displayValue": {"en": "Kiddushin 31", "he": "קידושין ל״א"},
              "ref": "Kiddushin 31"
            }
          ]
        }
        """.data(using: .utf8)!

        let decoded = try JSONDecoder().decode(SefariaCalendarResponse.self, from: json)
        XCTAssertNil(decoded.parashaItem)
    }
}
