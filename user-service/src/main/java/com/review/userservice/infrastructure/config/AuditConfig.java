package com.review.userservice.infrastructure.config;

import com.review.common.shared.CustomUserDetails;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.domain.AuditorAware;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

import java.util.Optional;

@Configuration
@RequiredArgsConstructor
public class AuditConfig {


    @Bean
    public AuditorAware<String> auditorProvider() {
        return () -> {

            Authentication auth = SecurityContextHolder.getContext().getAuthentication();
            if (auth != null && auth.isAuthenticated() && auth.getPrincipal() instanceof CustomUserDetails) {
                return Optional.of(auth.getName());
            }
            return Optional.of("system");
        };
    }
}