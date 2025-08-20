import SwiftUI

struct AnalysisResult: Codable {
    let shotPhases: ShotPhases?
    let formAnalysis: FormAnalysis
    let recommendations: [String]
    let fileInfo: FileInfo?
    let releaseFrame: ReleaseFrame?
    let shooterInfo: ShooterInfo?
    let ballDetectionInfo: BallDetectionInfo?
    
    enum CodingKeys: String, CodingKey {
        case shotPhases = "shot_phases"
        case formAnalysis = "form_analysis"
        case recommendations
        case fileInfo = "file_info"
        case releaseFrame = "release_frame"
        case shooterInfo = "shooter_info"
        case ballDetectionInfo = "ball_detection_info"
    }
}

struct ShotPhases: Codable {
    let totalFrames: Int
    let preparationPhase: [Int]?
    let releasePoint: Int?
    let followThroughPhase: [Int]?
    
    enum CodingKeys: String, CodingKey {
        case totalFrames = "total_frames"
        case preparationPhase = "preparation_phase"
        case releasePoint = "release_point"
        case followThroughPhase = "follow_through_phase"
    }
}

struct FormAnalysis: Codable {
    let elbowAlignment: String
    let elbowIssues: [String]
    let handPosition: String
    let handIssues: [String]
    let bodyAlignment: String
    let alignmentIssues: [String]
    let followThrough: String
    let followThroughIssues: [String]
    
    enum CodingKeys: String, CodingKey {
        case elbowAlignment = "elbow_alignment"
        case elbowIssues = "elbow_issues"
        case handPosition = "hand_position"
        case handIssues = "hand_issues"
        case bodyAlignment = "body_alignment"
        case alignmentIssues = "alignment_issues"
        case followThrough = "follow_through"
        case followThroughIssues = "follow_through_issues"
    }
}

struct FileInfo: Codable {
    let filename: String
    let fileType: String
    
    enum CodingKeys: String, CodingKey {
        case filename
        case fileType = "file_type"
    }
}

struct ReleaseFrame: Codable {
    let originalFrame: OriginalFrame?
    let ballHolderCrop: PlayerCrop?
    let allPlayerCrops: [PlayerCrop]?
    let frameNumber: Int
    let ballHolderId: Int?
    let totalPlayersDetected: Int?
    let ballDetected: Bool?
    
    // Legacy support for old format
    let imageData: String?
    let shooterId: Int?
    let cropCoordinates: CropCoordinates?
    let originalSize: ImageSize?
    let croppedSize: ImageSize?
    
    enum CodingKeys: String, CodingKey {
        case originalFrame = "original_frame"
        case ballHolderCrop = "ball_holder_crop"
        case allPlayerCrops = "all_player_crops"
        case frameNumber = "frame_number"
        case ballHolderId = "ball_holder_id"
        case totalPlayersDetected = "total_players_detected"
        case ballDetected = "ball_detected"
        // Legacy
        case imageData = "image_data"
        case shooterId = "shooter_id"
        case cropCoordinates = "crop_coordinates"
        case originalSize = "original_size"
        case croppedSize = "cropped_size"
    }
}

struct OriginalFrame: Codable {
    let imageData: String
    let width: Int
    let height: Int
    
    enum CodingKeys: String, CodingKey {
        case imageData = "image_data"
        case width
        case height
    }
}

struct PlayerCrop: Codable {
    let imageData: String
    let personId: Int
    let isBallHolder: Bool
    let cropCoordinates: CropCoordinates
    let croppedSize: ImageSize
    
    enum CodingKeys: String, CodingKey {
        case imageData = "image_data"
        case personId = "person_id"
        case isBallHolder = "is_ball_holder"
        case cropCoordinates = "crop_coordinates"
        case croppedSize = "cropped_size"
    }
}

struct BallDetectionInfo: Codable {
    let ballDetectedFrames: Int
    let totalFrames: Int
    let ballHolderFrames: Int
    
    enum CodingKeys: String, CodingKey {
        case ballDetectedFrames = "ball_detected_frames"
        case totalFrames = "total_frames"
        case ballHolderFrames = "ball_holder_frames"
    }
}

struct ShooterInfo: Codable {
    let shooterId: Int
    let confidence: Double
    let totalPeopleDetected: Int
    
    enum CodingKeys: String, CodingKey {
        case shooterId = "shooter_id"
        case confidence
        case totalPeopleDetected = "total_people_detected"
    }
}

struct CropCoordinates: Codable {
    let x: Int
    let y: Int
    let width: Int
    let height: Int
}

struct ImageSize: Codable {
    let width: Int
    let height: Int
}

struct AnalysisView: View {
    let analysisResult: AnalysisResult
    @Environment(\.presentationMode) var presentationMode
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // Header
                    VStack(alignment: .center, spacing: 10) {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.system(size: 50))
                            .foregroundColor(.green)
                        
                        Text("Shot Analysis Complete")
                            .font(.title2)
                            .fontWeight(.bold)
                        
                        if let fileInfo = analysisResult.fileInfo {
                            Text(fileInfo.filename)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    
                    // Ball Detection Info (if available)
                    if let ballInfo = analysisResult.ballDetectionInfo {
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Ball Detection")
                                .font(.headline)
                                .fontWeight(.semibold)
                            
                            BallDetectionInfoView(ballInfo: ballInfo)
                        }
                    }
                    
                    // Shooter Detection Info (if multiple people detected)
                    if let shooterInfo = analysisResult.shooterInfo, shooterInfo.totalPeopleDetected > 1 {
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Player Detection")
                                .font(.headline)
                                .fontWeight(.semibold)
                            
                            ShooterInfoView(shooterInfo: shooterInfo)
                        }
                    }
                    
                    // Release Frame (if available)
                    if let releaseFrame = analysisResult.releaseFrame {
                        VStack(alignment: .leading, spacing: 15) {
                            Text("Ball Release Frame Analysis")
                                .font(.headline)
                                .fontWeight(.semibold)
                            
                            ComprehensiveReleaseFrameView(releaseFrame: releaseFrame, shooterInfo: analysisResult.shooterInfo)
                        }
                    }
                    
                    // Overall Form Score
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Form Analysis")
                            .font(.headline)
                            .fontWeight(.semibold)
                        
                        FormScoreCard(formAnalysis: analysisResult.formAnalysis)
                    }
                    
                    // Shot Phases (if available)
                    if let shotPhases = analysisResult.shotPhases {
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Shot Breakdown")
                                .font(.headline)
                                .fontWeight(.semibold)
                            
                            ShotPhasesView(shotPhases: shotPhases)
                        }
                    }
                    
                    // Recommendations
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Recommendations")
                            .font(.headline)
                            .fontWeight(.semibold)
                        
                        ForEach(analysisResult.recommendations, id: \.self) { recommendation in
                            RecommendationCard(text: recommendation)
                        }
                    }
                    
                    // Action Buttons
                    VStack(spacing: 15) {
                        Button("Analyze Another Shot") {
                            presentationMode.wrappedValue.dismiss()
                        }
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(12)
                        
                        Button("Share Results") {
                            // Implement sharing functionality
                        }
                        .font(.headline)
                        .foregroundColor(.blue)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(12)
                    }
                    .padding(.top, 20)
                }
                .padding()
            }
            .navigationTitle("Analysis Results")
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(trailing: Button("Done") {
                presentationMode.wrappedValue.dismiss()
            })
        }
    }
}

struct FormScoreCard: View {
    let formAnalysis: FormAnalysis
    
    var body: some View {
        VStack(spacing: 12) {
            FormMetric(
                title: "Elbow Alignment",
                status: formAnalysis.elbowAlignment,
                issues: formAnalysis.elbowIssues
            )
            
            FormMetric(
                title: "Hand Position",
                status: formAnalysis.handPosition,
                issues: formAnalysis.handIssues
            )
            
            FormMetric(
                title: "Body Alignment",
                status: formAnalysis.bodyAlignment,
                issues: formAnalysis.alignmentIssues
            )
            
            FormMetric(
                title: "Follow Through",
                status: formAnalysis.followThrough,
                issues: formAnalysis.followThroughIssues
            )
        }
        .padding()
        .background(Color.gray.opacity(0.1))
        .cornerRadius(12)
    }
}

struct FormMetric: View {
    let title: String
    let status: String
    let issues: [String]
    
    private var statusColor: Color {
        switch status.lowercased() {
        case "good":
            return .green
        case "needs_improvement", "needs improvement":
            return .orange
        default:
            return .red
        }
    }
    
    private var statusIcon: String {
        switch status.lowercased() {
        case "good":
            return "checkmark.circle.fill"
        case "needs_improvement", "needs improvement":
            return "exclamationmark.triangle.fill"
        default:
            return "xmark.circle.fill"
        }
    }
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                if !issues.isEmpty {
                    Text(issues.joined(separator: ", "))
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            Spacer()
            
            HStack(spacing: 4) {
                Image(systemName: statusIcon)
                    .foregroundColor(statusColor)
                
                Text(status.replacingOccurrences(of: "_", with: " ").capitalized)
                    .font(.caption)
                    .fontWeight(.medium)
                    .foregroundColor(statusColor)
            }
        }
    }
}

struct ShotPhasesView: View {
    let shotPhases: ShotPhases
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Total Frames: \(shotPhases.totalFrames)")
                .font(.subheadline)
            
            if let prep = shotPhases.preparationPhase {
                Text("Preparation: Frames \(prep[0])-\(prep[1])")
                    .font(.subheadline)
            }
            
            if let release = shotPhases.releasePoint {
                Text("Release Point: Frame \(release)")
                    .font(.subheadline)
            }
            
            if let followThrough = shotPhases.followThroughPhase {
                Text("Follow Through: Frames \(followThrough[0])-\(followThrough[1])")
                    .font(.subheadline)
            }
        }
        .padding()
        .background(Color.blue.opacity(0.1))
        .cornerRadius(8)
    }
}

struct RecommendationCard: View {
    let text: String
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: "lightbulb.fill")
                .foregroundColor(.yellow)
                .font(.system(size: 16))
                .padding(.top, 2)
            
            Text(text)
                .font(.subheadline)
                .fixedSize(horizontal: false, vertical: true)
            
            Spacer()
        }
        .padding()
        .background(Color.yellow.opacity(0.1))
        .cornerRadius(8)
    }
}

struct BallDetectionInfoView: View {
    let ballInfo: BallDetectionInfo
    
    var body: some View {
        VStack(spacing: 12) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Ball Detection Results")
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundColor(.primary)
                    
                    Text("\(ballInfo.ballDetectedFrames) of \(ballInfo.totalFrames) frames")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 4) {
                    Text("Ball Holder Tracked")
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundColor(.orange)
                    
                    Text("\(ballInfo.ballHolderFrames) frames")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            // Detection success rate bar
            let detectionRate = ballInfo.totalFrames > 0 ? Double(ballInfo.ballDetectedFrames) / Double(ballInfo.totalFrames) : 0.0
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    Rectangle()
                        .fill(Color.gray.opacity(0.3))
                        .frame(height: 4)
                        .cornerRadius(2)
                    
                    Rectangle()
                        .fill(Color.orange)
                        .frame(width: geometry.size.width * CGFloat(detectionRate), height: 4)
                        .cornerRadius(2)
                }
            }
            .frame(height: 4)
            
            Text("Detection Rate: \(Int(detectionRate * 100))%")
                .font(.caption)
                .foregroundColor(.secondary)
                .frame(maxWidth: .infinity, alignment: .center)
        }
        .padding()
        .background(Color.orange.opacity(0.05))
        .cornerRadius(12)
    }
}

struct ShooterInfoView: View {
    let shooterInfo: ShooterInfo
    
    var body: some View {
        VStack(spacing: 12) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Shooter Identified")
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundColor(.primary)
                    
                    Text("\(shooterInfo.totalPeopleDetected) players detected")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 4) {
                    Text("Player #\(shooterInfo.shooterId + 1)")
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundColor(.blue)
                    
                    Text("Confidence: \(Int(shooterInfo.confidence * 100))%")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            // Confidence bar
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    Rectangle()
                        .fill(Color.gray.opacity(0.3))
                        .frame(height: 4)
                        .cornerRadius(2)
                    
                    Rectangle()
                        .fill(Color.blue)
                        .frame(width: geometry.size.width * CGFloat(shooterInfo.confidence), height: 4)
                        .cornerRadius(2)
                }
            }
            .frame(height: 4)
        }
        .padding()
        .background(Color.blue.opacity(0.05))
        .cornerRadius(12)
    }
}

struct ReleaseFrameView: View {
    let releaseFrame: ReleaseFrame
    let shooterInfo: ShooterInfo?
    @State private var showingFullScreen = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Frame \(releaseFrame.frameNumber)")
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundColor(.primary)
                    
                    if let ballHolderId = releaseFrame.ballHolderId {
                        let ballDetectedText = releaseFrame.ballDetected == true ? " (Ball Detected)" : ""
                        Text("Ball Holder #\(ballHolderId + 1) - Release Moment\(ballDetectedText)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    } else if let shooterId = releaseFrame.shooterId {
                        Text("Player #\(shooterId + 1) - Ball Release Moment")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    } else {
                        Text("Ball Release Moment")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                Spacer()
                
                Button("View Full Size") {
                    showingFullScreen = true
                }
                .font(.caption)
                .foregroundColor(.blue)
            }
            
            // Display the cropped frame
            if let imageData = releaseFrame.imageData,
               let data = Data(base64Encoded: imageData),
               let uiImage = UIImage(data: data) {
                
                Button(action: {
                    showingFullScreen = true
                }) {
                    Image(uiImage: uiImage)
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(maxHeight: 200)
                        .cornerRadius(8)
                        .overlay(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(Color.blue.opacity(0.3), lineWidth: 2)
                        )
                }
                .buttonStyle(PlainButtonStyle())
                
                Text("Tap image to view full size")
                    .font(.caption2)
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .center)
            } else {
                RoundedRectangle(cornerRadius: 8)
                    .fill(Color.gray.opacity(0.3))
                    .frame(height: 200)
                    .overlay(
                        VStack {
                            Image(systemName: "photo")
                                .font(.largeTitle)
                                .foregroundColor(.gray)
                            Text("Image not available")
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                    )
            }
        }
        .padding()
        .background(Color.blue.opacity(0.05))
        .cornerRadius(12)
        .sheet(isPresented: $showingFullScreen) {
            FullScreenImageView(releaseFrame: releaseFrame, shooterInfo: shooterInfo)
        }
    }
}

struct FullScreenImageView: View {
    let releaseFrame: ReleaseFrame
    let shooterInfo: ShooterInfo?
    @Environment(\.presentationMode) var presentationMode
    
    var body: some View {
        NavigationView {
            ZStack {
                Color.black.ignoresSafeArea()
                
                if let imageData = releaseFrame.imageData,
                   let data = Data(base64Encoded: imageData),
                   let uiImage = UIImage(data: data) {
                    
                    ScrollView([.horizontal, .vertical]) {
                        Image(uiImage: uiImage)
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    VStack {
                        Image(systemName: "photo")
                            .font(.system(size: 50))
                            .foregroundColor(.gray)
                        Text("Image not available")
                            .foregroundColor(.gray)
                    }
                }
            }
            .navigationTitle(releaseFrame.ballHolderId != nil ? 
                            "Ball Holder #\(releaseFrame.ballHolderId! + 1) - Frame \(releaseFrame.frameNumber)" : 
                            (releaseFrame.shooterId != nil ? 
                             "Player #\(releaseFrame.shooterId! + 1) - Frame \(releaseFrame.frameNumber)" : 
                             "Release Frame \(releaseFrame.frameNumber)"))
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(trailing: Button("Done") {
                presentationMode.wrappedValue.dismiss()
            })
        }
    }
}

struct ComprehensiveReleaseFrameView: View {
    let releaseFrame: ReleaseFrame
    let shooterInfo: ShooterInfo?
    
    @State private var showingOriginalFrame = false
    @State private var selectedPlayerCrop: PlayerCrop?
    
    var body: some View {
        VStack(spacing: 15) {
            // Frame info header
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Frame \(releaseFrame.frameNumber)")
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundColor(.primary)
                    
                    if let ballHolderId = releaseFrame.ballHolderId {
                        let ballDetectedText = releaseFrame.ballDetected == true ? " (Ball Detected)" : ""
                        Text("Ball Holder #\(ballHolderId + 1) - Release Moment\(ballDetectedText)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    } else {
                        Text("Ball Release Moment")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    
                    Text("\(releaseFrame.totalPlayersDetected ?? 1) players detected")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
            }
            
            // 1. Original Full Frame
            if let originalFrame = releaseFrame.originalFrame {
                VStack(alignment: .leading, spacing: 8) {
                    Text("📸 Original Frame")
                        .font(.subheadline)
                        .fontWeight(.medium)
                    
                    Button(action: { showingOriginalFrame = true }) {
                        if let imageData = Data(base64Encoded: originalFrame.imageData),
                           let uiImage = UIImage(data: imageData) {
                            Image(uiImage: uiImage)
                                .resizable()
                                .aspectRatio(contentMode: .fit)
                                .frame(maxHeight: 120)
                                .cornerRadius(8)
                        } else {
                            Rectangle()
                                .fill(Color.gray.opacity(0.3))
                                .frame(height: 120)
                                .cornerRadius(8)
                                .overlay(Text("Image not available"))
                        }
                    }
                    .buttonStyle(PlainButtonStyle())
                }
            }
            
            // 2. Ball Holder Crop
            if let ballHolderCrop = releaseFrame.ballHolderCrop {
                VStack(alignment: .leading, spacing: 8) {
                    Text("🏀 Ball Holder (Player #\(ballHolderCrop.personId + 1))")
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundColor(.orange)
                    
                    Button(action: { selectedPlayerCrop = ballHolderCrop }) {
                        PlayerCropImageView(playerCrop: ballHolderCrop)
                    }
                    .buttonStyle(PlainButtonStyle())
                }
            }
            
            // 3. All Other Players
            if let allPlayerCrops = releaseFrame.allPlayerCrops, !allPlayerCrops.isEmpty {
                VStack(alignment: .leading, spacing: 8) {
                    Text("👥 Other Players (\(allPlayerCrops.count))")
                        .font(.subheadline)
                        .fontWeight(.medium)
                    
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 10) {
                            ForEach(allPlayerCrops, id: \.personId) { playerCrop in
                                VStack(spacing: 4) {
                                    Button(action: { selectedPlayerCrop = playerCrop }) {
                                        PlayerCropImageView(playerCrop: playerCrop)
                                            .frame(width: 80, height: 120)
                                    }
                                    .buttonStyle(PlainButtonStyle())
                                    
                                    Text("Player #\(playerCrop.personId + 1)")
                                        .font(.caption2)
                                        .foregroundColor(.secondary)
                                }
                            }
                        }
                        .padding(.horizontal, 4)
                    }
                }
            }
            
            // Legacy support for old format
            if releaseFrame.originalFrame == nil && releaseFrame.ballHolderCrop == nil {
                LegacyReleaseFrameView(releaseFrame: releaseFrame, shooterInfo: shooterInfo)
            }
        }
        .padding()
        .background(Color.blue.opacity(0.05))
        .cornerRadius(12)
        .sheet(isPresented: $showingOriginalFrame) {
            if let originalFrame = releaseFrame.originalFrame {
                FullScreenOriginalFrameView(originalFrame: originalFrame, frameNumber: releaseFrame.frameNumber)
            }
        }
        .sheet(item: $selectedPlayerCrop) { playerCrop in
            FullScreenPlayerCropView(playerCrop: playerCrop, frameNumber: releaseFrame.frameNumber)
        }
    }
}

struct PlayerCropImageView: View {
    let playerCrop: PlayerCrop
    
    var body: some View {
        if let imageData = Data(base64Encoded: playerCrop.imageData),
           let uiImage = UIImage(data: imageData) {
            Image(uiImage: uiImage)
                .resizable()
                .aspectRatio(contentMode: .fit)
                .frame(maxHeight: 120)
                .cornerRadius(8)
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(playerCrop.isBallHolder ? Color.orange : Color.gray.opacity(0.3), lineWidth: playerCrop.isBallHolder ? 2 : 1)
                )
        } else {
            Rectangle()
                .fill(Color.gray.opacity(0.3))
                .frame(height: 120)
                .cornerRadius(8)
                .overlay(Text("Image not available").font(.caption))
        }
    }
}

struct FullScreenOriginalFrameView: View {
    let originalFrame: OriginalFrame
    let frameNumber: Int
    @Environment(\.presentationMode) var presentationMode
    
    var body: some View {
        NavigationView {
            VStack {
                if let imageData = Data(base64Encoded: originalFrame.imageData),
                   let uiImage = UIImage(data: imageData) {
                    Image(uiImage: uiImage)
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .clipped()
                } else {
                    Rectangle()
                        .fill(Color.gray.opacity(0.3))
                        .overlay(
                            Text("Image not available")
                                .foregroundColor(.gray)
                        )
                }
            }
            .navigationTitle("Original Frame \(frameNumber)")
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(trailing: Button("Done") {
                presentationMode.wrappedValue.dismiss()
            })
        }
    }
}

struct FullScreenPlayerCropView: View {
    let playerCrop: PlayerCrop
    let frameNumber: Int
    @Environment(\.presentationMode) var presentationMode
    
    var body: some View {
        NavigationView {
            VStack {
                if let imageData = Data(base64Encoded: playerCrop.imageData),
                   let uiImage = UIImage(data: imageData) {
                    Image(uiImage: uiImage)
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .clipped()
                } else {
                    Rectangle()
                        .fill(Color.gray.opacity(0.3))
                        .overlay(
                            Text("Image not available")
                                .foregroundColor(.gray)
                        )
                }
            }
            .navigationTitle("\(playerCrop.isBallHolder ? "Ball Holder" : "Player") #\(playerCrop.personId + 1) - Frame \(frameNumber)")
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(trailing: Button("Done") {
                presentationMode.wrappedValue.dismiss()
            })
        }
    }
}

struct LegacyReleaseFrameView: View {
    let releaseFrame: ReleaseFrame
    let shooterInfo: ShooterInfo?
    
    @State private var showingFullScreen = false
    
    var body: some View {
        VStack(spacing: 12) {
            HStack {
                Text("Legacy Format")
                    .font(.caption)
                    .foregroundColor(.secondary)
                Spacer()
                Button("View Full Size") {
                    showingFullScreen = true
                }
                .font(.caption)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(6)
            }
            
            if let imageData = releaseFrame.imageData,
               let data = Data(base64Encoded: imageData),
               let uiImage = UIImage(data: data) {
                Image(uiImage: uiImage)
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(maxHeight: 200)
                    .cornerRadius(8)
                    .onTapGesture {
                        showingFullScreen = true
                    }
            }
        }
        .sheet(isPresented: $showingFullScreen) {
            if let imageData = releaseFrame.imageData {
                LegacyFullScreenImageView(imageData: imageData, releaseFrame: releaseFrame, shooterInfo: shooterInfo)
            }
        }
    }
}

struct LegacyFullScreenImageView: View {
    let imageData: String
    let releaseFrame: ReleaseFrame
    let shooterInfo: ShooterInfo?
    @Environment(\.presentationMode) var presentationMode
    
    var body: some View {
        NavigationView {
            ZStack {
                Color.black.ignoresSafeArea()
                
                if let data = Data(base64Encoded: imageData),
                   let uiImage = UIImage(data: data) {
                    
                    ScrollView([.horizontal, .vertical]) {
                        Image(uiImage: uiImage)
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                            .scaleEffect(1.0)
                    }
                } else {
                    Rectangle()
                        .fill(Color.gray.opacity(0.3))
                        .overlay(
                            Text("Image not available")
                                .foregroundColor(.gray)
                        )
                }
            }
            .navigationTitle("Legacy Release Frame \(releaseFrame.frameNumber)")
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(trailing: Button("Done") {
                presentationMode.wrappedValue.dismiss()
            })
        }
    }
}

extension PlayerCrop: Identifiable {
    var id: Int { personId }
}

struct AnalysisView_Previews: PreviewProvider {
    static var previews: some View {
        let sampleResult = AnalysisResult(
            shotPhases: ShotPhases(
                totalFrames: 30,
                preparationPhase: [0, 10],
                releasePoint: 15,
                followThroughPhase: [16, 29]
            ),
            formAnalysis: FormAnalysis(
                elbowAlignment: "good",
                elbowIssues: [],
                handPosition: "needs_improvement",
                handIssues: ["hands_too_close"],
                bodyAlignment: "good",
                alignmentIssues: [],
                followThrough: "good",
                followThroughIssues: []
            ),
            recommendations: [
                "Spread your hands wider on the ball - shooting hand behind, guide hand on the side",
                "Focus on one technique at a time during practice for best results"
            ],
            fileInfo: FileInfo(filename: "demo_shot.mp4", fileType: "video"),
            releaseFrame: nil,
            shooterInfo: nil,
            ballDetectionInfo: nil
        )
        
        AnalysisView(analysisResult: sampleResult)
    }
}
