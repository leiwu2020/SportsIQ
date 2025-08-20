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
                    
                    // Demo Analysis Button
                    Button(action: {
                        loadDemoAnalysis()
                    }) {
                        HStack {
                            Image(systemName: "play.circle")
                            Text("View Demo Analysis")
                        }
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.purple)
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
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { showingSettings = true }) {
                        Image(systemName: "gear")
                    }
                }
            }
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
                    analysisResult = analysis
                    showingAnalysis = true
                case .failure(let error):
                    print("Analysis failed with error: \(error)")
                    print("Error details: \(error.localizedDescription)")
                    // Show error alert in real implementation
                    showingErrorAlert = true
                    errorMessage = error.localizedDescription
                }
            }
        }
    }
    
    private func loadDemoAnalysis() {
        print("Loading demo analysis...")
        isAnalyzing = true
        
        NetworkManager.shared.getDemoAnalysis { result in
            DispatchQueue.main.async {
                isAnalyzing = false
                switch result {
                case .success(let analysis):
                    print("Demo analysis successful!")
                    analysisResult = analysis
                    showingAnalysis = true
                case .failure(let error):
                    print("Demo analysis failed: \(error)")
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
