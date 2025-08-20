import Foundation
import UIKit

class NetworkManager: ObservableObject {
    static let shared = NetworkManager()
    
    private let baseURL = "http://localhost:5001"
    private let session = URLSession.shared
    
    private init() {}
    
    func analyzeVideo(_ videoURL: URL, completion: @escaping (Result<AnalysisResult, Error>) -> Void) {
        let uploadURL = URL(string: "\(baseURL)/analyze")!
        
        var request = URLRequest(url: uploadURL)
        request.httpMethod = "POST"
        
        let boundary = "Boundary-\(UUID().uuidString)"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        let httpBody = createMultipartBody(videoURL: videoURL, boundary: boundary)
        
        let task = session.uploadTask(with: request, from: httpBody) { data, response, error in
            if let error = error {
                print("Network error: \(error)")
                completion(.failure(error))
                return
            }
            
            if let httpResponse = response as? HTTPURLResponse {
                print("HTTP Status Code: \(httpResponse.statusCode)")
            }
            
            guard let data = data else {
                print("No data received from server")
                completion(.failure(NetworkError.noData))
                return
            }
            
            print("Received \(data.count) bytes of data")
            
            do {
                let analysisResult = try JSONDecoder().decode(AnalysisResult.self, from: data)
                completion(.success(analysisResult))
            } catch {
                print("Decoding error: \(error)")
                completion(.failure(error))
            }
        }
        
        task.resume()
    }
    
    func getDemoAnalysis(completion: @escaping (Result<AnalysisResult, Error>) -> Void) {
        guard let url = URL(string: "\(baseURL)/analyze/demo") else {
            completion(.failure(NetworkError.invalidURL))
            return
        }
        
        let task = session.dataTask(with: url) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(NetworkError.noData))
                return
            }
            
            do {
                let analysisResult = try JSONDecoder().decode(AnalysisResult.self, from: data)
                completion(.success(analysisResult))
            } catch {
                print("Decoding error: \(error)")
                completion(.failure(error))
            }
        }
        
        task.resume()
    }
    
    private func createMultipartBody(videoURL: URL, boundary: String) -> Data {
        var body = Data()
        
        // Add video file
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(videoURL.lastPathComponent)\"\r\n".data(using: .utf8)!)
        
        let mimeType = getMimeType(for: videoURL)
        body.append("Content-Type: \(mimeType)\r\n\r\n".data(using: .utf8)!)
        
        do {
            let videoData = try Data(contentsOf: videoURL)
            body.append(videoData)
        } catch {
            print("Error reading video data: \(error)")
        }
        
        body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)
        
        return body
    }
    
    private func getMimeType(for url: URL) -> String {
        let pathExtension = url.pathExtension.lowercased()
        
        switch pathExtension {
        case "mp4":
            return "video/mp4"
        case "mov":
            return "video/quicktime"
        case "avi":
            return "video/x-msvideo"
        case "mkv":
            return "video/x-matroska"
        case "jpg", "jpeg":
            return "image/jpeg"
        case "png":
            return "image/png"
        default:
            return "application/octet-stream"
        }
    }
}

enum NetworkError: Error {
    case invalidURL
    case noData
    case decodingError
    
    var localizedDescription: String {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .noData:
            return "No data received"
        case .decodingError:
            return "Failed to decode response"
        }
    }
}
