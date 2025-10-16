package com.review.projectservice.shared;

import org.springframework.web.multipart.MultipartFile;

import java.util.List;

public class FileUtil {

    public static String classifyFile(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            return "folder";
        }

        String contentType = file.getContentType();
        String extension = getFileExtension(file.getOriginalFilename());

        if ((contentType == null || contentType.isBlank()) && extension.isEmpty()) {
            return "folder";
        }

        List<String> videoExtensions = List.of("mp4", "mov", "avi", "mkv", "webm");
        List<String> documentExtensions = List.of(
                "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt"
        );
        List<String> imageExtensions = List.of(
                "jpg", "jpeg", "png", "gif", "bmp", "svg", "webp"
        );

        extension = extension.toLowerCase();

        if ((contentType != null && contentType.startsWith("video"))
                || videoExtensions.contains(extension)) {
            return "video";
        }

        if (documentExtensions.contains(extension)
                || imageExtensions.contains(extension)
                || (contentType != null && (contentType.startsWith("application") || contentType.startsWith("image")))) {
            return "document";
        }

        return "document";
    }

    public static String getFileExtension(String filename) {
        if (filename == null || !filename.contains(".")) {
            return "";
        }
        return filename.substring(filename.lastIndexOf(".")).toLowerCase();
    }
}
