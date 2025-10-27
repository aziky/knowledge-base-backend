package com.review.userservice.application.impl;

import com.review.common.dto.request.NotificationMessage;
import com.review.common.dto.response.ApiResponse;
import com.review.common.enumration.Template;
import com.review.common.shared.ApplicationException;
import com.review.userservice.api.dto.auth.LoginReq;
import com.review.userservice.api.dto.auth.LoginRes;
import com.review.userservice.api.dto.auth.RegisterReq;
import com.review.userservice.api.dto.auth.RegisterRes;
import com.review.userservice.application.AuthService;
import com.review.userservice.application.RedisService;
import com.review.userservice.application.SQSService;
import com.review.userservice.domain.entity.User;
import com.review.userservice.domain.repository.UserRepository;
import com.review.userservice.infrastructure.properties.HostProperties;
import com.review.userservice.infrastructure.properties.SQSProperties;
import com.review.userservice.shared.utils.JwtUtil;
import io.lettuce.core.RedisCommandTimeoutException;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@Service
@Slf4j
@RequiredArgsConstructor
public class AuthServiceImpl implements AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;
    private final SQSService sqsService;
    private final SQSProperties sqsProperties;
    private final HostProperties hostProperties;
    private final RedisService redisService;

    @Override
    public ApiResponse<LoginRes> login(LoginReq request) {
        log.info("Handle login request with email {}", request.email());
        User user = userRepository.findByEmailAndIsActiveTrueAndEmailVerifiedTrue(request.email())
                .orElseThrow(() -> new EntityNotFoundException("Invalid email or password"));

        if (!passwordEncoder.matches(request.password(), user.getPasswordHash())) {
            throw new EntityNotFoundException("Invalid email or password");
        }

        String token = jwtUtil.generateToken(user);
        LoginRes response = new LoginRes(token, user.getRole(), user.getFullName(), user.getEmail());
        return ApiResponse.success(response, "Login successful");
    }

    @Transactional
    @Override
    public ApiResponse<RegisterRes> register(RegisterReq request) {
        log.info("Registering new user with email {}", request.email());
        if (userRepository.findByEmail(request.email()).isPresent()) {
            throw new ApplicationException.DuplicateInformation("Email is already in use");
        }
        User user = new User();
        user.setEmail(request.email());
        user.setPasswordHash(passwordEncoder.encode(request.password()));
        user.setFullName(request.fullName());
        user.setRole(request.role().name());
        user.setIsActive(true);
        user.setEmailVerified(false);
        userRepository.save(user);

        String token = UUID.randomUUID().toString();
        redisService.save("verified_token:" + token, user, Duration.ofHours(24));
        log.info("save verified token for user {} with token {}", user.getEmail(), token);

        handleSendEmailVerification(user, token);
        RegisterRes response = new RegisterRes(user.getId(), user.getEmail(), user.getFullName(), user.getRole());
        return ApiResponse.success(response, "User registered successfully");
    }

    @Override
    @Transactional
    public ApiResponse<Void> verifyAccount(String token) {
        log.info("Verifying account with token {}", token);
        User user = redisService.get("verified_token:" + token, User.class);
        if (user == null) throw new RedisCommandTimeoutException("Token is invalid or expired");

        user.setEmailVerified(true);
        userRepository.save(user);

        return ApiResponse.success(null, "Verify account successfully");
    }


    private void handleSendEmailVerification(User user, String token) {
        try {
            log.info("Sending email verification to {}", user.getEmail());
            Map<String, String> payload = new HashMap<>();
            payload.put("userName", user.getFullName());
            payload.put("verificationLink", hostProperties.backendHost() + hostProperties.handleVerificationUrl() + "/" + token);

            NotificationMessage message = NotificationMessage.builder()
                    .to(user.getEmail())
                    .payload(payload)
                    .type(Template.EMAIL_VERIFICATION.name())
                    .build();

            sqsService.sendMessage(sqsProperties.emailQueue(), message);
        } catch (Exception e) {
            log.info("Failed to send email verification to {} cause by {}", user.getEmail(), e.getMessage());
            throw new RuntimeException("Failed to send email verification", e);
        }
    }

}
