package com.review.userservice.application;

import com.review.common.dto.request.NotificationMessage;

public interface SQSService {

    void sendMessage(String queueName, NotificationMessage message);

}
