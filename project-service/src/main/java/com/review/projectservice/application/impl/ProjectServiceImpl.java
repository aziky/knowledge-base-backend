package com.review.projectservice.application.impl;

import com.review.common.dto.request.NotificationMessage;
import com.review.common.dto.request.user.GetUserRes;
import com.review.common.dto.response.ApiResponse;
import com.review.common.enumration.ProjectRole;
import com.review.common.enumration.ProjectStatus;
import com.review.common.enumration.Template;
import com.review.common.shared.CustomUserDetails;
import com.review.projectservice.api.dto.project.CreateInvitationReq;
import com.review.projectservice.api.dto.project.CreateProjectReq;
import com.review.projectservice.api.dto.project.GetProjectRes;
import com.review.projectservice.application.ProjectService;
import com.review.projectservice.application.SQSService;
import com.review.projectservice.domain.entity.Project;
import com.review.projectservice.domain.entity.ProjectMember;
import com.review.projectservice.domain.repository.ProjectMemberRepository;
import com.review.projectservice.domain.repository.ProjectRepository;
import com.review.projectservice.infrastructure.external.UserClient;
import com.review.projectservice.infrastructure.properties.HostProperties;
import com.review.projectservice.infrastructure.properties.SQSProperties;
import com.review.projectservice.shared.PageResponse;
import com.review.projectservice.shared.SecurityUtil;
import com.review.projectservice.shared.mapper.ProjectMapper;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
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
    private final UserClient userClient;
    

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


    private void sendInvitationEmail(Project project, CreateInvitationReq request) {
        try {
            log.info("Sending email verification to {}", request.email());
            String token = UUID.randomUUID().toString();

            log.info("Start calling user-service");
            GetUserRes user = userClient.getUserById(request.userId()).getBody().data();
            CustomUserDetails currentUser = SecurityUtil.getCurrentUser();

            Map<String, String> payload = new HashMap<>();
            payload.put("inviteeName", request.fullName());
            payload.put("inviterName", currentUser.getFullName());
            payload.put("inviterEmail", currentUser.getUsername());
            payload.put("projectName", project.getName());
            payload.put("userRole", ProjectRole.MEMBER.name());
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd-MM-yyyy HH:mm");
            payload.put("invitationDate", LocalDateTime.now().format(formatter));
            payload.put("projectDescription", project.getDescription());
            payload.put("acceptInvitationLink", hostProperties.backendHost() + hostProperties.verifiedInvitation() + "/" + token);

            NotificationMessage message = NotificationMessage.builder()
                    .to(request.email())
                    .payload(payload)
                    .type(Template.EMAIL_VERIFICATION.name())
                    .build();

            sqsService.sendMessage(sqsProperties.emailQueue(), message);
            log.info("Send into email queue successfully");
        } catch (Exception e) {
            log.info("Failed to send email verification to {} cause by {}", request.email(), e.getMessage());
            throw new RuntimeException("Failed to send email verification", e);
        }
    }
}
