package com.review.userservice.application.impl;

import com.review.common.dto.request.user.GetUserRes;
import com.review.common.dto.response.ApiResponse;
import com.review.userservice.application.UserService;
import com.review.userservice.domain.entity.User;
import com.review.userservice.domain.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

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

    @Override
    public ApiResponse<List<GetUserRes>> getUsersProfile(List<UUID> userIds) {
        log.info("Fetching user profiles for userIds: {}", userIds);

        Iterable<User> usersIterable = userRepository.findAllById(userIds);
        Map<UUID, User> userById = StreamSupport.stream(usersIterable.spliterator(), false)
                .collect(Collectors.toMap(User::getId, Function.identity()));

        List<GetUserRes> results = userIds.stream()
                .filter(userById::containsKey)
                .map(id -> {
                    User u = userById.get(id);
                    return GetUserRes.builder()
                            .id(u.getId())
                            .email(u.getEmail())
                            .fullName(u.getFullName())
                            .build();
                })
                .toList();

        return ApiResponse.success(results);
    }

}
