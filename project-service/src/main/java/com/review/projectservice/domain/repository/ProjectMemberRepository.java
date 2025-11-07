package com.review.projectservice.domain.repository;

import com.review.projectservice.domain.entity.ProjectMember;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface ProjectMemberRepository extends JpaRepository<ProjectMember, UUID> {

    Page<ProjectMember> findAllByUserId(Pageable pageable, UUID userId);

    List<ProjectMember> findByProjectIdAndUserIdIn(UUID projectId, List<UUID> userIds);

    List<ProjectMember> findAllByProjectId(UUID projectId);

}
