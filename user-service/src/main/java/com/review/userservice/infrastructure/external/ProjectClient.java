package com.review.userservice.infrastructure.external;


import com.review.common.dto.response.ApiResponse;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

import java.util.UUID;

@FeignClient(name = "project-service")
public interface ProjectClient {

    String BASE = "/api/project";

    @GetMapping(BASE + "/{projectId}/available-users")
    ApiResponse<?> getAvailableUsersForProject(@PathVariable UUID projectId);
}
