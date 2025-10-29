package com.review.projectservice.application.impl;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.review.common.dto.request.NotificationMessage;
import com.review.common.dto.request.user.GetUserRes;
import com.review.common.dto.response.ApiResponse;
import com.review.common.enumration.ProjectRole;
import com.review.common.enumration.ProjectStatus;
import com.review.common.enumration.Template;
import com.review.common.shared.CustomUserDetails;
import com.review.projectservice.api.dto.document.DocumentRes;
import com.review.projectservice.api.dto.project.*;
import com.review.projectservice.api.dto.video.VideoRes;
import com.review.projectservice.application.ProjectService;
import com.review.projectservice.application.RedisService;
import com.review.projectservice.application.SQSService;
import com.review.projectservice.domain.entity.Document;
import com.review.projectservice.domain.entity.Project;
import com.review.projectservice.domain.entity.ProjectMember;
import com.review.projectservice.domain.entity.Video;
import com.review.projectservice.domain.enumration.HandleStaus;
import com.review.projectservice.domain.repository.*;
import com.review.projectservice.infrastructure.external.UserClient;
import com.review.projectservice.infrastructure.properties.HostProperties;
import com.review.projectservice.infrastructure.properties.SQSProperties;
import com.review.projectservice.shared.FileUtil;
import com.review.projectservice.shared.PageResponse;
import com.review.projectservice.shared.SecurityUtil;
import com.review.projectservice.shared.mapper.ProjectMapper;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.time.Duration;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
@Slf4j
@RequiredArgsConstructor
public class ProjectServiceImpl implements ProjectService {

    private final ProjectRepository projectRepository;
    private final ProjectMemberRepository projectMemberRepository;
    private final ProjectMapper projectMapper;
    private final HostProperties hostProperties;
    private final SQSService sqsService;
    private final SQSProperties sqsProperties;
    private final RedisService redisService;
    private final DocumentRepository documentRepository;
    private final FolderRepository folderRepository;
    private final VideoRepository videoRepository;
    private final S3ServiceImpl s3Service;
    private final UserClient userClient; // injected user-service client
    private final ObjectMapper objectMapper;

    @Override
    @Transactional
    public ApiResponse<?> createProject(CreateProjectReq request) {
        log.info("Handle create project request: {}", request);

        boolean existingProjectName = projectRepository.existsByName(request.name());
        if (existingProjectName) throw new IllegalArgumentException("Project name already exists");

        Project project = Project.builder()
                .name(request.name())
                .description(request.description())
                .status(ProjectStatus.ACTIVE.name())
                .build();
        projectRepository.saveAndFlush(project);
        log.info("Saving project successfully");

        ProjectMember projectMember = new ProjectMember();
        projectMember.setProjectId(project.getId());
        projectMember.setUserId(UUID.fromString("97582237-79b6-4fac-8974-fecebefb3e82"));
        projectMember.setProjectRole(ProjectRole.CREATOR.name());
        projectMemberRepository.save(projectMember);
        log.info("Saving project member successfully");

        return ApiResponse.success("Project created successfully");
    }

    @Override
    public ApiResponse<?> getAllProject(Pageable pageable) {
        log.info("Start get all projects with");
        Page<ProjectMember> projects = projectMemberRepository.findAllByUserId(pageable, UUID.fromString("97582237-79b6-4fac-8974-fecebefb3e82"));
        Page<GetProjectRes> response = projects.map(projectMapper::toGetProjectRes);
        return ApiResponse.success(PageResponse.of(response), "Get all projects successfully");
    }

    @Override
    public ApiResponse<Void> sendInvitation(UUID projectId, CreateInvitationReq request) {
        log.info("Start send invitation for projectId: {} with request: {}", projectId, request);
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new EntityNotFoundException("Project not found"));
        sendInvitationEmail(project, request);
        return ApiResponse.success("Invitation sent successfully");
    }

    @Override
    public String verifiedInvitationToken(String token) {
        log.info("Start verify invitation token");
        Map<String, String> dataRedis = redisService.get("verified_invitation:" + token, Map.class);
        if (dataRedis == null) {
            throw new IllegalArgumentException("Invitation is expired");
        }

        ProjectMember projectMember = new ProjectMember();
        projectMember.setProjectId(UUID.fromString(dataRedis.get("projectId")));
        projectMember.setUserId(UUID.fromString(dataRedis.get("userId")));
        projectMember.setProjectRole(ProjectRole.MEMBER.name());
        projectMemberRepository.save(projectMember);

        log.info("Verified invitation successfully");
        redisService.delete("verified_invitation:" + token);
        return hostProperties.frontendHost();
    }

    @Override
    @Transactional
    public ApiResponse<Void> removeUserFromProject(UUID projectId, UUID userId) {
        ProjectMember member = projectMemberRepository.findByProjectIdAndUserId(projectId, userId)
                .orElseThrow(() -> new EntityNotFoundException("Project member not found"));
        member.setRemovedAt(LocalDateTime.now());
        projectMemberRepository.save(member);
        return ApiResponse.success("User removed from project successfully");
    }

    @Override
    public ApiResponse<?> getProjectDetails(UUID projectId) {
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new EntityNotFoundException("Project not found"));

        List<ProjectMember> memberEntities = projectMemberRepository.findAllByProjectId(projectId);

        List<UUID> userIds = memberEntities.stream()
                .map(ProjectMember::getUserId)
                .toList();

        Map<UUID, GetUserRes> emailByUserId = new HashMap<>();
        try {
            ResponseEntity<ApiResponse<List<GetUserRes>>> resp = userClient.getUsersProfile(userIds);
            ApiResponse<List<GetUserRes>> apiResp = resp != null ? resp.getBody() : null;
            if (apiResp != null && apiResp.data() != null) {
                for (GetUserRes u : apiResp.data()) {
                    if (u != null && u.id() != null) {
                        emailByUserId.put(u.id(), u);
                    }
                }
            }
        } catch (Exception e) {
            log.warn("Failed to fetch user emails from user-service, proceeding without emails: {}", e.getMessage());
        }

        // map members to DTO including email
        var members = memberEntities.stream()
                .map(m -> new ProjectDetailRes.MemberInfo(
                        m.getUserId(),
                        emailByUserId.get(m.getUserId()).email(),
                        emailByUserId.get(m.getUserId()).fullName(),
                        m.getProjectRole(),
                        m.getJoinedAt(),
                        m.getRemovedAt()
                ))
                .toList();

        var folders = folderRepository.findAllByProjectId(projectId).stream()
                .map(f -> new ProjectDetailRes.FolderInfo(
                        f.getId(),
                        f.getName(),
                        f.getCreatedAt()
                ))
                .toList();

        var documents = documentRepository.findAllByProjectIdAndIsActiveTrue(projectId).stream()
                .map(d -> new ProjectDetailRes.DocumentInfo(
                        d.getId(),
                        d.getName(),
                        d.getFileType(),
                        d.getUploadedAt(),
                        d.getUploadedBy(),
                        d.getStatus()
                ))
                .toList();

        var videos = videoRepository.findAllByProjectIdAndIsActiveTrue(projectId).stream()
                .map(v -> new ProjectDetailRes.VideoInfo(
                        v.getId(),
                        v.getName(),
                        v.getFileType(),
                        v.getUploadedAt(),
                        v.getUploadedBy(),
                        v.getStatus()
                ))
                .toList();

        var response = new ProjectDetailRes(
                project.getId(),
                project.getName(),
                project.getDescription(),
                project.getCreatedAt(),
                members,
                folders,
                documents,
                videos
        );

        return ApiResponse.success(response, "Project details fetched successfully");
    }


    @Override
    public ApiResponse<?> uploadFile(UUID projectId, MultipartFile[] files) {
        log.info("Uploading file for project {}", projectId);
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new EntityNotFoundException("Project not found"));

        for (MultipartFile file : files) {
            String s3Key = s3Service.uploadFile(projectId, file);
            String category = FileUtil.classifyFile(file);

            switch (category) {
                case "video" -> {
                    Video video = new Video();
                    video.setProjectId(project.getId());
                    video.setName(file.getOriginalFilename());
                    video.setFilePath(s3Key);
                    video.setFileType(FileUtil.getFileExtension(file.getOriginalFilename()));
                    video.setIsActive(true);
                    video.setStatus(HandleStaus.PROCESSING.name());
                    videoRepository.save(video);
                }
//            case "folder" -> {
//                return ApiResponse.error("Cannot upload a folder!");
//            }
                case "document" -> {
                    Document document = new Document();
                    document.setProjectId(project.getId());
                    document.setName(file.getOriginalFilename());
                    document.setFilePath(s3Key);
                    document.setFileType(FileUtil.getFileExtension(file.getOriginalFilename()));
                    document.setIsActive(true);
                    document.setStatus(HandleStaus.PROCESSING.name());
                    documentRepository.save(document);
                }

                default -> throw new IllegalArgumentException("Invalid category");

            }
        }

        return ApiResponse.success("File uploaded and saved successfully.");

    }

    @Override
    public ApiResponse<?> searchEntityByPath(String path, String type) {
        log.info("Searching for {} with path: {}", type, path);
        switch (type.toLowerCase()) {
            case "document" -> {
                Document document = documentRepository.findByFilePathAndIsActiveTrue(path)
                        .orElseThrow(() -> new EntityNotFoundException("Document not found"));
                DocumentRes res = new DocumentRes(
                        document.getId(),
                        document.getName(),
                        document.getFilePath(),
                        document.getFileType(),
                        document.getProjectId(),
                        document.getUploadedAt()
                );

                return ApiResponse.success(res, "Document found successfully");
            }
            case "video" -> {
                Video video = videoRepository.findByFilePathAndIsActiveTrue(path)
                        .orElseThrow(() -> new EntityNotFoundException("Video not found"));
                VideoRes res = new VideoRes(
                        video.getId(),
                        video.getName(),
                        video.getFilePath(),
                        video.getFileType(),
                        video.getProjectId(),
                        video.getUploadedAt()
                );
                return ApiResponse.success(res, "Document found successfully");
            }
            default -> throw new IllegalArgumentException("Invalid type");
        }
    }

    private void sendInvitationEmail(Project project, CreateInvitationReq request) {
        try {
            log.info("Sending email verification to {}", request.email());
            String token = UUID.randomUUID().toString();

            log.info("Start calling user-service");
            CustomUserDetails currentUser = SecurityUtil.getCurrentUser();

            Map<String, String> payload = new HashMap<>();
            payload.put("inviteeName", request.fullName());
            payload.put("inviterName", currentUser.getFullName());
            payload.put("inviterEmail", currentUser.getUsername());
            payload.put("projectName", project.getName());
            payload.put("userRole", ProjectRole.valueOf(request.role()).name());
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd-MM-yyyy HH:mm");
            payload.put("invitationDate", LocalDateTime.now().format(formatter));
            payload.put("projectDescription", project.getDescription());
            payload.put("acceptInvitationLink", hostProperties.backendHost() + hostProperties.verifiedInvitation() + "/" + token);


            Map<String, String> dataRedis = new HashMap<>();
            dataRedis.put("projectId", project.getId().toString());
            dataRedis.put("userId", request.userId().toString());
            redisService.save("verified_invitation:" + token, dataRedis, Duration.ofDays(1));

            NotificationMessage message = NotificationMessage.builder()
                    .to(request.email())
                    .payload(payload)
                    .type(Template.EMAIL_INVITATION.name())
                    .build();

            sqsService.sendMessage(sqsProperties.emailQueue(), message);
            log.info("Send into email queue successfully");
        } catch (Exception e) {
            log.info("Failed to send email verification to {} cause by {}", request.email(), e.getMessage());
            throw new RuntimeException("Failed to send email verification", e);
        }
    }
}
