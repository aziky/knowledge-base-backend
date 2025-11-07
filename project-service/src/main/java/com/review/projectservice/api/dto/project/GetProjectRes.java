package com.review.projectservice.api.dto.project;

import java.util.UUID;

public record GetProjectRes (
        UUID projectId,
        String projectName,
        String projectRole,
        String joinedAt,
        String lockedAt,
        String removedAt
) {
}
