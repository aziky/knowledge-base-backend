package com.review.projectservice.domain.repository;

import com.review.projectservice.domain.entity.Video;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.UUID;

public interface VideoRepository extends JpaRepository<Video, UUID> {
    List<Video> findAllByProjectId(UUID projectId);
}
