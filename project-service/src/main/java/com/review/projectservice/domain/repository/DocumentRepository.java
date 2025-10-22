package com.review.projectservice.domain.repository;

import com.review.projectservice.domain.entity.Document;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface DocumentRepository extends JpaRepository<Document, UUID> {
    List<Document> findAllByProjectIdAndIsActiveTrue(UUID projectId);

    Optional<Document> findByFilePathAndIsActiveTrue(String filePath);

}
