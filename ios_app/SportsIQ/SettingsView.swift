import SwiftUI

struct SettingsView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var backendIP = UserDefaults.standard.string(forKey: "backend_ip") ?? "localhost"
    @State private var backendPort = UserDefaults.standard.string(forKey: "backend_port") ?? "5001"
    @State private var isTestingConnection = false
    @State private var connectionStatus: ConnectionStatus = .unknown
    @State private var showingAlert = false
    @State private var alertMessage = ""
    
    enum ConnectionStatus {
        case unknown
        case success
        case failed
    }
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Backend Configuration")) {
                    HStack {
                        Text("IP Address")
                        Spacer()
                        TextField("localhost", text: $backendIP)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .autocapitalization(.none)
                            .disableAutocorrection(true)
                            .frame(width: 150)
                    }
                    
                    HStack {
                        Text("Port")
                        Spacer()
                        TextField("5001", text: $backendPort)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .keyboardType(.numberPad)
                            .frame(width: 100)
                    }
                    
                    HStack {
                        Text("Full URL")
                        Spacer()
                        Text("http://\(backendIP):\(backendPort)")
                            .foregroundColor(.secondary)
                            .font(.caption)
                    }
                }
                
                Section(header: Text("Connection Test")) {
                    Button(action: testConnection) {
                        HStack {
                            if isTestingConnection {
                                ProgressView()
                                    .scaleEffect(0.8)
                                Text("Testing...")
                            } else {
                                Image(systemName: connectionStatusIcon)
                                    .foregroundColor(connectionStatusColor)
                                Text("Test Connection")
                            }
                        }
                    }
                    .disabled(isTestingConnection)
                    
                    if connectionStatus != .unknown {
                        HStack {
                            Image(systemName: connectionStatusIcon)
                                .foregroundColor(connectionStatusColor)
                            Text(connectionStatusText)
                                .foregroundColor(connectionStatusColor)
                        }
                    }
                }
                
                Section(header: Text("Presets")) {
                    Button("Local Development") {
                        backendIP = "localhost"
                        backendPort = "5001"
                    }
                    
                    Button("Local Network (Auto-detect)") {
                        // Get the current device's IP and use it as base
                        backendIP = getLocalNetworkIP() ?? "192.168.1.100"
                        backendPort = "5001"
                    }
                    
                    Button("Remote Server") {
                        backendIP = "your-server.com"
                        backendPort = "5001"
                    }
                }
                
                Section(footer: Text("Changes will take effect immediately. Make sure your backend server is running at the specified address.")) {
                    EmptyView()
                }
            }
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Save") {
                        saveSettings()
                        dismiss()
                    }
                }
            }
        }
        .alert("Connection Test", isPresented: $showingAlert) {
            Button("OK") { }
        } message: {
            Text(alertMessage)
        }
    }
    
    private var connectionStatusIcon: String {
        switch connectionStatus {
        case .unknown:
            return "questionmark.circle"
        case .success:
            return "checkmark.circle"
        case .failed:
            return "xmark.circle"
        }
    }
    
    private var connectionStatusColor: Color {
        switch connectionStatus {
        case .unknown:
            return .secondary
        case .success:
            return .green
        case .failed:
            return .red
        }
    }
    
    private var connectionStatusText: String {
        switch connectionStatus {
        case .unknown:
            return "Not tested"
        case .success:
            return "Connection successful"
        case .failed:
            return "Connection failed"
        }
    }
    
    private func saveSettings() {
        UserDefaults.standard.set(backendIP, forKey: "backend_ip")
        UserDefaults.standard.set(backendPort, forKey: "backend_port")
        
        // Update NetworkManager's base URL
        NetworkManager.shared.updateBaseURL(ip: backendIP, port: backendPort)
        
        print("Settings saved - Backend: http://\(backendIP):\(backendPort)")
    }
    
    private func testConnection() {
        isTestingConnection = true
        connectionStatus = .unknown
        
        // Test the health endpoint
        let testURL = "http://\(backendIP):\(backendPort)/health"
        
        guard let url = URL(string: testURL) else {
            connectionStatus = .failed
            alertMessage = "Invalid URL format"
            showingAlert = true
            isTestingConnection = false
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.timeoutInterval = 10.0
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                isTestingConnection = false
                
                if let error = error {
                    connectionStatus = .failed
                    alertMessage = "Connection failed: \(error.localizedDescription)"
                    showingAlert = true
                    return
                }
                
                guard let httpResponse = response as? HTTPURLResponse else {
                    connectionStatus = .failed
                    alertMessage = "Invalid response from server"
                    showingAlert = true
                    return
                }
                
                if httpResponse.statusCode == 200 {
                    connectionStatus = .success
                    alertMessage = "Successfully connected to backend server!"
                    showingAlert = true
                } else {
                    connectionStatus = .failed
                    alertMessage = "Server responded with status code: \(httpResponse.statusCode)"
                    showingAlert = true
                }
            }
        }.resume()
    }
    
    private func getLocalNetworkIP() -> String? {
        // Simple heuristic to suggest a local network IP
        // This is a basic implementation - in a real app you might want more sophisticated detection
        return "192.168.1.100" // Common local network range
    }
}

struct SettingsView_Previews: PreviewProvider {
    static var previews: some View {
        SettingsView()
    }
}
