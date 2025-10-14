package com.review.userservice.application.impl;

import com.review.common.dto.request.user.GetUserRes;
import com.review.common.dto.response.ApiResponse;
import com.review.userservice.application.UserService;
import com.review.userservice.domain.entity.User;
import com.review.userservice.domain.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class UserServiceImpl implements UserService {

    private final UserRepository userRepository;

    public ApiResponse<GetUserRes> getUserProfile(UUID userId) {
        log.info("Fetching user profile for userId: {}", userId);
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("User not found with id: " + userId));

        GetUserRes getUserRes = GetUserRes.builder()
                .email(user.getEmail())
                .fullName(user.getFullName())
                .build();

        return ApiResponse.success(getUserRes);
    }

}
