package com.review.projectservice.application.impl;

import com.review.common.dto.response.ApiResponse;
import com.review.projectservice.api.dto.document.DeleteDocumentReq;
import com.review.projectservice.application.DocumentService;
import com.review.projectservice.domain.entity.Document;
import com.review.projectservice.domain.repository.DocumentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class DocumentServiceImpl implements DocumentService {

    private final DocumentRepository documentRepository;

    @Transactional
    public ApiResponse<?> deleteListDocument(DeleteDocumentReq request) {
        log.info("Start handle delete list document with {}", request);
        List<Document> documentList = documentRepository.findAllById(request.documentIds());
        for (Document document : documentList) {
            document.setIsActive(false);
        }

        documentRepository.saveAll(documentList);
        log.info("Delete document successfully");
        return ApiResponse.success("Delete document successfully");
    }


}
