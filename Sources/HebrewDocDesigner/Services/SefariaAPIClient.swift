import Foundation

/// Abstraction for the Sefaria REST API. Using a protocol makes the
/// ``ParashaViewModel`` easy to test with an in-memory mock.
public protocol SefariaAPIClientProtocol: Sendable {
    func fetchCalendar(diaspora: Bool, date: Date?) async throws -> SefariaCalendarResponse
    func fetchText(ref: String) async throws -> SefariaTextResponse
    func fetchWeeklyParasha(diaspora: Bool, date: Date?) async throws -> Parasha
}

public extension SefariaAPIClientProtocol {
    func fetchCalendar() async throws -> SefariaCalendarResponse {
        try await fetchCalendar(diaspora: true, date: nil)
    }

    func fetchWeeklyParasha() async throws -> Parasha {
        try await fetchWeeklyParasha(diaspora: true, date: nil)
    }
}

/// HTTP client for `https://www.sefaria.org`.
///
/// The client is implemented as an `actor` so all network activity is
/// serialized and the underlying `URLSession` / `JSONDecoder` state is
/// isolated from the rest of the app.
public actor SefariaAPIClient: SefariaAPIClientProtocol {
    public static let defaultBaseURL = URL(string: "https://www.sefaria.org")!

    private let baseURL: URL
    private let session: URLSession
    private let decoder: JSONDecoder

    public init(
        baseURL: URL = SefariaAPIClient.defaultBaseURL,
        session: URLSession = .shared
    ) {
        self.baseURL = baseURL
        self.session = session
        self.decoder = JSONDecoder()
    }

    // MARK: - Calendar

    public func fetchCalendar(
        diaspora: Bool = true,
        date: Date? = nil
    ) async throws -> SefariaCalendarResponse {
        guard var components = URLComponents(
            url: baseURL.appendingPathComponent("api/calendars"),
            resolvingAgainstBaseURL: false
        ) else {
            throw SefariaAPIError.invalidURL
        }

        var queryItems: [URLQueryItem] = [
            URLQueryItem(name: "diaspora", value: diaspora ? "1" : "0")
        ]
        if let date {
            let gregorian = Calendar(identifier: .gregorian)
            queryItems.append(URLQueryItem(name: "year",
                                           value: String(gregorian.component(.year, from: date))))
            queryItems.append(URLQueryItem(name: "month",
                                           value: String(gregorian.component(.month, from: date))))
            queryItems.append(URLQueryItem(name: "day",
                                           value: String(gregorian.component(.day, from: date))))
        }
        components.queryItems = queryItems

        guard let url = components.url else { throw SefariaAPIError.invalidURL }
        let data = try await fetchData(from: url)
        do {
            return try decoder.decode(SefariaCalendarResponse.self, from: data)
        } catch {
            throw SefariaAPIError.decodingFailed(String(describing: error))
        }
    }

    // MARK: - Text

    public func fetchText(ref: String) async throws -> SefariaTextResponse {
        let normalized = ref.replacingOccurrences(of: " ", with: "_")
        guard
            let encoded = normalized.addingPercentEncoding(withAllowedCharacters: .urlPathAllowed),
            var components = URLComponents(
                url: baseURL.appendingPathComponent("api/v3/texts/\(encoded)"),
                resolvingAgainstBaseURL: false
            )
        else {
            throw SefariaAPIError.invalidURL
        }

        components.queryItems = [
            URLQueryItem(name: "version", value: "source"),
            URLQueryItem(name: "version", value: "english"),
            URLQueryItem(name: "return_format", value: "text_only"),
        ]

        guard let url = components.url else { throw SefariaAPIError.invalidURL }
        let data = try await fetchData(from: url)
        do {
            return try decoder.decode(SefariaTextResponse.self, from: data)
        } catch {
            throw SefariaAPIError.decodingFailed(String(describing: error))
        }
    }

    // MARK: - Parasha

    public func fetchWeeklyParasha(
        diaspora: Bool = true,
        date: Date? = nil
    ) async throws -> Parasha {
        let calendar = try await fetchCalendar(diaspora: diaspora, date: date)
        guard let parashaItem = calendar.parashaItem,
              let ref = parashaItem.ref,
              let heRef = parashaItem.heRef else {
            throw SefariaAPIError.parashaNotFound
        }

        let text = try await fetchText(ref: ref)
        let verses = SefariaAPIClient.makeVerses(from: text)
        guard !verses.isEmpty else {
            throw SefariaAPIError.emptyText
        }

        return Parasha(
            nameHebrew: parashaItem.displayValue.he ?? "",
            nameEnglish: parashaItem.displayValue.en ?? "",
            ref: ref,
            heRef: heRef,
            verses: verses,
            haftarahHeRef: calendar.haftarahItem?.heRef,
            haftarahRef: calendar.haftarahItem?.ref
        )
    }

    // MARK: - Helpers

    private func fetchData(from url: URL) async throws -> Data {
        var request = URLRequest(url: url)
        request.addValue("application/json", forHTTPHeaderField: "Accept")
        let (data, response) = try await session.data(for: request)
        try Self.validate(response: response)
        return data
    }

    static func validate(response: URLResponse) throws {
        guard let http = response as? HTTPURLResponse else {
            throw SefariaAPIError.invalidResponse
        }
        guard (200..<300).contains(http.statusCode) else {
            throw SefariaAPIError.httpError(http.statusCode)
        }
    }

    /// Converts a Sefaria text response into a flat list of verses with the
    /// correct chapter / verse numbering. Handles both flat (single chapter)
    /// and nested (multi-chapter) responses.
    static func makeVerses(from text: SefariaTextResponse) -> [ParashaVerse] {
        let hebrewVersion = text.versions.first(where: { $0.language == "he" })
            ?? text.versions.first
        guard let version = hebrewVersion, let content = version.text else {
            return []
        }

        let englishVersion = text.versions.first(where: { $0.language == "en" })
        let englishFlat = englishVersion?.text?.flatten() ?? []

        let startChapter = text.sections.flatMap { $0.first.flatMap(Int.init) } ?? 1
        let startVerse: Int = {
            guard let sections = text.sections, sections.count >= 2 else { return 1 }
            return Int(sections[1]) ?? 1
        }()

        var verses: [ParashaVerse] = []
        var englishIndex = 0

        func takeEnglish() -> String? {
            defer { englishIndex += 1 }
            return englishIndex < englishFlat.count ? englishFlat[englishIndex] : nil
        }

        switch content {
        case .string(let singleVerse):
            verses.append(
                ParashaVerse(
                    chapter: startChapter,
                    verse: startVerse,
                    hebrew: singleVerse,
                    english: takeEnglish()
                )
            )

        case .array(let outer):
            let isMultiChapter = outer.contains { element in
                if case .array = element { return true }
                return false
            }

            if isMultiChapter {
                for (chapterOffset, chapterContent) in outer.enumerated() {
                    guard case .array(let innerVerses) = chapterContent else { continue }
                    let chapterNumber = startChapter + chapterOffset
                    let baseVerse = (chapterOffset == 0) ? startVerse : 1
                    for (verseOffset, verseContent) in innerVerses.enumerated() {
                        guard case .string(let hebrew) = verseContent, !hebrew.isEmpty else {
                            continue
                        }
                        verses.append(
                            ParashaVerse(
                                chapter: chapterNumber,
                                verse: baseVerse + verseOffset,
                                hebrew: hebrew,
                                english: takeEnglish()
                            )
                        )
                    }
                }
            } else {
                for (verseOffset, verseContent) in outer.enumerated() {
                    guard case .string(let hebrew) = verseContent, !hebrew.isEmpty else {
                        continue
                    }
                    verses.append(
                        ParashaVerse(
                            chapter: startChapter,
                            verse: startVerse + verseOffset,
                            hebrew: hebrew,
                            english: takeEnglish()
                        )
                    )
                }
            }
        }

        return verses
    }
}
