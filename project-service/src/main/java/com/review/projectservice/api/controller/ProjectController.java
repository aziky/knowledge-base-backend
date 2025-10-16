package com.review.projectservice.api.controller;

import com.review.common.dto.response.ApiResponse;
import com.review.projectservice.api.dto.project.CreateInvitationReq;
import com.review.projectservice.api.dto.project.CreateProjectReq;
import com.review.projectservice.application.ProjectService;
import com.review.projectservice.application.S3Service;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.view.RedirectView;

import java.util.UUID;

@RequiredArgsConstructor
@RestController
@RequestMapping("/project")
public class ProjectController {

    private final ProjectService projectService;
    private final S3Service s3Service;

    @PostMapping()
    public ResponseEntity<?> createProject(@RequestBody CreateProjectReq request) {
        return ResponseEntity.ok(projectService.createProject(request));
    }

    @GetMapping()
    public ResponseEntity<?> getAllProjects(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "joinedAt") String sortBy,
            @RequestParam(defaultValue = "desc") String sortDir
    ) {
        Sort sort = sortDir.equalsIgnoreCase("asc")
                ? Sort.by(sortBy).ascending()
                : Sort.by(sortBy).descending();

        Pageable pageable = PageRequest.of(page, size, sort);
        return ResponseEntity.ok(projectService.getAllProject(pageable));
    }

    @PostMapping("/{projectId}/invite")
    public ResponseEntity<?> inviteUserToProject(
            @PathVariable UUID projectId,
            @RequestBody CreateInvitationReq request
            ) {
        return ResponseEntity.ok(projectService.sendInvitation(projectId, request));
    }

    @GetMapping("/verified-invitation/{token}")
    public RedirectView verifiedInvitation(@PathVariable String token) {
        return new RedirectView(projectService.verifiedInvitationToken(token));
    }

    @PutMapping("/{projectId}/remove-user/{userId}")
    public ResponseEntity<?> removeUserFromProject(
            @PathVariable UUID projectId,
            @PathVariable UUID userId
    ) {
        return ResponseEntity.ok(projectService.removeUserFromProject(projectId, userId));
    }

    @GetMapping("/{projectId}/details")
    public ResponseEntity<?> getProjectDetails(@PathVariable UUID projectId) {
        return ResponseEntity.ok(projectService.getProjectDetails(projectId));
    }


    @PostMapping("/{projectId}/upload")
    public ResponseEntity<ApiResponse<?>> uploadFile(@PathVariable UUID projectId, @RequestParam MultipartFile file) {
        s3Service.uploadFile(projectId, file);
        return ResponseEntity.ok(ApiResponse.success("File uploaded successfully"));
    }


}
