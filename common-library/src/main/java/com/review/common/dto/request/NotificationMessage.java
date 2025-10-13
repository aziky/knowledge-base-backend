package com.review.common.dto.request;

import lombok.Builder;
import lombok.With;

import java.util.Map;

@With
@Builder
public record NotificationMessage(
        String to,
        String type,
        Map<String, String> payload
) {
}
