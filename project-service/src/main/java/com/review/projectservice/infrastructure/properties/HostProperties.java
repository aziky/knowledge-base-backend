package com.review.projectservice.infrastructure.properties;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "host")
public record HostProperties(
        String frontendHost,
        String backendHost,
        String verifiedInvitation
) {
}
