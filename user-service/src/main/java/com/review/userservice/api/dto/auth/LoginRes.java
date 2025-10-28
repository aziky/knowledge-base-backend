package com.review.userservice.api.dto.auth;

public record LoginRes(
        String token,
        String role,
        String fullName,
        String email
) {
}
