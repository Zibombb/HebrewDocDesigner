import XCTest
@testable import HebrewDocDesigner

final class HebrewNumeralsTests: XCTestCase {
    func test_singleLetterGetsGeresh() {
        XCTAssertEqual(HebrewNumerals.letters(for: 1), "א׳")
        XCTAssertEqual(HebrewNumerals.letters(for: 5), "ה׳")
        XCTAssertEqual(HebrewNumerals.letters(for: 10), "י׳")
        XCTAssertEqual(HebrewNumerals.letters(for: 100), "ק׳")
        XCTAssertEqual(HebrewNumerals.letters(for: 400), "ת׳")
    }

    func test_multiLetterGetsGershayim() {
        XCTAssertEqual(HebrewNumerals.letters(for: 11), "י״א")
        XCTAssertEqual(HebrewNumerals.letters(for: 12), "י״ב")
        XCTAssertEqual(HebrewNumerals.letters(for: 21), "כ״א")
        XCTAssertEqual(HebrewNumerals.letters(for: 99), "צ״ט")
    }

    func test_avoidsGodsName_15_16() {
        XCTAssertEqual(HebrewNumerals.letters(for: 15), "ט״ו")
        XCTAssertEqual(HebrewNumerals.letters(for: 16), "ט״ז")
    }

    func test_avoidsGodsName_inLargerNumbers() {
        XCTAssertEqual(HebrewNumerals.letters(for: 115), "קט״ו")
        XCTAssertEqual(HebrewNumerals.letters(for: 116), "קט״ז")
        XCTAssertEqual(HebrewNumerals.letters(for: 215), "רט״ו")
    }

    func test_hundreds() {
        XCTAssertEqual(HebrewNumerals.letters(for: 200), "ר׳")
        XCTAssertEqual(HebrewNumerals.letters(for: 300), "ש׳")
        XCTAssertEqual(HebrewNumerals.letters(for: 500), "ת״ק")
        XCTAssertEqual(HebrewNumerals.letters(for: 900), "תת״ק")
    }

    func test_outOfRange_fallsBackToDecimal() {
        XCTAssertEqual(HebrewNumerals.letters(for: 0), "0")
        XCTAssertEqual(HebrewNumerals.letters(for: -1), "-1")
        XCTAssertEqual(HebrewNumerals.letters(for: 1000), "1000")
    }
}
