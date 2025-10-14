package com.review.projectservice.infrastructure.properties;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "spring.cloud.aws.credentials")
public record AWSProperties(
        String accessKey,
        String secretKey
) {
}
