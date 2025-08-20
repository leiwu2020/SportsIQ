import SwiftUI

struct ContentView: View {
    @State private var showingCamera = false
    @State private var showingPhotoPicker = false

    @State private var selectedVideo: URL?
    @State private var analysisResult: AnalysisResult?
    @State private var isAnalyzing = false
    @State private var showingAnalysis = false
    @State private var showingFormGuide = false
    @State private var showingErrorAlert = false
    @State private var errorMessage = ""
    @State private var showingSettings = false

    
    // Check if running in simulator
    private var isRunningInSimulator: Bool {
        #if targetEnvironment(simulator)
        return true
        #else
        return false
        #endif
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: 30) {
                // Header
                VStack(spacing: 10) {
                    Image(systemName: "basketball.fill")
                        .font(.system(size: 60))
                        .foregroundColor(.orange)
                    
                    Text("Analyze Your Basketball Shot")
                        .font(.headline)
                        .foregroundColor(.secondary)
                }
                .padding(.top, 20)
                
                // Simulator Notice
                if isRunningInSimulator {
                    VStack(spacing: 8) {
                        HStack {
                            Image(systemName: "info.circle")
                                .foregroundColor(.orange)
                            Text("Running in Simulator")
                                .font(.subheadline)
                                .fontWeight(.medium)
                        }
                        Text("Camera recording will open photo library instead")
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding()
                    .background(Color.orange.opacity(0.1))
                    .cornerRadius(8)
                    .padding(.horizontal, 30)
                }
                
                Spacer()
                
                // Action Buttons
                VStack(spacing: 20) {
                    // Record Video Button
                    Button(action: {
                        showingCamera = true
                    }) {
                        HStack {
                            Image(systemName: "video.fill")
                            Text(UIImagePickerController.isSourceTypeAvailable(.camera) ? "Record Shot" : "Select Video (Simulator)")
                        }
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(12)
                    }
                    
                    // Select from Library Button
                    Button(action: {
                        showingPhotoPicker = true
                    }) {
                        HStack {
                            Image(systemName: "photo.on.rectangle")
                            Text("Select from Library")
                        }
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.green)
                        .cornerRadius(12)
                    }
                    
                    // Perfect Form Guide Button
                    Button(action: {
                        showingFormGuide = true
                    }) {
                        HStack {
                            Image(systemName: "target")
                            Text("Perfect Form Guide")
                        }
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.orange)
                        .cornerRadius(12)
                    }
                }
                .padding(.horizontal, 30)
                
                Spacer()
                
                // Analysis Status
                if isAnalyzing {
                    VStack {
                        ProgressView()
                            .scaleEffect(1.2)
                        Text("Analyzing your shot...")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .padding(.top, 8)
                    }
                }
                
                Spacer()
            }
            .navigationTitle("SportsIQ")
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(trailing: Button(action: { showingSettings = true }) {
                Image(systemName: "gear")
            })
        }
        .sheet(isPresented: $showingCamera) {
            CameraView { videoURL in
                selectedVideo = videoURL
                analyzeVideo(videoURL)
            }
        }
        .sheet(isPresented: $showingPhotoPicker) {
            PhotoPicker { videoURL in
                selectedVideo = videoURL
                analyzeVideo(videoURL)
            }
        }

        .sheet(isPresented: $showingAnalysis) {
            if let result = analysisResult {
                AnalysisView(analysisResult: result)
            }
        }
        .sheet(isPresented: $showingFormGuide) {
            ShootingFormGuideView()
        }
        .sheet(isPresented: $showingSettings) {
            SettingsView()
        }
        .alert("Analysis Error", isPresented: $showingErrorAlert) {
            Button("OK") { }
        } message: {
            Text(errorMessage)
        }
        .onReceive(NotificationCenter.default.publisher(for: NSNotification.Name("RedoAnalysis"))) { _ in
            // Handle re-analysis request
            if let analysis = analysisResult, let fileId = analysis.fileInfo?.fileId {
                print("ContentView: Redo analysis requested for file ID: \(fileId)")
                reanalyzeVideo(fileId: fileId)
            } else if let videoURL = selectedVideo {
                print("ContentView: No file ID available, re-uploading video: \(videoURL)")
                analyzeVideo(videoURL)
            }
        }

    }
    
    private func analyzeVideo(_ videoURL: URL) {
        print("Starting video analysis for: \(videoURL)")
        isAnalyzing = true
        
        NetworkManager.shared.analyzeVideo(videoURL) { result in
            DispatchQueue.main.async {
                isAnalyzing = false
                switch result {
                case .success(let analysis):
                    print("Analysis successful! Got result with keys: \(Mirror(reflecting: analysis).children.map { $0.label ?? "unknown" })")
                    print("Analysis type: \(analysis.analysisType ?? "nil")")
                    print("Is streamlined: \(analysis.isStreamlinedAnalysis)")
                    print("Is fallback: \(analysis.isFallbackAnalysis)")
                    print("Shooting sequence: \(analysis.shootingSequence == nil ? "nil" : "present")")
                    analysisResult = analysis
                    showingAnalysis = true
                    
                    // Cleanup temporary video file after successful analysis
                    cleanupTemporaryVideoFile(videoURL)
                case .failure(let error):
                    print("Analysis failed with error: \(error)")
                    print("Error details: \(error.localizedDescription)")
                    // Show error alert in real implementation
                    showingErrorAlert = true
                    errorMessage = error.localizedDescription
                    
                    // Cleanup temporary video file even if analysis failed
                    cleanupTemporaryVideoFile(videoURL)
                }
            }
        }
    }
    
    private func cleanupTemporaryVideoFile(_ videoURL: URL) {
        // Only cleanup if it's a temporary file we created
        if videoURL.lastPathComponent.hasPrefix("temp_") {
            do {
                try FileManager.default.removeItem(at: videoURL)
                print("ContentView: Cleaned up temporary video file: \(videoURL.lastPathComponent)")
            } catch {
                print("ContentView: Error cleaning up temporary video file: \(error)")
            }
        }
    }
    
    private func reanalyzeVideo(fileId: String) {
        print("ContentView: Starting re-analysis for file ID: \(fileId)")
        isAnalyzing = true
        
        NetworkManager.shared.reanalyzeVideo(fileId: fileId) { result in
            DispatchQueue.main.async {
                isAnalyzing = false
                switch result {
                case .success(let analysis):
                    print("Re-analysis successful! Got result with keys: \(Mirror(reflecting: analysis).children.map { $0.label ?? "unknown" })")
                    analysisResult = analysis
                    showingAnalysis = true
                case .failure(let error):
                    print("Re-analysis failed with error: \(error)")
                    print("Error details: \(error.localizedDescription)")
                    showingErrorAlert = true
                    errorMessage = error.localizedDescription
                }
            }
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
