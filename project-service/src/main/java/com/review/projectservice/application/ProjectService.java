package com.review.projectservice.application;

import com.review.common.dto.response.ApiResponse;
import com.review.projectservice.api.dto.project.CreateProjectRes;

public interface ProjectService {

    ApiResponse<?> createProject(CreateProjectRes request);

}
