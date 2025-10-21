package com.review.projectservice.api.dto.project;

import java.time.LocalDateTime;
import java.util.UUID;

public record DocumentRes(
        UUID documentId,
        String name,
        String filePath,
        String fileType,
        UUID projectId,
        LocalDateTime uploadedAt
) {}
