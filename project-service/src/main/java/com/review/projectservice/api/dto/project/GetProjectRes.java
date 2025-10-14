package com.review.projectservice.api.dto.project;

import java.util.UUID;

public record GetProjectRes (
        UUID id,
        String projectName,
        String projectRole,
        String joinedAt,
        String removedAt
) {
}
