package com.review.projectservice.application;

import com.review.common.dto.response.ApiResponse;
import com.review.projectservice.api.dto.project.CreateProjectReq;
import org.springframework.data.domain.Pageable;

public interface ProjectService {

    ApiResponse<?> createProject(CreateProjectReq request);

    ApiResponse<?> getAllProject(Pageable pageable);

}
