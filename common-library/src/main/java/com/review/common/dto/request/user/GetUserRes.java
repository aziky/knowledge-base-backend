package com.review.common.dto.request.user;

import lombok.Builder;

@Builder
public record GetUserRes(
        String email,
        String fullName
) {
}
