import Foundation

/// Errors produced by ``SefariaAPIClient``.
public enum SefariaAPIError: Error, LocalizedError, Sendable, Equatable {
    case invalidURL
    case invalidResponse
    case httpError(Int)
    case parashaNotFound
    case decodingFailed(String)
    case emptyText

    public var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "כתובת API לא חוקית"
        case .invalidResponse:
            return "תגובה לא תקינה מהשרת"
        case .httpError(let code):
            return "שגיאת HTTP \(code)"
        case .parashaNotFound:
            return "לא נמצאה פרשת השבוע ביומן הלימוד"
        case .decodingFailed(let message):
            return "שגיאת פענוח נתונים: \(message)"
        case .emptyText:
            return "לא התקבל טקסט לפרשה זו"
        }
    }
}
