package com.review.projectservice.api.dto.video;

import java.util.List;
import java.util.UUID;

public record DeleteVideoReq(
    List<UUID> videoIds
) {}
