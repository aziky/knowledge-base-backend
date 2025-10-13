package com.review.notificationservice.application;

import com.review.common.dto.request.NotificationMessage;

public interface NotificationService {

    void sendEmail(NotificationMessage notificationMessage);
}
