package com.review.projectservice.api.controller;

import com.review.projectservice.api.dto.document.DeleteDocumentReq;
import com.review.projectservice.application.DocumentService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/document")
@RequiredArgsConstructor
public class DocumentController {

    private final DocumentService documentService;


    @DeleteMapping()
    public ResponseEntity<?> deleteListDocument(@RequestBody DeleteDocumentReq request) {
        return ResponseEntity.ok(documentService.deleteListDocument(request));
    }



}
