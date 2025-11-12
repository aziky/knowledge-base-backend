package com.review.projectservice.api.dto.project;

import lombok.Builder;

import java.util.UUID;

@Builder
public record GetProjectRes (
        UUID projectId,
        String projectName,
        String projectRole,
        String joinedAt,
        String lockedAt,
        String removedAt
) {
}
