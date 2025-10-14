package com.review.projectservice.api.dto.project;

import jakarta.validation.constraints.NotBlank;

public record CreateProjectRes(
        @NotBlank
        String name,
        String description
) {
}
