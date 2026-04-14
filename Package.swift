// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "HebrewDocDesigner",
    defaultLocalization: "he",
    platforms: [
        .iOS(.v16),
        .macOS(.v13),
        .tvOS(.v16),
        .watchOS(.v9),
    ],
    products: [
        .library(
            name: "HebrewDocDesigner",
            targets: ["HebrewDocDesigner"]
        ),
    ],
    targets: [
        .target(
            name: "HebrewDocDesigner",
            path: "Sources/HebrewDocDesigner"
        ),
        .testTarget(
            name: "HebrewDocDesignerTests",
            dependencies: ["HebrewDocDesigner"],
            path: "Tests/HebrewDocDesignerTests"
        ),
    ]
)
