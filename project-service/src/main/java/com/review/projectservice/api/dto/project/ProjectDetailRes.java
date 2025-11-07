package com.review.projectservice.api.dto.project;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Builder;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Builder
public record ProjectDetailRes(
        UUID projectId,
        String projectName,
        String description,
        LocalDateTime createdAt,
        String lockedBy,
        LocalDateTime lockedAt,
        String lockedReason,
        String status,
        String userRole,
        List<MemberInfo> members,
        List<FolderInfo> folders,
        List<DocumentInfo> documents,
        List<VideoInfo> videos
) {
    public record FolderInfo(UUID id, String folderName, LocalDateTime createdAt) {}
    public record DocumentInfo(UUID id, String fileName, String fileType, LocalDateTime uploadedAt, String uploadedBy, String status) {}
    public record VideoInfo(UUID id, String fileName, String fileType, LocalDateTime uploadedAt, String uploadedBy, String status) {}
    public record MemberInfo(UUID id, String email, String fullName, String role, LocalDateTime joinedAt, LocalDateTime removedAt) {}
}
