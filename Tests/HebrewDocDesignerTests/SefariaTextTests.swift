import XCTest
@testable import HebrewDocDesigner

final class SefariaTextTests: XCTestCase {
    func test_decodesFlatTextResponse() throws {
        let json = """
        {
          "ref": "Genesis 1:1-3",
          "heRef": "בראשית א׳:א׳-ג׳",
          "sections": ["1", "1"],
          "toSections": ["1", "3"],
          "versions": [
            {
              "language": "he",
              "versionTitle": "Tanach with Ta'amei Hamikra",
              "text": ["בְּרֵאשִׁית", "וְהָאָרֶץ", "וַיֹּאמֶר"]
            }
          ]
        }
        """.data(using: .utf8)!

        let response = try JSONDecoder().decode(SefariaTextResponse.self, from: json)
        XCTAssertEqual(response.ref, "Genesis 1:1-3")
        XCTAssertEqual(response.versions.count, 1)
        XCTAssertEqual(response.versions.first?.text?.flatten().count, 3)
    }

    func test_decodesNestedMultiChapterResponse() throws {
        let json = """
        {
          "ref": "Genesis 1:31-2:2",
          "heRef": "בראשית א׳:ל״א-ב׳:ב׳",
          "sections": ["1", "31"],
          "toSections": ["2", "2"],
          "versions": [
            {
              "language": "he",
              "text": [
                ["וַיַּרְא"],
                ["וַיְכֻלּוּ", "וַיְכַל"]
              ]
            }
          ]
        }
        """.data(using: .utf8)!

        let response = try JSONDecoder().decode(SefariaTextResponse.self, from: json)
        let verses = SefariaAPIClient.makeVerses(from: response)
        XCTAssertEqual(verses.count, 3)
        XCTAssertEqual(verses[0].chapter, 1)
        XCTAssertEqual(verses[0].verse, 31)
        XCTAssertEqual(verses[1].chapter, 2)
        XCTAssertEqual(verses[1].verse, 1)
        XCTAssertEqual(verses[2].chapter, 2)
        XCTAssertEqual(verses[2].verse, 2)
    }

    func test_makeVerses_singleChapter_startingAtOne() throws {
        let response = SefariaTextResponse(
            ref: "Genesis 1:1-3",
            heRef: "בראשית א׳:א׳-ג׳",
            sections: ["1", "1"],
            toSections: ["1", "3"],
            versions: [
                SefariaVersion(
                    language: "he",
                    text: .array([.string("א"), .string("ב"), .string("ג")])
                )
            ]
        )

        let verses = SefariaAPIClient.makeVerses(from: response)
        XCTAssertEqual(verses.count, 3)
        XCTAssertEqual(verses.map(\.verse), [1, 2, 3])
        XCTAssertEqual(verses.map(\.chapter), [1, 1, 1])
        XCTAssertEqual(verses.map(\.hebrew), ["א", "ב", "ג"])
    }

    func test_makeVerses_singleChapter_withStartVerseOffset() throws {
        let response = SefariaTextResponse(
            ref: "Genesis 5:3-5",
            heRef: "בראשית ה׳:ג׳-ה׳",
            sections: ["5", "3"],
            toSections: ["5", "5"],
            versions: [
                SefariaVersion(
                    language: "he",
                    text: .array([.string("ג"), .string("ד"), .string("ה")])
                )
            ]
        )

        let verses = SefariaAPIClient.makeVerses(from: response)
        XCTAssertEqual(verses.map(\.chapter), [5, 5, 5])
        XCTAssertEqual(verses.map(\.verse), [3, 4, 5])
    }

    func test_makeVerses_attachesEnglishTranslation() throws {
        let response = SefariaTextResponse(
            ref: "Genesis 1:1-2",
            heRef: "בראשית א׳:א׳-ב׳",
            sections: ["1", "1"],
            toSections: ["1", "2"],
            versions: [
                SefariaVersion(
                    language: "he",
                    text: .array([.string("בראשית"), .string("והארץ")])
                ),
                SefariaVersion(
                    language: "en",
                    text: .array([.string("In the beginning"), .string("And the earth")])
                ),
            ]
        )

        let verses = SefariaAPIClient.makeVerses(from: response)
        XCTAssertEqual(verses.count, 2)
        XCTAssertEqual(verses[0].english, "In the beginning")
        XCTAssertEqual(verses[1].english, "And the earth")
    }

    func test_makeVerses_handlesMissingEnglish() throws {
        let response = SefariaTextResponse(
            ref: "Genesis 1:1",
            heRef: "בראשית א׳:א׳",
            sections: ["1", "1"],
            toSections: ["1", "1"],
            versions: [
                SefariaVersion(
                    language: "he",
                    text: .array([.string("בראשית")])
                )
            ]
        )

        let verses = SefariaAPIClient.makeVerses(from: response)
        XCTAssertEqual(verses.count, 1)
        XCTAssertNil(verses[0].english)
    }
}
