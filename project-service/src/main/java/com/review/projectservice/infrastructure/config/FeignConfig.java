package com.review.projectservice.infrastructure.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class FeignConfig {

    @Bean
    public EnhancedAuthContextFeignInterceptor authContextFeignInterceptor() {
        return new EnhancedAuthContextFeignInterceptor();
    }

}
