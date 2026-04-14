import Foundation

/// A normalized, view-friendly representation of the weekly Torah portion.
public struct Parasha: Sendable, Identifiable, Hashable {
    public var id: String { ref }

    /// The Hebrew display name (e.g. "בראשית", "נח", "לך לך").
    public let nameHebrew: String
    /// The English display name (e.g. "Bereshit", "Noach", "Lech Lecha").
    public let nameEnglish: String
    /// The canonical Sefaria reference, e.g. `"Genesis 1:1-6:8"`.
    public let ref: String
    /// The Hebrew canonical reference, e.g. `"בראשית א׳:א׳-ו׳:ח׳"`.
    public let heRef: String
    /// The verses that make up the parasha, in reading order.
    public let verses: [ParashaVerse]
    /// The optional haftarah reference (Hebrew form).
    public let haftarahHeRef: String?
    /// The optional haftarah reference (English form).
    public let haftarahRef: String?

    public init(
        nameHebrew: String,
        nameEnglish: String,
        ref: String,
        heRef: String,
        verses: [ParashaVerse],
        haftarahHeRef: String? = nil,
        haftarahRef: String? = nil
    ) {
        self.nameHebrew = nameHebrew
        self.nameEnglish = nameEnglish
        self.ref = ref
        self.heRef = heRef
        self.verses = verses
        self.haftarahHeRef = haftarahHeRef
        self.haftarahRef = haftarahRef
    }

    /// Verses grouped by chapter, with chapters in ascending order.
    public var chapters: [(chapter: Int, verses: [ParashaVerse])] {
        let grouped = Dictionary(grouping: verses, by: \.chapter)
        return grouped
            .sorted { $0.key < $1.key }
            .map { ($0.key, $0.value.sorted { $0.verse < $1.verse }) }
    }
}

/// A single verse of a parasha with both Hebrew text and optional English
/// translation.
public struct ParashaVerse: Sendable, Identifiable, Hashable {
    public var id: String { "\(chapter):\(verse)" }
    public let chapter: Int
    public let verse: Int
    public let hebrew: String
    public let english: String?

    public init(chapter: Int, verse: Int, hebrew: String, english: String? = nil) {
        self.chapter = chapter
        self.verse = verse
        self.hebrew = hebrew
        self.english = english
    }
}
