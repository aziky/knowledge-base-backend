package com.review.notificationservice.infrastructure.properties;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "host")
public record HostProperties(
        String backendHost,
        String handleVerificationUrl
) {
}
