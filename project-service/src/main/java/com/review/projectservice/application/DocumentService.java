package com.review.projectservice.application;

import com.review.common.dto.response.ApiResponse;
import com.review.projectservice.api.dto.document.DeleteDocumentReq;

public interface DocumentService {

    ApiResponse<?> deleteListDocument(DeleteDocumentReq request);

}
