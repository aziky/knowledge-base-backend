package com.review.projectservice.application;

import org.springframework.web.multipart.MultipartFile;

import java.util.UUID;

public interface S3Service {

    String uploadFile(UUID projectId, MultipartFile file);
}
