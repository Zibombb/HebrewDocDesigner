#if canImport(SwiftUI)
import SwiftUI

/// Displays a ``Parasha`` as a traditional Torah book page: right-to-left
/// layout, Hebrew serif font, chapter headings in gematria, and a control
/// bar for adjusting the display.
public struct TorahBookView: View {
    public let parasha: Parasha
    @Binding public var fontSize: CGFloat
    @Binding public var showNikud: Bool
    @Binding public var showEnglish: Bool

    public init(
        parasha: Parasha,
        fontSize: Binding<CGFloat>,
        showNikud: Binding<Bool>,
        showEnglish: Binding<Bool>
    ) {
        self.parasha = parasha
        self._fontSize = fontSize
        self._showNikud = showNikud
        self._showEnglish = showEnglish
    }

    public var body: some View {
        VStack(alignment: .trailing, spacing: 24) {
            header
            controls
            Divider()
            chapters
            if let haftarah = parasha.haftarahHeRef {
                HaftarahFooter(haftarah: haftarah)
            }
        }
        .frame(maxWidth: .infinity, alignment: .trailing)
        .environment(\.layoutDirection, .rightToLeft)
    }

    // MARK: - Header

    private var header: some View {
        VStack(alignment: .trailing, spacing: 8) {
            Text("פרשת \(parasha.nameHebrew)")
                .font(.system(size: 44, weight: .bold, design: .serif))
                .multilineTextAlignment(.trailing)
            Text(parasha.heRef)
                .font(.title3)
                .foregroundStyle(.secondary)
            Text(parasha.nameEnglish)
                .font(.caption)
                .foregroundStyle(.tertiary)
                .environment(\.layoutDirection, .leftToRight)
        }
    }

    // MARK: - Controls

    private var controls: some View {
        VStack(alignment: .trailing, spacing: 12) {
            HStack {
                Text("גודל טקסט")
                    .font(.subheadline)
                Slider(value: $fontSize, in: 14...48, step: 1)
                Text("\(Int(fontSize))")
                    .font(.caption.monospacedDigit())
                    .foregroundStyle(.secondary)
                    .frame(width: 28)
            }
            HStack(spacing: 16) {
                Toggle("ניקוד וטעמים", isOn: $showNikud)
                    .toggleStyle(.switch)
                Toggle("תרגום אנגלי", isOn: $showEnglish)
                    .toggleStyle(.switch)
            }
            .font(.subheadline)
        }
    }

    // MARK: - Chapters

    private var chapters: some View {
        VStack(alignment: .trailing, spacing: 20) {
            ForEach(parasha.chapters, id: \.chapter) { entry in
                ChapterView(
                    chapterNumber: entry.chapter,
                    verses: entry.verses,
                    fontSize: fontSize,
                    showNikud: showNikud,
                    showEnglish: showEnglish
                )
            }
        }
    }
}

/// A single chapter of a parasha.
struct ChapterView: View {
    let chapterNumber: Int
    let verses: [ParashaVerse]
    let fontSize: CGFloat
    let showNikud: Bool
    let showEnglish: Bool

    var body: some View {
        VStack(alignment: .trailing, spacing: 12) {
            Text("פרק \(HebrewNumerals.letters(for: chapterNumber))")
                .font(.system(size: 26, weight: .bold, design: .serif))
                .foregroundStyle(.primary)
                .padding(.top, 8)

            ForEach(verses) { verse in
                VerseView(
                    verse: verse,
                    fontSize: fontSize,
                    showNikud: showNikud,
                    showEnglish: showEnglish
                )
            }
        }
    }
}

/// A single verse with its Hebrew letter number and optional English
/// translation.
struct VerseView: View {
    let verse: ParashaVerse
    let fontSize: CGFloat
    let showNikud: Bool
    let showEnglish: Bool

    var body: some View {
        VStack(alignment: .trailing, spacing: 4) {
            HStack(alignment: .firstTextBaseline, spacing: 6) {
                Text(HebrewNumerals.letters(for: verse.verse))
                    .font(.system(size: fontSize * 0.75, weight: .semibold, design: .serif))
                    .foregroundStyle(.secondary)
                Text(displayedHebrew)
                    .font(.system(size: fontSize, weight: .regular, design: .serif))
                    .multilineTextAlignment(.trailing)
                    .fixedSize(horizontal: false, vertical: true)
            }
            if showEnglish, let english = verse.english {
                Text(english)
                    .font(.system(size: fontSize * 0.75))
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.leading)
                    .environment(\.layoutDirection, .leftToRight)
            }
        }
    }

    private var displayedHebrew: String {
        showNikud ? verse.hebrew : HebrewText.stripNikud(verse.hebrew)
    }
}

/// Footer showing the haftarah reference, if one was returned with the
/// parasha.
struct HaftarahFooter: View {
    let haftarah: String

    var body: some View {
        VStack(alignment: .trailing, spacing: 6) {
            Divider()
            Text("הפטרה")
                .font(.title3.bold())
            Text(haftarah)
                .font(.body)
                .foregroundStyle(.secondary)
        }
        .padding(.top, 16)
    }
}
#endif
