package com.review.projectservice.api.controller;

import com.review.projectservice.api.dto.project.CreateProjectRes;
import com.review.projectservice.application.ProjectService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RequiredArgsConstructor
@RestController
@RequestMapping("/project")
public class ProjectController {

    private final ProjectService projectService;

    @PostMapping()
    public ResponseEntity<?> createProject(@RequestBody CreateProjectRes request) {
        return ResponseEntity.ok(projectService.createProject(request));
    }

}
