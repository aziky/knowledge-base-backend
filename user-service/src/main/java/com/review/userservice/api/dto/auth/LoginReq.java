package com.review.userservice.api.dto.auth;

public record LoginReq(
        String email,
        String password
) {
}
