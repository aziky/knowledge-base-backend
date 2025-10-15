package com.review.gatewayservice.config;

import com.review.common.enumration.Role;
import com.review.gatewayservice.filter.JWTAuthenticationFilter;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.reactive.EnableWebFluxSecurity;
import org.springframework.security.config.web.server.SecurityWebFiltersOrder;
import org.springframework.security.config.web.server.ServerHttpSecurity;
import org.springframework.security.web.server.SecurityWebFilterChain;


@Configuration
@EnableWebFluxSecurity
@Slf4j
@RequiredArgsConstructor
public class SecurityConfig {

    private final JWTAuthenticationFilter jwtAuthFilter;
//    private final WebUrlProperties webUrlProperties;

    private static final String USER_PREFIX = "/user-service/api";
    private static final String PROJECT_PREFIX = "/project-service/api";


    private static final String[] PUBLIC_ENDPOINT = {
//            "/swagger-ui.html",
//            "/swagger-ui/**",
//            "/v3/api-docs/**",
//            "/webjars/**",
//            "/",
//            "/user-service/api/v3/api-docs",
//            "/booking-service/api/v3/api-docs",
//            "/payment-service/api/v3/api-docs",
//            "/notification-service/api/v3/api-docs",
//            "/recommendation-service/api/v3/api-docs",
            USER_PREFIX + "/auth/**",
    };

    private static final String[] USER_ENDPOINT = {
            USER_PREFIX + "/user/**",
            PROJECT_PREFIX + "/project/**",
    };

    @Bean
    public SecurityWebFilterChain securityWebFilterChain(ServerHttpSecurity http) {
        return http
                .csrf(ServerHttpSecurity.CsrfSpec::disable)
//                .cors(cors -> cors.configurationSource(corsConfigurationSource()))
                .authorizeExchange(exchanges -> exchanges
                        .pathMatchers(PUBLIC_ENDPOINT).permitAll()
                        .pathMatchers(USER_ENDPOINT).hasAuthority(Role.USER.name())
                        .anyExchange().authenticated()
                )
                .formLogin(ServerHttpSecurity.FormLoginSpec::disable)
                .httpBasic(ServerHttpSecurity.HttpBasicSpec::disable)
                .addFilterAt(jwtAuthFilter, SecurityWebFiltersOrder.AUTHENTICATION)
                .build();
    }


//    @Bean
//    public CorsConfigurationSource corsConfigurationSource() {
//        CorsConfiguration corsConfig = new CorsConfiguration();
//        corsConfig.setAllowCredentials(true);
//        corsConfig.setAllowedOrigins(List.of(
//                webUrlProperties.host(),
//                "http://localhost:8050"
//        ));
//        corsConfig.addAllowedHeader("*");
//        corsConfig.addAllowedMethod("*");
//
//        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
//        source.registerCorsConfiguration("/**", corsConfig);
//
//        return source;
//    }

}