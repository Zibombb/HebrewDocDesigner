#if canImport(SwiftUI)
import SwiftUI

/// The root view of the Torah book designer. It loads the weekly parasha
/// from Sefaria and hands it off to ``TorahBookView`` for display.
public struct ContentView: View {
    @StateObject private var viewModel: ParashaViewModel

    public init(viewModel: ParashaViewModel = ParashaViewModel()) {
        _viewModel = StateObject(wrappedValue: viewModel)
    }

    public var body: some View {
        NavigationStack {
            ParashaContainerView(viewModel: viewModel)
                .navigationTitle("מעצב ספר תורני")
                #if os(iOS)
                .navigationBarTitleDisplayMode(.inline)
                #endif
        }
        .environment(\.layoutDirection, .rightToLeft)
        .task {
            if viewModel.parasha == nil {
                await viewModel.load()
            }
        }
    }
}

/// A wrapper that switches on the load state of the view model.
struct ParashaContainerView: View {
    @ObservedObject var viewModel: ParashaViewModel

    var body: some View {
        Group {
            switch viewModel.state {
            case .idle, .loading:
                LoadingView()
            case .loaded(let parasha):
                ScrollView {
                    TorahBookView(
                        parasha: parasha,
                        fontSize: $viewModel.fontSize,
                        showNikud: $viewModel.showNikud,
                        showEnglish: $viewModel.showEnglish
                    )
                    .padding()
                }
            case .failed(let message):
                ErrorView(message: message) {
                    Task { await viewModel.retry() }
                }
            }
        }
    }
}

struct LoadingView: View {
    var body: some View {
        VStack(spacing: 16) {
            ProgressView()
            Text("טוען את פרשת השבוע…")
                .font(.headline)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

struct ErrorView: View {
    let message: String
    let retry: () -> Void

    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: 44))
                .foregroundStyle(.orange)
            Text("שגיאה בטעינה")
                .font(.title2.bold())
            Text(message)
                .multilineTextAlignment(.center)
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .padding(.horizontal)
            Button(action: retry) {
                Label("נסה שוב", systemImage: "arrow.clockwise")
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}
#endif
