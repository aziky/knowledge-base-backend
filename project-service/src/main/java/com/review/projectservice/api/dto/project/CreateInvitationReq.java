package com.review.projectservice.api.dto.project;

import java.util.UUID;

public record CreateInvitationReq (
        UUID userId,
        String fullName,
        String email
) {
}
