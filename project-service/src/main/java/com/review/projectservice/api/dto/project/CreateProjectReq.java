package com.review.projectservice.api.dto.project;

import jakarta.validation.constraints.NotBlank;

public record CreateProjectReq(
        @NotBlank
        String name,
        String description
) {
}
