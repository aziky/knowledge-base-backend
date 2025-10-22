package com.review.projectservice.api.controller;

import com.review.projectservice.api.dto.document.DeleteDocumentReq;
import com.review.projectservice.application.DocumentService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/document")
@RequiredArgsConstructor
public class DocumentController {

    private final DocumentService documentService;


    @DeleteMapping()
    public ResponseEntity<?> deleteListDocument(@RequestBody DeleteDocumentReq request) {
        return ResponseEntity.ok(documentService.deleteListDocument(request));
    }


    @PatchMapping("/{documentId}/status")
    public ResponseEntity<?> updateDocumentStatus(@PathVariable("documentId") UUID documentId, @RequestParam("status") String status) {
        return ResponseEntity.ok(documentService.updateDocumentStatus(documentId, status));
    }


}
