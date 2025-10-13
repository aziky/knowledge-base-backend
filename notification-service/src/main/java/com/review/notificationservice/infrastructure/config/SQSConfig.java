package com.review.notificationservice.infrastructure.config;

import com.review.notificationservice.infrastructure.properties.AWSProperties;
import com.review.notificationservice.infrastructure.properties.SQSProperties;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.sqs.SqsClient;

@Configuration
@RequiredArgsConstructor
public class SQSConfig {

    private final SQSProperties sqsProperties;
    private final AWSProperties awsProperties;

    @Bean
    public SqsClient sqsClient() {
        return SqsClient.builder()
                .region(Region.of(sqsProperties.region()))
                .credentialsProvider(StaticCredentialsProvider.create(
                        AwsBasicCredentials.create(awsProperties.accessKey(), awsProperties.secretKey())
                ))
                .build();
    }

}
