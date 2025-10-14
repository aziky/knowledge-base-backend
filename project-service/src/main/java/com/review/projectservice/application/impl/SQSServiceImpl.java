package com.review.projectservice.application.impl;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.review.common.dto.request.NotificationMessage;
import com.review.projectservice.application.SQSService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.services.sqs.SqsClient;
import software.amazon.awssdk.services.sqs.model.SendMessageRequest;
import software.amazon.awssdk.services.sqs.model.SendMessageResponse;

@Service
@RequiredArgsConstructor
@Slf4j
public class SQSServiceImpl implements SQSService {

    private final SqsClient sqsClient;
    private final ObjectMapper objectMapper;


    @Override
    public void sendMessage(String queueName, NotificationMessage message) {
        try {
            SendMessageRequest request = SendMessageRequest.builder()
                    .queueUrl(queueName)
                    .messageBody(objectMapper.writeValueAsString(message))
                    .build();

            SendMessageResponse response = sqsClient.sendMessage(request);
            log.info("Sent message to SQS. messageId={}, md5={}, queueUrl={}",
                    response.messageId(), response.md5OfMessageBody(), queueName);
        } catch (Exception e) {
            log.info("Failed to send message to SQS cause by {}", e.getMessage());
        }
    }
}
