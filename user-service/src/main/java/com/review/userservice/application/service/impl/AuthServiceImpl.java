package com.review.userservice.application.service.impl;

import com.review.common.dto.response.ApiResponse;
import com.review.userservice.api.dto.auth.LoginReq;
import com.review.userservice.api.dto.auth.LoginRes;
import com.review.userservice.api.dto.auth.RegisterReq;
import com.review.userservice.api.dto.auth.RegisterRes;
import com.review.userservice.application.service.AuthService;
import com.review.userservice.domain.entity.User;
import com.review.userservice.domain.repository.UserRepository;
import com.review.userservice.shared.utils.JwtUtil;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@Slf4j
@RequiredArgsConstructor
public class AuthServiceImpl implements AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    @Override
    public ApiResponse<LoginRes> login(LoginReq request) {
        log.info("Handle login request with email {}", request.email());
        User user = userRepository.findByEmailAndIsActiveTrue(request.email())
                .orElseThrow(() -> new EntityNotFoundException("Invalid email or password"));

        if (!passwordEncoder.matches(request.password(), user.getPasswordHash())) {
            throw new EntityNotFoundException("Invalid email or password");
        }

        String token = jwtUtil.generateToken(user);
        LoginRes response = new LoginRes(token);
        return ApiResponse.success(response, "Login successful");
    }

    @Override
    public ApiResponse<RegisterRes> register(RegisterReq request) {
        log.info("Registering new user with email {}", request.email());
        if (userRepository.findByEmailAndIsActiveTrue(request.email()).isPresent()) {
            throw new IllegalArgumentException("Email already exists");
        }
        User user = new User();
        user.setEmail(request.email());
        user.setPasswordHash(passwordEncoder.encode(request.password()));
        user.setFullName(request.fullName());
        user.setRole(request.role());
        user.setIsActive(true);
        user.setEmailVerified(false);
        userRepository.save(user);

        RegisterRes response = new RegisterRes(user.getId(), user.getEmail(), user.getFullName(), user.getRole());
        return ApiResponse.success(response, "User registered successfully");
    }

}
