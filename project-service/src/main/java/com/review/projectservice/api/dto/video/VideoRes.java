package com.review.projectservice.api.dto.video;

import java.time.LocalDateTime;
import java.util.UUID;

public record VideoRes(
        UUID videoId,
        String name,
        String filePath,
        String fileType,
        UUID projectId,
        LocalDateTime uploadedAt
) {
}
