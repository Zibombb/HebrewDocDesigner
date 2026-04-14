import Foundation

/// Converts integer chapter/verse numbers into their traditional Hebrew
/// letter (gematria) representation.
///
/// Examples:
/// - `1` → `"א׳"`
/// - `15` → `"ט״ו"` (not `"י״ה"`, to avoid spelling God's name)
/// - `16` → `"ט״ז"`
/// - `115` → `"קט״ו"`
/// - `200` → `"ר׳"`
public enum HebrewNumerals {
    /// Returns a Hebrew letter representation for a positive integer in the
    /// range 1...999. For numbers outside this range the decimal form is
    /// returned instead.
    public static func letters(for number: Int) -> String {
        guard number > 0 && number < 1000 else {
            return String(number)
        }

        var remaining = number
        var result = ""

        let values: [(Int, String)] = [
            (400, "ת"), (300, "ש"), (200, "ר"), (100, "ק"),
            (90, "צ"), (80, "פ"), (70, "ע"), (60, "ס"), (50, "נ"),
            (40, "מ"), (30, "ל"), (20, "כ"), (10, "י"),
            (9, "ט"), (8, "ח"), (7, "ז"), (6, "ו"), (5, "ה"),
            (4, "ד"), (3, "ג"), (2, "ב"), (1, "א"),
        ]

        for (value, symbol) in values {
            while remaining >= value {
                result += symbol
                remaining -= value
            }
        }

        // Avoid spelling the name of God in 15 and 16.
        if result.hasSuffix("יה") {
            result = String(result.dropLast(2)) + "טו"
        } else if result.hasSuffix("יו") {
            result = String(result.dropLast(2)) + "טז"
        }

        return addGershayim(to: result)
    }

    /// Adds a geresh (׳) to a single-letter numeral, or inserts gershayim (״)
    /// before the last letter of a multi-letter numeral, following standard
    /// Hebrew typographic convention.
    private static func addGershayim(to raw: String) -> String {
        guard !raw.isEmpty else { return raw }
        if raw.count == 1 {
            return raw + "׳"
        }
        var chars = Array(raw)
        chars.insert("״", at: chars.count - 1)
        return String(chars)
    }
}
