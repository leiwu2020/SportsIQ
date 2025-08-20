import SwiftUI

struct AnalysisResult: Codable {
    let shotPhases: ShotPhases?
    let formAnalysis: FormAnalysis?
    let recommendations: [String]?
    let fileInfo: FileInfo?
    let releaseFrame: ReleaseFrame?
    let shooterInfo: ShooterInfo?
    let ballDetectionInfo: BallDetectionInfo?
    
    // New streamlined analysis fields
    let shooterId: Int?
    let totalFramesAnalyzed: Int?
    let shooterTrackedFrames: Int?
    let releaseFrameNumber: Int?
    let analysisType: String?
    let shootingSequence: ShootingSequence?
    
    enum CodingKeys: String, CodingKey {
        case shotPhases = "shot_phases"
        case formAnalysis = "form_analysis"
        case recommendations
        case fileInfo = "file_info"
        case releaseFrame = "release_frame"
        case shooterInfo = "shooter_info"
        case ballDetectionInfo = "ball_detection_info"
        case shooterId = "shooter_id"
        case totalFramesAnalyzed = "total_frames_analyzed"
        case shooterTrackedFrames = "shooter_tracked_frames"
        case releaseFrameNumber = "release_frame_number"
        case analysisType = "analysis_type"
        case shootingSequence = "shooting_sequence"
    }
    
    // Helper computed properties
    var isStreamlinedAnalysis: Bool {
        return analysisType == "streamlined_shooter_tracking"
    }
    
    var isFallbackAnalysis: Bool {
        return analysisType == "fallback_comprehensive" || analysisType == "fallback_error"
    }
}

struct ShotPhases: Codable {
    let totalFrames: Int?
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
    let elbowAlignment: String?
    let elbowIssues: [String]?
    let handPosition: String?
    let handIssues: [String]?
    let bodyAlignment: String?
    let alignmentIssues: [String]?
    let followThrough: String?
    let followThroughIssues: [String]?
    
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
    let filename: String?
    let fileType: String?
    
    enum CodingKeys: String, CodingKey {
        case filename
        case fileType = "file_type"
    }
}

struct ReleaseFrame: Codable {
    let originalFrame: OriginalFrame?
    let allPlayerCrops: [PlayerCrop]?
    let ballDetected: Bool?
    let ballHolderCrop: PlayerCrop?
    let ballHolderId: Int?
    let totalPlayersDetected: Int?
    
    enum CodingKeys: String, CodingKey {
        case originalFrame = "original_frame"
        case allPlayerCrops = "all_player_crops"
        case ballDetected = "ball_detected"
        case ballHolderCrop = "ball_holder_crop"
        case ballHolderId = "ball_holder_id"
        case totalPlayersDetected = "total_players_detected"
    }
}

struct OriginalFrame: Codable {
    let frameNumber: Int?
    let imageData: String?
    let width: Int?
    let height: Int?
    
    enum CodingKeys: String, CodingKey {
        case frameNumber = "frame_number"
        case imageData = "image_data"
        case width
        case height
    }
}

struct PlayerCrop: Codable {
    let imageData: String?
    let personId: Int?
    let isBallHolder: Bool?
    let cropCoordinates: CropCoordinates?
    let croppedSize: ImageSize?
    
    enum CodingKeys: String, CodingKey {
        case imageData = "image_data"
        case personId = "person_id"
        case isBallHolder = "is_ball_holder"
        case cropCoordinates = "crop_coordinates"
        case croppedSize = "cropped_size"
    }
}

struct CropCoordinates: Codable {
    let x: Int?
    let y: Int?
    let width: Int?
    let height: Int?
}

struct ImageSize: Codable {
    let width: Int?
    let height: Int?
}

struct ShooterInfo: Codable {
    let id: Int?
    let confidence: Double?
    let shootingSequenceFrames: [Int]?
    let totalFramesDetected: Int?
    
    enum CodingKeys: String, CodingKey {
        case id
        case confidence
        case shootingSequenceFrames = "shooting_sequence_frames"
        case totalFramesDetected = "total_frames_detected"
    }
}

struct BallDetectionInfo: Codable {
    let ballDetected: Bool?
    let ballPositions: [BallPosition?]?
    let detectionConfidence: Double?
    
    enum CodingKeys: String, CodingKey {
        case ballDetected = "ball_detected"
        case ballPositions = "ball_positions"
        case detectionConfidence = "detection_confidence"
    }
}

struct BallPosition: Codable {
    let x: Int?
    let y: Int?
    let radius: Int?
}

struct ShootingSequence: Codable {
    let totalFrames: Int?
    let frames: [SequenceFrame]?
    let shooterId: Int?
    let releaseFrameNumber: Int?
    
    enum CodingKeys: String, CodingKey {
        case totalFrames = "total_frames"
        case frames
        case shooterId = "shooter_id"
        case releaseFrameNumber = "release_frame_number"
    }
}

struct SequenceFrame: Codable {
    let frameNumber: Int?
    let phaseLabel: String?
    let ballPosition: BallPosition?
    let boundingBox: BoundingBox?
    let fullFrameWithBbox: FrameWithBbox?
    let shooterCrop: ShooterCrop?
    let shooterConfidence: Double?
    
    enum CodingKeys: String, CodingKey {
        case frameNumber = "frame_number"
        case phaseLabel = "phase_label"
        case ballPosition = "ball_position"
        case boundingBox = "bounding_box"
        case fullFrameWithBbox = "full_frame_with_bbox"
        case shooterCrop = "shooter_crop"
        case shooterConfidence = "shooter_confidence"
    }
}

struct BoundingBox: Codable {
    let x: Int?
    let y: Int?
    let width: Int?
    let height: Int?
}

struct FrameWithBbox: Codable {
    let frameNumber: Int?
    let imageData: String?
    let width: Int?
    let height: Int?
    
    enum CodingKeys: String, CodingKey {
        case frameNumber = "frame_number"
        case imageData = "image_data"
        case width
        case height
    }
}

struct ShooterCrop: Codable {
    let imageData: String?
    let personId: Int?
    let cropCoordinates: CropCoordinates?
    let croppedSize: ImageSize?
    
    enum CodingKeys: String, CodingKey {
        case imageData = "image_data"
        case personId = "person_id"
        case cropCoordinates = "crop_coordinates"
        case croppedSize = "cropped_size"
    }
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
                        
                        if let fileInfo = analysisResult.fileInfo, let filename = fileInfo.filename {
                            Text(filename)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        
                        if let analysisType = analysisResult.analysisType {
                            Text("Analysis Type: \(analysisType)")
                                .font(.caption2)
                                        .foregroundColor(.secondary)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 4)
                                .background(Color.gray.opacity(0.2))
                                .cornerRadius(8)
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    
                    // Analysis Summary (if available)
                    if let totalFrames = analysisResult.totalFramesAnalyzed,
                       let trackedFrames = analysisResult.shooterTrackedFrames,
                       let shooterId = analysisResult.shooterId {
                        VStack(alignment: .leading, spacing: 15) {
                            HStack {
                                Image(systemName: "chart.bar.fill")
                                    .foregroundColor(.blue)
                                Text("Analysis Summary")
                                    .font(.headline)
                                    .fontWeight(.semibold)
                            }
                            
                            VStack(alignment: .leading, spacing: 8) {
                                HStack {
                                    Text("Total Frames Analyzed:")
                                        .fontWeight(.medium)
                                    Spacer()
                                    Text("\(totalFrames)")
                                        .foregroundColor(.secondary)
                                }
                                
                            HStack {
                                    Text("Shooter Tracked Frames:")
                                        .fontWeight(.medium)
                                    Spacer()
                                    Text("\(trackedFrames)")
                                        .foregroundColor(.secondary)
                                }
                                
                            HStack {
                                    Text("Shooter ID:")
                                        .fontWeight(.medium)
                                    Spacer()
                                    Text("\(shooterId)")
                                        .foregroundColor(.secondary)
                                }
                                
                                if let releaseFrameNum = analysisResult.releaseFrameNumber {
                                    HStack {
                                        Text("Release Frame:")
                                            .fontWeight(.medium)
                                        Spacer()
                                        Text("\(releaseFrameNum)")
                                .foregroundColor(.secondary)
                                    }
                                }
                            }
                            .padding()
                            .background(Color.gray.opacity(0.1))
                            .cornerRadius(12)
                        }
                    }
                    
                    // Ball Release Frame (if available)
                    if let releaseFrame = analysisResult.releaseFrame {
                        VStack(alignment: .leading, spacing: 15) {
                            HStack {
                                Image(systemName: "target")
                                    .foregroundColor(.orange)
                                Text("Ball Release Frame")
                                .font(.headline)
                                .fontWeight(.semibold)
                            }
                            
                            // Show the original frame image if available
                            if let originalFrame = releaseFrame.originalFrame {
                                VStack(spacing: 10) {
                                    if let imageData = originalFrame.imageData, let uiImage = UIImage(data: Data(base64Encoded: imageData) ?? Data()) {
                                        Image(uiImage: uiImage)
                                            .resizable()
                                            .aspectRatio(contentMode: .fit)
                        .frame(maxWidth: .infinity)
                        .cornerRadius(12)
                                    } else {
                                        Text("No image data available.")
                                            .foregroundColor(.secondary)
                        .padding()
                                            .frame(maxWidth: .infinity)
                                            .background(Color.gray.opacity(0.1))
                        .cornerRadius(12)
                                    }
                                    
                                    if let frameNumber = originalFrame.frameNumber {
                                        Text("Frame \(frameNumber)")
                                            .font(.caption)
                                            .foregroundColor(.secondary)
                                    }
                                }
                            } else {
                                Text("No release frame data available.")
                                    .foregroundColor(.secondary)
        .padding()
                                    .frame(maxWidth: .infinity)
        .background(Color.gray.opacity(0.1))
        .cornerRadius(12)
                            }
                            
                            // Show additional release frame info if available
                            if let ballDetected = releaseFrame.ballDetected {
        HStack {
                                    Image(systemName: ballDetected ? "basketball.fill" : "basketball")
                                        .foregroundColor(ballDetected ? .orange : .gray)
                                    Text("Ball Detected: \(ballDetected ? "Yes" : "No")")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
                            if let totalPlayers = releaseFrame.totalPlayersDetected {
                                HStack {
                                    Image(systemName: "person.2.fill")
                                        .foregroundColor(.blue)
                                    Text("Players Detected: \(totalPlayers)")
                    .font(.caption)
                                        .foregroundColor(.secondary)
                                }
                            }
                        }
                    }
                    
                    // Shooter Info (if available)
                    if let shooterInfo = analysisResult.shooterInfo {
                        VStack(alignment: .leading, spacing: 15) {
                            HStack {
                                Image(systemName: "person.fill")
                                    .foregroundColor(.green)
                                Text("Shooter Information")
                                    .font(.headline)
                                    .fontWeight(.semibold)
                            }
                            
                            VStack(alignment: .leading, spacing: 8) {
                                if let id = shooterInfo.id {
            HStack {
                                        Text("ID:")
                        .fontWeight(.medium)
                Spacer()
                                        Text("\(id)")
                        .foregroundColor(.secondary)
                }
            }
            
                                if let confidence = shooterInfo.confidence {
            HStack {
                                        Text("Confidence:")
                        .fontWeight(.medium)
                Spacer()
                                        Text(String(format: "%.2f", confidence))
                        .foregroundColor(.secondary)
                }
            }
            
                                if let totalFrames = shooterInfo.totalFramesDetected {
            HStack {
                                        Text("Frames Detected:")
                        .fontWeight(.medium)
                                        Spacer()
                                        Text("\(totalFrames)")
                            .foregroundColor(.secondary)
                    }
                }
                
                                if let sequenceFrames = shooterInfo.shootingSequenceFrames, !sequenceFrames.isEmpty {
                                    HStack {
                                        Text("Sequence Frames:")
                                            .fontWeight(.medium)
                Spacer()
                                        Text("\(sequenceFrames.count) frames")
                    .foregroundColor(.secondary)
                                    }
            }
        }
        .padding()
                            .background(Color.gray.opacity(0.1))
        .cornerRadius(12)
                        }
                    }
                    
                    // Ball Detection Info (if available)
                    if let ballInfo = analysisResult.ballDetectionInfo {
                        VStack(alignment: .leading, spacing: 15) {
                            HStack {
                                Image(systemName: "basketball.fill")
                                    .foregroundColor(.orange)
                                Text("Ball Detection")
                                    .font(.headline)
                                    .fontWeight(.semibold)
                            }
                            
                            VStack(alignment: .leading, spacing: 8) {
                                if let ballDetected = ballInfo.ballDetected {
            HStack {
                                        Text("Ball Detected:")
                        .fontWeight(.medium)
                                        Spacer()
                                        Text(ballDetected ? "Yes" : "No")
                            .foregroundColor(.secondary)
                    }
                }
                
                                if let confidence = ballInfo.detectionConfidence {
                                    HStack {
                                        Text("Detection Confidence:")
                                            .fontWeight(.medium)
                Spacer()
                                        Text(String(format: "%.2f", confidence))
                                            .foregroundColor(.secondary)
                                    }
                                }
                                
                                if let positions = ballInfo.ballPositions, !positions.isEmpty {
                                    HStack {
                                        Text("Ball Positions:")
                        .fontWeight(.medium)
                                        Spacer()
                                        Text("\(positions.count) detected")
                                        .foregroundColor(.secondary)
                                }
            }
        }
        .padding()
                            .background(Color.gray.opacity(0.1))
        .cornerRadius(12)
                        }
                    }
                    
                    // Form Analysis (if available)
                    if let formAnalysis = analysisResult.formAnalysis {
        VStack(alignment: .leading, spacing: 15) {
            HStack {
                                Image(systemName: "figure.basketball")
                                    .foregroundColor(.purple)
                                Text("Form Analysis")
                        .font(.headline)
                        .fontWeight(.semibold)
                            }
                            
                            VStack(alignment: .leading, spacing: 12) {
                                if let elbowAlignment = formAnalysis.elbowAlignment {
                                    FormAnalysisRow(title: "Elbow Alignment", value: elbowAlignment)
                                }
                                
                                if let handPosition = formAnalysis.handPosition {
                                    FormAnalysisRow(title: "Hand Position", value: handPosition)
                                }
                                
                                if let bodyAlignment = formAnalysis.bodyAlignment {
                                    FormAnalysisRow(title: "Body Alignment", value: bodyAlignment)
                                }
                                
                                if let followThrough = formAnalysis.followThrough {
                                    FormAnalysisRow(title: "Follow Through", value: followThrough)
            }
        }
        .padding()
                            .background(Color.gray.opacity(0.1))
        .cornerRadius(12)
                        }
                    }
                    
                    // Recommendations (if available)
                    if let recommendations = analysisResult.recommendations, !recommendations.isEmpty {
        VStack(alignment: .leading, spacing: 15) {
            HStack {
                                Image(systemName: "lightbulb.fill")
                                    .foregroundColor(.yellow)
                                Text("Recommendations")
                                    .font(.headline)
                                    .fontWeight(.semibold)
                            }
                            
                            VStack(alignment: .leading, spacing: 8) {
                                ForEach(recommendations, id: \.self) { recommendation in
                                    HStack(alignment: .top) {
                                        Image(systemName: "arrow.right.circle.fill")
                                            .foregroundColor(.blue)
                            .font(.caption)
                                        Text(recommendation)
                                            .font(.body)
                                    }
                                }
                            }
                            .padding()
                            .background(Color.gray.opacity(0.1))
                            .cornerRadius(12)
                        }
                    }
                    
                    // Action Button
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

// Helper view for form analysis rows
struct FormAnalysisRow: View {
    let title: String
    let value: String
    
    var body: some View {
        HStack {
            Text(title + ":")
                .fontWeight(.medium)
            Spacer()
            Text(value)
                .foregroundColor(.secondary)
        }
    }
}

struct AnalysisView_Previews: PreviewProvider {
    static var previews: some View {
        AnalysisView(analysisResult: AnalysisResult(
            shotPhases: nil,
            formAnalysis: nil,
            recommendations: nil,
            fileInfo: FileInfo(filename: "test.MOV", fileType: "video"),
            releaseFrame: nil,
            shooterInfo: nil,
            ballDetectionInfo: nil,
            shooterId: 1,
            totalFramesAnalyzed: 150,
            shooterTrackedFrames: 120,
            releaseFrameNumber: 75,
            analysisType: "streamlined_shooter_tracking",
            shootingSequence: nil
        ))
    }
}

