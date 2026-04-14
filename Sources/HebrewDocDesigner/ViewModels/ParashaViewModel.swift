#if canImport(Combine)
import Combine
#endif
import Foundation

#if canImport(SwiftUI)
import SwiftUI

/// View-model backing the main Torah book screen. Handles loading the
/// weekly parasha from Sefaria and exposing it to SwiftUI.
@MainActor
public final class ParashaViewModel: ObservableObject {
    public enum LoadState: Sendable, Equatable {
        case idle
        case loading
        case loaded(Parasha)
        case failed(String)
    }

    @Published public private(set) var state: LoadState = .idle
    @Published public var fontSize: CGFloat = 22
    @Published public var showNikud: Bool = true
    @Published public var showEnglish: Bool = false
    @Published public var diaspora: Bool = true

    private let apiClient: SefariaAPIClientProtocol

    public init(apiClient: SefariaAPIClientProtocol = SefariaAPIClient()) {
        self.apiClient = apiClient
    }

    /// The loaded parasha if available, otherwise `nil`.
    public var parasha: Parasha? {
        if case .loaded(let parasha) = state { return parasha }
        return nil
    }

    public var isLoading: Bool {
        if case .loading = state { return true }
        return false
    }

    /// Load the weekly parasha. Safe to call multiple times; concurrent calls
    /// are serialized by the actor-based API client.
    public func load() async {
        state = .loading
        do {
            let parasha = try await apiClient.fetchWeeklyParasha(
                diaspora: diaspora,
                date: nil
            )
            state = .loaded(parasha)
        } catch {
            state = .failed(error.localizedDescription)
        }
    }

    /// Retry after a failure.
    public func retry() async {
        await load()
    }
}
#endif
