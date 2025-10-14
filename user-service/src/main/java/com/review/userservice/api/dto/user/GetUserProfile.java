package com.review.userservice.api.dto.user;

import java.util.UUID;

public record GetUserProfile(
        UUID id,
        String email,
        String fullName
) {
}
