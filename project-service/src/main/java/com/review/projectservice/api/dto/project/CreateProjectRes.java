package com.review.projectservice.api.dto.project;

import java.util.UUID;

public record CreateProjectRes(UUID projectId, String name, String message) {}
