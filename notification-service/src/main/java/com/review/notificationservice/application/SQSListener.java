package com.review.notificationservice.application;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.review.common.dto.request.NotificationMessage;
import io.awspring.cloud.sqs.annotation.SqsListener;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

@Component
@Slf4j
@RequiredArgsConstructor
public class SQSListener {

    private final ObjectMapper objectMapper;
    private final NotificationService notificationService;


    @SqsListener("${spring.cloud.aws.sqs.email-queue}")
    public void listen(String message) {
        log.info("Star handle email queue with message: {}", message);
        NotificationMessage notificationMessage = null;
        try {
            notificationMessage = objectMapper.readValue(message, NotificationMessage.class);
            notificationService.sendEmail(notificationMessage);

        } catch (JsonProcessingException e) {
            log.info("Error when parse message from SQS cause by: {}", e.getMessage());
            throw new RuntimeException(e);
        }

    }


}
