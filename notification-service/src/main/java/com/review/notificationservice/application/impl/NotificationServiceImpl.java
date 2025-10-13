package com.review.notificationservice.application.impl;

import com.review.common.dto.request.NotificationMessage;
import com.review.notificationservice.application.NotificationService;
import com.review.notificationservice.domain.entity.Template;
import com.review.notificationservice.domain.repository.TemplateRepository;
import com.review.notificationservice.infrastructure.properties.SESProperties;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import software.amazon.awssdk.services.ses.SesClient;
import org.apache.commons.text.StringSubstitutor;
import org.springframework.stereotype.Service;
import jakarta.persistence.EntityNotFoundException;
import software.amazon.awssdk.services.ses.model.*;

import java.util.HashMap;
import java.util.Map;

@Service
@Slf4j
@RequiredArgsConstructor
public class NotificationServiceImpl implements NotificationService {

    private final TemplateRepository templateRepository;
    private final SesClient sesClient;
    private final SESProperties sesProperties;


    @Override
    public void sendEmail(NotificationMessage notificationMessage) {
        try {
            log.info("Sending email notification to: {}", notificationMessage.to());

            Template template = templateRepository.findByTypeAndStatusIsTrue(notificationMessage.type());
            if (template == null) {
                throw new EntityNotFoundException("Template not found");
            }

            String subject = templateMapping(template.getSubject(), notificationMessage.payload());
            String body = templateMapping(template.getTemplate(), notificationMessage.payload());

            Map<String, String> mappedPayload = new HashMap<>();
            mappedPayload.put("subject", subject);
            mappedPayload.put("body", body);
            notificationMessage = notificationMessage.withPayload(mappedPayload);

            sendEmailViaSes(notificationMessage);

        } catch (Exception e) {
            log.error("Error sending email: {}", e.getMessage(), e);
        }
    }

    private String templateMapping(String source, Map<String, String> payload) {
        StringSubstitutor sbs = new StringSubstitutor(payload);
        return sbs.replace(source);
    }

    private void sendEmailViaSes(NotificationMessage message) {
        try {
            SendEmailRequest emailRequest = SendEmailRequest.builder()
                    .source(sesProperties.sender())
                    .destination(Destination.builder()
                            .toAddresses(message.to())
                            .build())
                    .message(Message.builder()
                            .subject(Content.builder().data(message.payload().get("subject")).build())
                            .body(Body.builder()
                                    .text(Content.builder().data(message.payload().get("body")).build())
                                    .build())
                            .build())
                    .build();

            SendEmailResponse response = sesClient.sendEmail(emailRequest);
            log.info("Email sent! Message ID: {}", response.messageId());
        } catch (SesException e) {
            log.error("Failed to send SES email: {}", e.awsErrorDetails().errorMessage());
        }
    }
}
