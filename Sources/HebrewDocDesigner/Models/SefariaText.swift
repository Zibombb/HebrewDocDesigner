import Foundation

/// Response from `GET /api/v3/texts/{tref}` on Sefaria.
///
/// The response contains one or more text versions (Hebrew source, English
/// translations, etc.). Text can be either a flat list of verses or a nested
/// list of chapters and verses depending on the range that was requested.
public struct SefariaTextResponse: Codable, Sendable {
    public let ref: String?
    public let heRef: String?
    public let sections: [String]?
    public let toSections: [String]?
    public let versions: [SefariaVersion]
    public let book: String?
    public let heTitle: String?
    public let title: String?
    public let type: String?
    public let categories: [String]?

    public init(
        ref: String?,
        heRef: String?,
        sections: [String]?,
        toSections: [String]?,
        versions: [SefariaVersion],
        book: String? = nil,
        heTitle: String? = nil,
        title: String? = nil,
        type: String? = nil,
        categories: [String]? = nil
    ) {
        self.ref = ref
        self.heRef = heRef
        self.sections = sections
        self.toSections = toSections
        self.versions = versions
        self.book = book
        self.heTitle = heTitle
        self.title = title
        self.type = type
        self.categories = categories
    }
}

/// A specific textual version returned by the Sefaria API (e.g. the Hebrew
/// Masoretic text with ta'amei hamikra, or a specific English translation).
public struct SefariaVersion: Codable, Sendable {
    public let language: String?
    public let versionTitle: String?
    public let versionSource: String?
    public let text: TextContent?
    public let direction: String?
    public let license: String?

    public init(
        language: String? = nil,
        versionTitle: String? = nil,
        versionSource: String? = nil,
        text: TextContent? = nil,
        direction: String? = nil,
        license: String? = nil
    ) {
        self.language = language
        self.versionTitle = versionTitle
        self.versionSource = versionSource
        self.text = text
        self.direction = direction
        self.license = license
    }
}

/// Recursive representation of Sefaria's `text` field, which may be either a
/// string (a single verse), a flat array (a single chapter), or a nested
/// array (multi-chapter range).
public indirect enum TextContent: Codable, Sendable, Hashable {
    case string(String)
    case array([TextContent])

    public init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if container.decodeNil() {
            self = .array([])
            return
        }
        if let s = try? container.decode(String.self) {
            self = .string(s)
        } else if let arr = try? container.decode([TextContent].self) {
            self = .array(arr)
        } else {
            throw DecodingError.typeMismatch(
                TextContent.self,
                .init(
                    codingPath: decoder.codingPath,
                    debugDescription: "Expected Sefaria text to be a string or an array."
                )
            )
        }
    }

    public func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        switch self {
        case .string(let s):
            try container.encode(s)
        case .array(let arr):
            try container.encode(arr)
        }
    }

    /// Flattens nested content into a list of plain strings (verses).
    public func flatten() -> [String] {
        switch self {
        case .string(let s):
            return [s]
        case .array(let arr):
            return arr.flatMap { $0.flatten() }
        }
    }
}
