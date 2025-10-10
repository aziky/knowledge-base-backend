package com.review.userservice.api.dto.auth;

import java.util.UUID;

public record RegisterRes(
    UUID id,
    String email,
    String fullName,
    String role
) {}
