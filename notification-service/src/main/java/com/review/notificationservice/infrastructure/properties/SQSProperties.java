package com.review.notificationservice.infrastructure.properties;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "spring.cloud.aws.sqs")
public record SQSProperties(
        String region,
        String emailQueue
) {
}
