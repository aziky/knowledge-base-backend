package com.review.userservice.application.service.impl;

import com.review.common.dto.response.ApiResponse;
import com.review.userservice.api.dto.auth.LoginReq;
import com.review.userservice.api.dto.auth.LoginRes;
import com.review.userservice.application.service.AuthService;
import com.review.userservice.domain.entity.User;
import com.review.userservice.domain.repository.UserRepository;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Service
@Slf4j
@RequiredArgsConstructor
public class AuthServiceImpl implements AuthService {

    private final UserRepository userRepository;

    @Override
    public ApiResponse<LoginRes> login(LoginReq request) {
        log.info("Handle login request with email {}", request.email());
        User user = userRepository.findByEmailAndPasswordHash(request.email(), request.password())
                .orElseThrow(() -> new EntityNotFoundException("User not found"));


        LoginRes response = new LoginRes("access token");
        return ApiResponse.success(response, "Login successful");

    }
}
