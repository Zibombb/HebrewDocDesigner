import XCTest
@testable import HebrewDocDesigner

final class HebrewTextTests: XCTestCase {
    func test_stripsNikud() {
        let withNikud = "בְּרֵאשִׁית"
        let expected = "בראשית"
        XCTAssertEqual(HebrewText.stripNikud(withNikud), expected)
    }

    func test_stripsTaamei() {
        // בְּרֵאשִׁ֖ית - "b'reishis" with ta'am tipcha
        let withTeamim = "בְּרֵאשִׁ֖ית"
        XCTAssertEqual(HebrewText.stripNikud(withTeamim), "בראשית")
    }

    func test_leavesBaseLettersUnchanged() {
        XCTAssertEqual(HebrewText.stripNikud("שלום"), "שלום")
    }

    func test_containsHebrewLetters_positive() {
        XCTAssertTrue(HebrewText.containsHebrewLetters("שלום"))
        XCTAssertTrue(HebrewText.containsHebrewLetters("Hello שלום"))
    }

    func test_containsHebrewLetters_negative() {
        XCTAssertFalse(HebrewText.containsHebrewLetters("Hello world"))
        XCTAssertFalse(HebrewText.containsHebrewLetters(""))
    }
}
