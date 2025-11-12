package com.review.notificationservice.infrastructure.config;

import com.review.notificationservice.infrastructure.properties.AWSProperties;
import com.review.notificationservice.infrastructure.properties.SESProperties;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.ses.SesClient;

import java.net.URI;

@Configuration
@RequiredArgsConstructor
public class SESConfig {

    private final SESProperties sesProperties;
    private final AWSProperties awsProperties;

    @Bean
    public SesClient sesClient() {
        return SesClient.builder()
                .region(Region.of(sesProperties.region()))
                .credentialsProvider(StaticCredentialsProvider.create(
                        AwsBasicCredentials.create(awsProperties.accessKey(), awsProperties.secretKey())
                ))
                .build();
    }

}
