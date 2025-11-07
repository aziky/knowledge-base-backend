package com.review.projectservice.api.dto.project;

import java.util.List;
import java.util.UUID;

public record DeleteMemberReq(
        List<UUID> memberIds
) {
}
