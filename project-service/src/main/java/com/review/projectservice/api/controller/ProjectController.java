package com.review.projectservice.api.controller;

import com.review.common.dto.response.ApiResponse;
import com.review.projectservice.api.dto.project.CreateInvitationReq;
import com.review.projectservice.api.dto.project.CreateProjectReq;
import com.review.projectservice.api.dto.project.DeleteFileReq;
import com.review.projectservice.application.ProjectService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.view.RedirectView;

import java.util.List;
import java.util.UUID;

@RequiredArgsConstructor
@RestController
@RequestMapping("/project")
public class ProjectController {

    private final ProjectService projectService;

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
            @RequestBody List<CreateInvitationReq> requestList
            ) {
        return ResponseEntity.ok(projectService.sendInvitation(projectId, requestList));
    }

    @GetMapping("/verified-invitation/{token}")
    public RedirectView verifiedInvitation(@PathVariable String token) {
        return new RedirectView(projectService.verifiedInvitationToken(token));
    }

    @DeleteMapping("/{projectId}/users/{userId}")
    public ResponseEntity<?> removeUserFromProject(
            @PathVariable UUID projectId,
            @PathVariable UUID userId
    ) {
        return ResponseEntity.ok(projectService.removeUserFromProject(projectId, userId));
    }

    @GetMapping("/{projectId}")
    public ResponseEntity<?> getProjectDetails(@PathVariable UUID projectId) {
        return ResponseEntity.ok(projectService.getProjectDetails(projectId));
    }


    @PostMapping("/{projectId}/upload")
    public ResponseEntity<?> uploadFile(@PathVariable UUID projectId, @RequestPart("files") MultipartFile[] files) {
        return ResponseEntity.ok(projectService.uploadFile(projectId, files));
    }

    @GetMapping("/path")
    public ResponseEntity<ApiResponse<?>> searchByPath(@RequestParam String path, @RequestParam String type) {
        return ResponseEntity.ok(projectService.searchEntityByPath(path, type));
    }

    @DeleteMapping("/{projectId}/files")
    public ResponseEntity<?> deleteFile(@PathVariable UUID projectId, @RequestBody List<DeleteFileReq> request) {
        return ResponseEntity.ok(projectService.deleteListFile(projectId, request));
    }

    @GetMapping("/download/{filedId}")
    public ResponseEntity<?> downloadFile(@PathVariable UUID filedId, @RequestParam String type) {
        return ResponseEntity.ok(projectService.downloadFile(filedId, type));
    }

    @DeleteMapping("/{projectId}")
    public ResponseEntity<?> deleteProject(@PathVariable UUID projectId) {
        return ResponseEntity.ok(projectService.deleteProject(projectId));
    }

    @PatchMapping("/{projectId}")
    public ResponseEntity<?> activeProject(@PathVariable UUID projectId) {
        return ResponseEntity.ok(projectService.activeProject(projectId));
    }



}
