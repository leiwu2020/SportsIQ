import SwiftUI

@main
struct SportsIQApp: App {
    @Environment(\.scenePhase) private var scenePhase
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .onReceive(NotificationCenter.default.publisher(for: UIApplication.willResignActiveNotification)) { _ in
                    // App going to background - cleanup temporary files
                    cleanupTemporaryFiles()
                }
                .onReceive(NotificationCenter.default.publisher(for: UIApplication.willTerminateNotification)) { _ in
                    // App terminating - cleanup temporary files
                    cleanupTemporaryFiles()
                }
        }
        .onChange(of: scenePhase) { newPhase in
            switch newPhase {
            case .background:
                // App entering background - cleanup temporary files
                cleanupTemporaryFiles()
            case .inactive:
                // App becoming inactive - cleanup temporary files
                cleanupTemporaryFiles()
            default:
                break
            }
        }
    }
    
    private func cleanupTemporaryFiles() {
        print("SportsIQ: Cleaning up temporary files...")
        
        let tempDir = FileManager.default.temporaryDirectory
        do {
            let tempFiles = try FileManager.default.contentsOfDirectory(at: tempDir, includingPropertiesForKeys: nil)
            
            for fileURL in tempFiles {
                if fileURL.lastPathComponent.hasPrefix("temp_image_") || 
                   fileURL.lastPathComponent.hasPrefix("temp_video_") {
                    try FileManager.default.removeItem(at: fileURL)
                    print("SportsIQ: Removed temporary file: \(fileURL.lastPathComponent)")
                }
            }
        } catch {
            print("SportsIQ: Error cleaning up temporary files: \(error)")
        }
    }
}

