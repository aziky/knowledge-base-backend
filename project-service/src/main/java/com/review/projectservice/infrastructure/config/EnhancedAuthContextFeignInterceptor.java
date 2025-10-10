package com.review.projectservice.infrastructure.config;

import com.review.common.shared.CustomHeader;
import com.review.common.shared.CustomUserDetails;
import com.review.projectservice.shared.SecurityUtil;
import feign.RequestInterceptor;
import feign.RequestTemplate;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.stereotype.Component;

import java.util.Collection;
import java.util.stream.Collectors;

@Slf4j
@Component
@RequiredArgsConstructor
public class EnhancedAuthContextFeignInterceptor implements RequestInterceptor {


    @Override
    public void apply(RequestTemplate template) {
        CustomUserDetails userDetails = SecurityUtil.getCurrentUser();

        template.header(CustomHeader.X_USER_ID, userDetails.getUserId().toString());
        template.header(CustomHeader.X_EMAIL, userDetails.getUsername());

        Collection<? extends GrantedAuthority> authorities = userDetails.getAuthorities();
        if (authorities != null && !authorities.isEmpty()) {
            String roles = authorities.stream()
                    .map(GrantedAuthority::getAuthority)
                    .collect(Collectors.joining(","));
            template.header(CustomHeader.X_ROLES, roles);
        }
        log.info("Added auth headers to Feign request - UserId: {}, Email: {}",
                userDetails.getUserId(), userDetails.getUsername());
    }
}
