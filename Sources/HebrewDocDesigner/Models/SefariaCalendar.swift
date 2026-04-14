import Foundation

/// Response from `GET https://www.sefaria.org/api/calendars`.
///
/// Contains the learning calendar for a given day, including the weekly
/// Torah portion (Parashat Hashavua), Haftarah, daily Mishnah and more.
public struct SefariaCalendarResponse: Codable, Sendable {
    public let date: String?
    public let timezone: String?
    public let calendarItems: [CalendarItem]

    public init(
        date: String?,
        timezone: String?,
        calendarItems: [CalendarItem]
    ) {
        self.date = date
        self.timezone = timezone
        self.calendarItems = calendarItems
    }

    enum CodingKeys: String, CodingKey {
        case date
        case timezone
        case calendarItems = "calendar_items"
    }
}

/// A single item returned by the Sefaria calendar endpoint (e.g. the weekly
/// parasha, the haftarah, daf yomi, etc.).
public struct CalendarItem: Codable, Sendable, Identifiable, Hashable {
    public var id: String {
        (title.en ?? "") + "|" + (displayValue.en ?? "") + "|" + (ref ?? "")
    }

    public let title: LocalizedValue
    public let displayValue: LocalizedValue
    public let url: String?
    public let ref: String?
    public let heRef: String?
    public let order: Int?
    public let category: String?
    public let description: LocalizedValue?
    public let extraDetails: [String: String]?

    public init(
        title: LocalizedValue,
        displayValue: LocalizedValue,
        url: String? = nil,
        ref: String? = nil,
        heRef: String? = nil,
        order: Int? = nil,
        category: String? = nil,
        description: LocalizedValue? = nil,
        extraDetails: [String: String]? = nil
    ) {
        self.title = title
        self.displayValue = displayValue
        self.url = url
        self.ref = ref
        self.heRef = heRef
        self.order = order
        self.category = category
        self.description = description
        self.extraDetails = extraDetails
    }

    enum CodingKeys: String, CodingKey {
        case title
        case displayValue
        case url
        case ref
        case heRef
        case order
        case category
        case description
        case extraDetails
    }
}

/// A value that has both an English and Hebrew form.
public struct LocalizedValue: Codable, Sendable, Hashable {
    public let en: String?
    public let he: String?

    public init(en: String? = nil, he: String? = nil) {
        self.en = en
        self.he = he
    }
}

public extension SefariaCalendarResponse {
    /// Returns the calendar item representing the weekly Torah portion, if
    /// present. The API usually returns the parasha as one of several items,
    /// so we look it up by its canonical title.
    var parashaItem: CalendarItem? {
        calendarItems.first { item in
            if let en = item.title.en?.lowercased(),
               en.contains("parashat") || en.contains("parasha") {
                return true
            }
            if item.title.he == "פרשת השבוע" {
                return true
            }
            return false
        }
    }

    /// The haftarah reading paired with the weekly parasha, if present.
    var haftarahItem: CalendarItem? {
        calendarItems.first { item in
            if let en = item.title.en?.lowercased(), en.contains("haftar") {
                return true
            }
            if item.title.he?.contains("הפטר") == true {
                return true
            }
            return false
        }
    }
}
