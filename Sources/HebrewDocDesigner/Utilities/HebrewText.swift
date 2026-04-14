import Foundation

/// Utility helpers for Hebrew text normalization.
public enum HebrewText {
    /// Unicode range for Hebrew points (nikud) and cantillation marks
    /// (te'amim): `U+0591`…`U+05C7`.
    private static let markRange: ClosedRange<UInt32> = 0x0591...0x05C7

    /// Returns the given string with all Hebrew vowel points (nikud) and
    /// cantillation marks (te'amim) removed, leaving only the base letters.
    public static func stripNikud(_ text: String) -> String {
        String(text.unicodeScalars.filter { !markRange.contains($0.value) })
    }

    /// Returns `true` when the given string contains any Hebrew base letters
    /// (`U+05D0`…`U+05EA`).
    public static func containsHebrewLetters(_ text: String) -> Bool {
        text.unicodeScalars.contains { (0x05D0...0x05EA).contains($0.value) }
    }
}
