package com.review.projectservice.application;

import com.review.common.dto.response.ApiResponse;
import com.review.projectservice.api.dto.project.CreateInvitationReq;
import com.review.projectservice.api.dto.project.CreateProjectReq;
import org.springframework.data.domain.Pageable;

import java.util.UUID;

public interface ProjectService {

    ApiResponse<?> createProject(CreateProjectReq request);

    ApiResponse<?> getAllProject(Pageable pageable);

    ApiResponse<Void> sendInvitation(UUID projectId, CreateInvitationReq request);

    ApiResponse<Void> removeUserFromProject(UUID projectId, UUID userId);

    String verifiedInvitationToken(String token);

}
