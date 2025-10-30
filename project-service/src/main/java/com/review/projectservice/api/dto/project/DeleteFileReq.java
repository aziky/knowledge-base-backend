package com.review.projectservice.api.dto.project;

import java.util.UUID;

public record DeleteFileReq(
        UUID id,
        String fileType
) {
}
