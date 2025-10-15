package com.review.userservice.infrastructure.config;

import com.review.common.shared.CustomHeader;
import com.review.common.shared.CustomUserDetails;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;
import java.util.UUID;

@Component
@Slf4j
public class CustomHeaderAuthFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        String userId = request.getHeader(CustomHeader.X_USER_ID);
        String role = request.getHeader(CustomHeader.X_ROLES);
        String email = request.getHeader(CustomHeader.X_EMAIL);
        String fullName = request.getHeader(CustomHeader.X_FULL_NAME);
        if (userId != null && role != null) {

            List<SimpleGrantedAuthority> authorities = List.of(new SimpleGrantedAuthority(role));
            CustomUserDetails userDetails = new CustomUserDetails(UUID.fromString(userId) ,email, "", fullName, authorities);

            Authentication auth = new UsernamePasswordAuthenticationToken(userDetails, null, authorities);
            SecurityContextHolder.getContext().setAuthentication(auth);
        }

        log.info("Start handle uri {} with userId {}", request.getRequestURI(), userId);
        filterChain.doFilter(request, response);
    }
}
