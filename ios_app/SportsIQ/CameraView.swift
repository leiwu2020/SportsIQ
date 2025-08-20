import SwiftUI
import AVFoundation
import UIKit

struct CameraView: UIViewControllerRepresentable {
    let onVideoRecorded: (URL) -> Void
    @Environment(\.presentationMode) var presentationMode
    
    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        
        // Check if camera is available (not available in simulator)
        if UIImagePickerController.isSourceTypeAvailable(.camera) {
            picker.sourceType = .camera
            picker.mediaTypes = ["public.movie"]
            picker.videoQuality = .typeHigh
            picker.videoMaximumDuration = 30 // 30 seconds max
        } else {
            // Fallback to photo library for simulator
            picker.sourceType = .photoLibrary
            picker.mediaTypes = ["public.movie", "public.image"]
        }
        
        return picker
    }
    
    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: CameraView
        
        init(_ parent: CameraView) {
            self.parent = parent
        }
        
        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
            if let videoURL = info[.mediaURL] as? URL {
                parent.onVideoRecorded(videoURL)
            }
            parent.presentationMode.wrappedValue.dismiss()
        }
        
        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            parent.presentationMode.wrappedValue.dismiss()
        }
    }
}

struct DocumentPicker: UIViewControllerRepresentable {
    let onVideoSelected: (URL) -> Void
    
    func makeUIViewController(context: Context) -> UIDocumentPickerViewController {
        let picker = UIDocumentPickerViewController(forOpeningContentTypes: [.movie, .video])
        picker.delegate = context.coordinator
        picker.allowsMultipleSelection = false
        return picker
    }
    
    func updateUIViewController(_ uiViewController: UIDocumentPickerViewController, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    class Coordinator: NSObject, UIDocumentPickerDelegate {
        let parent: DocumentPicker
        
        init(_ parent: DocumentPicker) {
            self.parent = parent
        }
        
        func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentsAt urls: [URL]) {
            guard let url = urls.first else { return }
            print("DocumentPicker: Selected file: \(url)")
            parent.onVideoSelected(url)
        }
        
        func documentPickerWasCancelled(_ controller: UIDocumentPickerViewController) {
            print("DocumentPicker: Cancelled")
        }
    }
}

struct PhotoPicker: UIViewControllerRepresentable {
    let onVideoSelected: (URL) -> Void
    @Environment(\.presentationMode) var presentationMode
    
    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        picker.sourceType = .photoLibrary
        picker.mediaTypes = ["public.movie", "public.image"]
        return picker
    }
    
    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: PhotoPicker
        
        init(_ parent: PhotoPicker) {
            self.parent = parent
        }
        
        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
            if let mediaType = info[.mediaType] as? String {
                if mediaType == "public.movie" {
                    // Handle video selection
                    if let videoURL = info[.mediaURL] as? URL {
                        print("PhotoPicker: Video selected with URL: \(videoURL)")
                        parent.onVideoSelected(videoURL)
                    }
                } else if mediaType == "public.image" {
                    // Handle image selection
                    if let image = info[.originalImage] as? UIImage,
                       let imageURL = saveImageToTempFile(image) {
                        parent.onVideoSelected(imageURL)
                    }
                }
            }
            
            parent.presentationMode.wrappedValue.dismiss()
        }
        
        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            parent.presentationMode.wrappedValue.dismiss()
        }
        
        private func saveImageToTempFile(_ image: UIImage) -> URL? {
            guard let data = image.jpegData(compressionQuality: 0.8) else { return nil }
            
            let tempDir = FileManager.default.temporaryDirectory
            let fileName = "temp_image_\(UUID().uuidString).jpg"
            let fileURL = tempDir.appendingPathComponent(fileName)
            
            do {
                try data.write(to: fileURL)
                print("PhotoPicker: Created temporary image file: \(fileName)")
                return fileURL
            } catch {
                print("Error saving image: \(error)")
                return nil
            }
        }
        
        // Cleanup temporary files when picker is dismissed
        func cleanup() {
            let tempDir = FileManager.default.temporaryDirectory
            do {
                let tempFiles = try FileManager.default.contentsOfDirectory(at: tempDir, includingPropertiesForKeys: nil)
                
                for fileURL in tempFiles {
                    if fileURL.lastPathComponent.hasPrefix("temp_image_") {
                        try FileManager.default.removeItem(at: fileURL)
                        print("PhotoPicker: Cleaned up temporary file: \(fileURL.lastPathComponent)")
                    }
                }
            } catch {
                print("PhotoPicker: Error cleaning up temporary files: \(error)")
            }
        }
        

    }
}
