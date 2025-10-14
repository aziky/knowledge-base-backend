package com.review.projectservice.infrastructure.external;

import com.review.common.dto.request.user.GetUserRes;
import com.review.common.dto.response.ApiResponse;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

import java.util.UUID;

@FeignClient(name = "user-service")
public interface UserClient {

    String BASE = "/api/user";

    @GetMapping(BASE + "/{userId}")
    ResponseEntity<ApiResponse<GetUserRes>> getUserById(@PathVariable UUID userId);
}
