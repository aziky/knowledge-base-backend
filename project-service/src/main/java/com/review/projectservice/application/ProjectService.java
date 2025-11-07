package com.review.projectservice.application;

import com.review.common.dto.response.ApiResponse;
import com.review.projectservice.api.dto.project.*;
import jakarta.ws.rs.DELETE;
import org.springframework.data.domain.Pageable;
import org.springframework.web.multipart.MultipartFile;

import java.util.UUID;
import java.util.List;

public interface ProjectService {

    ApiResponse<?> createProject(CreateProjectReq request);

    ApiResponse<?> getAllProject(Pageable pageable);

    ApiResponse<Void> sendInvitation(UUID projectId, List<CreateInvitationReq> requests);

    ApiResponse<Void> removeUserFromProject(UUID projectId, UUID userId);

    String verifiedInvitationToken(String token);

    ApiResponse<?> getProjectDetails(UUID projectId);

    ApiResponse<?> uploadFile(UUID projectId, MultipartFile[] files);

    ApiResponse<?> searchEntityByPath(String path, String type);

    ApiResponse<?> deleteListFile(UUID projectId, List<DeleteFileReq> listFileReq);

    ApiResponse<?> downloadFile(UUID fileId, String type);

    ApiResponse<?> deleteProject(UUID projectId);

    ApiResponse<?> activeProject(UUID projectId);

}
