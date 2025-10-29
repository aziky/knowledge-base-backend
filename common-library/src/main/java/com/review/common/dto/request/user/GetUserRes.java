package com.review.common.dto.request.user;

import lombok.Builder;

import java.util.UUID;

@Builder
public record GetUserRes(
        UUID id,
        String email,
        String fullName
) {
}
