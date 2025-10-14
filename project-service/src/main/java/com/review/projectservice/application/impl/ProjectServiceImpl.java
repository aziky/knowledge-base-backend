package com.review.projectservice.application.impl;

import com.review.common.dto.response.ApiResponse;
import com.review.common.enumration.ProjectRole;
import com.review.common.enumration.ProjectStatus;
import com.review.projectservice.api.dto.project.CreateProjectRes;
import com.review.projectservice.application.ProjectService;
import com.review.projectservice.domain.entity.Project;
import com.review.projectservice.domain.entity.ProjectMember;
import com.review.projectservice.domain.repository.ProjectMemberRepository;
import com.review.projectservice.domain.repository.ProjectRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

@Service
@Slf4j
@RequiredArgsConstructor
public class ProjectServiceImpl implements ProjectService {

    private final ProjectRepository projectRepository;
    private final ProjectMemberRepository projectMemberRepository;

    @Override
    @Transactional
    public ApiResponse<?> createProject(CreateProjectRes request) {
        log.info("Handle create project request: {}", request);

        boolean existingProjectName = projectRepository.existsByName(request.name());
        if (existingProjectName) throw new IllegalArgumentException("Project name already exists");

        Project project =  Project.builder()
                .name(request.name())
                .description(request.description())
                .status(ProjectStatus.ACTIVE.name())
                .build();
        projectRepository.saveAndFlush(project);
        log.info("Saving project successfully");

        ProjectMember projectMember = new ProjectMember();
        projectMember.setProjectId(project.getId());
        projectMember.setUserId(UUID.fromString("97582237-79b6-4fac-8974-fecebefb3e82"));
        projectMember.setProjectRole(ProjectRole.OWNER.name());
        projectMemberRepository.save(projectMember);
        log.info("Saving project member successfully");

        return ApiResponse.success("Project created successfully");
    }
}
