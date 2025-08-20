import Foundation
import UIKit
import AVFoundation
import Photos

class NetworkManager: ObservableObject {
    static let shared = NetworkManager()
    
    private var baseURL: String {
        let ip = UserDefaults.standard.string(forKey: "backend_ip") ?? "localhost"
        let port = UserDefaults.standard.string(forKey: "backend_port") ?? "5001"
        return "http://\(ip):\(port)"
    }
    private let session = URLSession.shared
    
    private init() {}
    
    func updateBaseURL(ip: String, port: String) {
        // This method is called when settings are saved
        // The baseURL computed property will automatically use the new values
        print("NetworkManager: Updated backend URL to http://\(ip):\(port)")
    }
    
    func getCurrentBaseURL() -> String {
        return baseURL
    }
    
    func analyzeVideo(_ videoURL: URL, completion: @escaping (Result<AnalysisResult, Error>) -> Void) {
        print("NetworkManager: Starting video analysis")
        print("NetworkManager: Video URL: \(videoURL)")
        print("NetworkManager: Video path: \(videoURL.path)")
        print("NetworkManager: Video exists: \(FileManager.default.fileExists(atPath: videoURL.path))")
        
        let uploadURL = URL(string: "\(baseURL)/analyze")!
        print("NetworkManager: Upload URL: \(uploadURL)")
        
        var request = URLRequest(url: uploadURL)
        request.httpMethod = "POST"
        
        let boundary = "Boundary-\(UUID().uuidString)"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        let httpBody = createMultipartBody(videoURL: videoURL, boundary: boundary)
        
        let task = session.uploadTask(with: request, from: httpBody) { data, response, error in
            if let error = error {
                print("Network error: \(error)")
                print("Error details: \(error.localizedDescription)")
                completion(.failure(error))
                return
            }
            
            guard let httpResponse = response as? HTTPURLResponse else {
                print("Invalid response type")
                let errorMessage = "Invalid response from server"
                completion(.failure(NSError(domain: "NetworkError", code: -1, userInfo: [NSLocalizedDescriptionKey: errorMessage])))
                return
            }
            
            print("HTTP Status Code: \(httpResponse.statusCode)")
            
            guard httpResponse.statusCode == 200 else {
                print("HTTP Error: Status code \(httpResponse.statusCode)")
                let errorMessage = "Server returned status code \(httpResponse.statusCode)"
                completion(.failure(NSError(domain: "HTTPError", code: httpResponse.statusCode, userInfo: [NSLocalizedDescriptionKey: errorMessage])))
                return
            }
            
            guard let data = data else {
                print("No data received from server")
                let errorMessage = "No data received from server"
                completion(.failure(NSError(domain: "NetworkError", code: -1, userInfo: [NSLocalizedDescriptionKey: errorMessage])))
                return
            }
            
            print("Received \(data.count) bytes of data")
            
            // Check if response is empty or too small
            if data.count < 10 {
                print("Response data is too small: \(data.count) bytes")
                let errorMessage = "Server response is too small (\(data.count) bytes)"
                completion(.failure(NSError(domain: "DataError", code: -1, userInfo: [NSLocalizedDescriptionKey: errorMessage])))
                return
            }
            
            // Log first part of JSON response for debugging
            if let jsonString = String(data: data, encoding: .utf8) {
                print("Raw JSON response preview: \(jsonString.prefix(500))...")
                print("Full JSON response: \(jsonString)")
            } else {
                print("Could not convert response data to string")
            }
            
            do {
                let analysisResult = try JSONDecoder().decode(AnalysisResult.self, from: data)
                print("Successfully decoded analysis result")
                completion(.success(analysisResult))
            } catch let decodingError {
                print("JSON decoding error: \(decodingError)")
                
                // Provide more specific error messages
                if let decodingError = decodingError as? DecodingError {
                    switch decodingError {
                    case .dataCorrupted(let context):
                        print("Data corrupted: \(context.debugDescription)")
                    case .keyNotFound(let key, let context):
                        print("Key '\(key.stringValue)' not found: \(context.debugDescription)")
                    case .typeMismatch(let type, let context):
                        print("Type mismatch for \(type): \(context.debugDescription)")
                    case .valueNotFound(let type, let context):
                        print("Value not found for \(type): \(context.debugDescription)")
                    @unknown default:
                        print("Unknown decoding error")
                    }
                }
                
                let errorMessage = "The data couldn't be read because it is missing or corrupted"
                completion(.failure(NSError(domain: "DecodingError", code: -1, userInfo: [NSLocalizedDescriptionKey: errorMessage])))
            }
        }
        
        task.resume()
    }
    
    func getDemoAnalysis(completion: @escaping (Result<AnalysisResult, Error>) -> Void) {
        guard let url = URL(string: "\(baseURL)/analyze/demo") else {
            let errorMessage = "Invalid demo analysis URL"
            completion(.failure(NSError(domain: "URLError", code: -1, userInfo: [NSLocalizedDescriptionKey: errorMessage])))
            return
        }
        
        let task = session.dataTask(with: url) { data, response, error in
            if let error = error {
                print("Demo analysis network error: \(error)")
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                print("No data received from demo analysis")
                let errorMessage = "No data received from demo analysis"
                completion(.failure(NSError(domain: "NetworkError", code: -1, userInfo: [NSLocalizedDescriptionKey: errorMessage])))
                return
            }
            
            print("Demo analysis received \(data.count) bytes of data")
            
            do {
                let analysisResult = try JSONDecoder().decode(AnalysisResult.self, from: data)
                print("Successfully decoded demo analysis result")
                completion(.success(analysisResult))
            } catch {
                print("Demo analysis decoding error: \(error)")
                let errorMessage = "Failed to parse demo analysis response"
                completion(.failure(NSError(domain: "DecodingError", code: -1, userInfo: [NSLocalizedDescriptionKey: errorMessage])))
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
            let videoData: Data
            
            // Handle Photos library URLs (ph:// scheme)
            if videoURL.scheme == "ph" {
                print("NetworkManager: Photos library URL detected, using AVAsset to read video data")
                videoData = try readVideoDataFromPhotosLibrary(url: videoURL)
            } else {
                // Regular file URL
                print("NetworkManager: Regular file URL, reading directly")
                videoData = try Data(contentsOf: videoURL)
            }
            
            body.append(videoData)
            print("NetworkManager: Successfully read video data: \(videoData.count) bytes")
        } catch {
            print("Error reading video data: \(error)")
            // Return empty body on error
            body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)
            return body
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
    
    private func readVideoDataFromPhotosLibrary(url: URL) throws -> Data {
        print("NetworkManager: Photos library URL detected: \(url)")
        print("NetworkManager: Attempting to read video data directly...")
        
        // Try to read the video data directly first
        do {
            let videoData = try Data(contentsOf: url)
            print("NetworkManager: Successfully read video data directly: \(videoData.count) bytes")
            return videoData
        } catch {
            print("NetworkManager: Direct read failed: \(error.localizedDescription)")
            
            // If direct read fails, provide a helpful error message
            throw NSError(
                domain: "PhotosLibraryError", 
                code: -1, 
                userInfo: [
                    NSLocalizedDescriptionKey: "Cannot read video from Photos library. Please try recording a new video or select a video from Files app instead."
                ]
            )
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
