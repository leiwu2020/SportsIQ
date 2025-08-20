import SwiftUI

struct ShootingFormGuideView: View {
    @Environment(\.presentationMode) var presentationMode
    @State private var selectedPhase = 0
    
    private let phases = ["Setup", "Preparation", "Release", "Follow Through"]
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Header
                    VStack(spacing: 10) {
                        Image(systemName: "target")
                            .font(.system(size: 50))
                            .foregroundColor(.orange)
                        
                        Text("Perfect Shooting Form")
                            .font(.title2)
                            .fontWeight(.bold)
                        
                        Text("Learn the optimal hand and arm positioning")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding()
                    
                    // Phase Selector
                    Picker("Phase", selection: $selectedPhase) {
                        ForEach(0..<phases.count, id: \.self) { index in
                            Text(phases[index]).tag(index)
                        }
                    }
                    .pickerStyle(SegmentedPickerStyle())
                    .padding(.horizontal)
                    
                    // Phase Content
                    PhaseContentView(phase: selectedPhase)
                        .animation(.easeInOut, value: selectedPhase)
                    
                    // Navigation Buttons
                    HStack(spacing: 20) {
                        Button("Previous") {
                            if selectedPhase > 0 {
                                selectedPhase -= 1
                            }
                        }
                        .disabled(selectedPhase == 0)
                        .foregroundColor(selectedPhase == 0 ? .gray : .blue)
                        
                        Spacer()
                        
                        Button("Next") {
                            if selectedPhase < phases.count - 1 {
                                selectedPhase += 1
                            }
                        }
                        .disabled(selectedPhase == phases.count - 1)
                        .foregroundColor(selectedPhase == phases.count - 1 ? .gray : .blue)
                    }
                    .padding(.horizontal, 30)
                    .font(.headline)
                }
            }
            .navigationTitle("Shooting Guide")
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(trailing: Button("Done") {
                presentationMode.wrappedValue.dismiss()
            })
        }
    }
}

struct PhaseContentView: View {
    let phase: Int
    
    var body: some View {
        VStack(spacing: 20) {
            // Phase illustration
            PhaseIllustrationView(phase: phase)
            
            // Phase details
            PhaseDetailsView(phase: phase)
        }
        .padding()
    }
}

struct PhaseIllustrationView: View {
    let phase: Int
    
    var body: some View {
        VStack {
            // Simple stick figure representation
            ZStack {
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.gray.opacity(0.1))
                    .frame(height: 200)
                
                VStack(spacing: 10) {
                    // Basketball
                    Circle()
                        .fill(Color.orange)
                        .frame(width: 30, height: 30)
                        .overlay(
                            Image(systemName: "basketball.fill")
                                .foregroundColor(.black)
                                .font(.system(size: 16))
                        )
                        .offset(ballPosition)
                    
                    // Player representation
                    VStack(spacing: 5) {
                        // Head
                        Circle()
                            .fill(Color.blue.opacity(0.7))
                            .frame(width: 20, height: 20)
                        
                        // Arms and body
                        HStack(spacing: armSpacing) {
                            // Left arm (guide hand)
                            RoundedRectangle(cornerRadius: 2)
                                .fill(Color.blue.opacity(0.7))
                                .frame(width: 4, height: armLength)
                                .rotationEffect(leftArmAngle)
                            
                            // Body
                            RoundedRectangle(cornerRadius: 4)
                                .fill(Color.blue.opacity(0.7))
                                .frame(width: 8, height: 40)
                            
                            // Right arm (shooting hand)
                            RoundedRectangle(cornerRadius: 2)
                                .fill(Color.blue.opacity(0.7))
                                .frame(width: 4, height: armLength)
                                .rotationEffect(rightArmAngle)
                        }
                        
                        // Legs
                        HStack(spacing: 5) {
                            RoundedRectangle(cornerRadius: 2)
                                .fill(Color.blue.opacity(0.7))
                                .frame(width: 4, height: 30)
                            
                            RoundedRectangle(cornerRadius: 2)
                                .fill(Color.blue.opacity(0.7))
                                .frame(width: 4, height: 30)
                        }
                    }
                }
            }
            
            Text(phaseTitle)
                .font(.headline)
                .fontWeight(.semibold)
        }
    }
    
    private var phaseTitle: String {
        switch phase {
        case 0: return "Setup Position"
        case 1: return "Preparation Phase"
        case 2: return "Release Point"
        case 3: return "Follow Through"
        default: return "Unknown Phase"
        }
    }
    
    private var ballPosition: CGSize {
        switch phase {
        case 0: return CGSize(width: 0, height: 20)  // Chest level
        case 1: return CGSize(width: 0, height: -10) // Above head
        case 2: return CGSize(width: 0, height: -30) // Highest point
        case 3: return CGSize(width: 10, height: -40) // Released
        default: return CGSize.zero
        }
    }
    
    private var leftArmAngle: Angle {
        switch phase {
        case 0: return .degrees(-30)  // Supporting ball
        case 1: return .degrees(-45)  // Preparing
        case 2: return .degrees(-60)  // Releasing
        case 3: return .degrees(-20)  // Away from ball
        default: return .degrees(0)
        }
    }
    
    private var rightArmAngle: Angle {
        switch phase {
        case 0: return .degrees(30)   // Behind ball
        case 1: return .degrees(45)   // Cocked back
        case 2: return .degrees(75)   // Extending
        case 3: return .degrees(90)   // Full extension
        default: return .degrees(0)
        }
    }
    
    private var armLength: CGFloat {
        switch phase {
        case 2, 3: return 35  // Extended
        default: return 25    // Bent
        }
    }
    
    private var armSpacing: CGFloat {
        switch phase {
        case 2, 3: return 25  // Extended
        default: return 15    // Closer
        }
    }
}

struct PhaseDetailsView: View {
    let phase: Int
    
    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            ForEach(phaseDetails, id: \.title) { detail in
                DetailCard(
                    title: detail.title,
                    description: detail.description,
                    icon: detail.icon,
                    color: detail.color
                )
            }
        }
    }
    
    private var phaseDetails: [PhaseDetail] {
        switch phase {
        case 0: return setupDetails
        case 1: return preparationDetails
        case 2: return releaseDetails
        case 3: return followThroughDetails
        default: return []
        }
    }
    
    private var setupDetails: [PhaseDetail] {
        [
            PhaseDetail(
                title: "Ball Position",
                description: "Hold ball at chest to chin level, centered in front of body",
                icon: "circle.fill",
                color: .orange
            ),
            PhaseDetail(
                title: "Shooting Hand",
                description: "Behind the ball, fingers spread wide, palm facing forward",
                icon: "hand.raised.fill",
                color: .blue
            ),
            PhaseDetail(
                title: "Guide Hand",
                description: "On the side of ball, thumb pointing up, light support only",
                icon: "hand.point.up.fill",
                color: .green
            ),
            PhaseDetail(
                title: "Elbow Alignment",
                description: "Shooting elbow directly under the ball, 90-degree angle",
                icon: "arrow.down",
                color: .purple
            )
        ]
    }
    
    private var preparationDetails: [PhaseDetail] {
        [
            PhaseDetail(
                title: "Ball Position",
                description: "Raise ball above forehead, in front of shooting eye",
                icon: "arrow.up",
                color: .orange
            ),
            PhaseDetail(
                title: "Shooting Hand",
                description: "Forms 'C' shape, wrist cocked back, index finger on air valve",
                icon: "c.circle.fill",
                color: .blue
            ),
            PhaseDetail(
                title: "Guide Hand",
                description: "Light contact, thumb forms 'T' with shooting thumb",
                icon: "t.circle.fill",
                color: .green
            ),
            PhaseDetail(
                title: "Elbow Position",
                description: "Still under ball, aligned with basket, forearm vertical",
                icon: "arrow.down.circle",
                color: .purple
            )
        ]
    }
    
    private var releaseDetails: [PhaseDetail] {
        [
            PhaseDetail(
                title: "Ball Position",
                description: "At highest point, above and in front of head",
                icon: "arrow.up.circle.fill",
                color: .orange
            ),
            PhaseDetail(
                title: "Shooting Hand",
                description: "Wrist snaps down through ball, creates backspin",
                icon: "arrow.clockwise",
                color: .blue
            ),
            PhaseDetail(
                title: "Guide Hand",
                description: "Releases first, falls away naturally, no sideways push",
                icon: "hand.wave.fill",
                color: .green
            ),
            PhaseDetail(
                title: "Elbow Extension",
                description: "Extends upward, follows through high, arm fully extended",
                icon: "arrow.up.right",
                color: .purple
            )
        ]
    }
    
    private var followThroughDetails: [PhaseDetail] {
        [
            PhaseDetail(
                title: "Ball Trajectory",
                description: "High arc at 45-50 degrees, consistent backspin",
                icon: "arrow.up.forward",
                color: .orange
            ),
            PhaseDetail(
                title: "Shooting Hand",
                description: "'Goose neck' finish, fingers pointing down, wrist fully flexed",
                icon: "arrow.down",
                color: .blue
            ),
            PhaseDetail(
                title: "Guide Hand",
                description: "Completely away from ball, natural position at side",
                icon: "hand.point.left.fill",
                color: .green
            ),
            PhaseDetail(
                title: "Body Position",
                description: "Balanced landing, same spot or slightly forward",
                icon: "figure.stand",
                color: .purple
            )
        ]
    }
}

struct PhaseDetail {
    let title: String
    let description: String
    let icon: String
    let color: Color
}

struct DetailCard: View {
    let title: String
    let description: String
    let icon: String
    let color: Color
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: icon)
                .foregroundColor(color)
                .font(.system(size: 18))
                .frame(width: 25)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.semibold)
                
                Text(description)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
            
            Spacer()
        }
        .padding()
        .background(color.opacity(0.1))
        .cornerRadius(8)
    }
}

struct ShootingFormGuideView_Previews: PreviewProvider {
    static var previews: some View {
        ShootingFormGuideView()
    }
}
