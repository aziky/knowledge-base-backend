package com.review.projectservice.application.impl;


import com.review.projectservice.application.S3Service;
import com.review.projectservice.infrastructure.properties.S3Properties;
import com.review.projectservice.shared.FileUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;
import software.amazon.awssdk.services.s3.model.PutObjectResponse;
import software.amazon.awssdk.services.s3.presigner.S3Presigner;
import software.amazon.awssdk.services.s3.presigner.model.GetObjectPresignRequest;
import software.amazon.awssdk.services.s3.presigner.model.PresignedGetObjectRequest;

import java.io.IOException;
import java.time.Duration;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class S3ServiceImpl implements S3Service {

    private final S3Client s3Client;
    private final S3Properties s3Properties;
    private final S3Presigner s3Presigner;


    public String uploadFile(UUID projectId, MultipartFile file) {
        String originalFilename = file.getOriginalFilename();
        log.info("Start handle upload file: {}", originalFilename);
        if (originalFilename == null || originalFilename.isBlank()) {
            throw new IllegalArgumentException("File name cannot be empty");
        }

        String fileCategory = FileUtil.classifyFile(file);
        String key = String.format("%s/%s/%s", fileCategory, projectId, originalFilename);

        PutObjectResponse response = null;
        try {
            response = s3Client.putObject(
                    PutObjectRequest.builder()
                            .bucket(s3Properties.bucketName())
                            .key(key)
                            .contentType(file.getContentType())
                            .build(),
                    RequestBody.fromBytes(file.getBytes())
            );
        } catch (IOException e) {
            log.info("Failed to upload file to S3 cause by {}", e.getMessage());
            throw new RuntimeException(e);
        }

        log.info("File uploaded successfully to s3://{}/{} (ETag: {})",
                s3Properties.bucketName(), key, response.eTag());

        return key;
    }


    public String getPresignedUrl(String filePath) {
        log.info("Generating presigned URL for file: {}", filePath);
        GetObjectRequest getObjectRequest = GetObjectRequest.builder()
                .bucket(s3Properties.bucketName())
                .key(filePath)
                .build();

        GetObjectPresignRequest presignRequest = GetObjectPresignRequest.builder()
                .signatureDuration(Duration.ofMinutes(60))
                .getObjectRequest(getObjectRequest)
                .build();

        PresignedGetObjectRequest presignedRequest = s3Presigner.presignGetObject(presignRequest);

        return presignedRequest.url().toString();
    }

}
