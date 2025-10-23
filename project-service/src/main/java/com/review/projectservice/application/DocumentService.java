package com.review.projectservice.application;

import com.review.common.dto.response.ApiResponse;
import com.review.projectservice.api.dto.document.DeleteDocumentReq;

import java.util.UUID;

public interface DocumentService {

    ApiResponse<?> deleteListDocument(DeleteDocumentReq request);

    ApiResponse<?> updateDocumentStatus(UUID document, String status);

}
