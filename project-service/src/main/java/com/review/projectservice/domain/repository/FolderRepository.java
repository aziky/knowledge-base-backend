package com.review.projectservice.domain.repository;

import com.review.projectservice.domain.entity.Folder;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.UUID;

public interface FolderRepository extends JpaRepository<Folder, UUID> {
    List<Folder> findAllByProjectId(UUID projectId);
}
