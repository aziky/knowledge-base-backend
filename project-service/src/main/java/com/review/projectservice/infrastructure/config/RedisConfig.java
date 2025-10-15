package com.review.projectservice.infrastructure.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;
import org.springframework.data.redis.serializer.StringRedisSerializer;

@Configuration
@RequiredArgsConstructor
public class RedisConfig {

    private final ObjectMapper objectMapper;
    private final RedisConnectionFactory redisConnectionFactory;

    @Bean
    public RedisTemplate<String, Object> redisTemplate() {
        RedisTemplate<String, Object> rt = new RedisTemplate<>();
        rt.setConnectionFactory(redisConnectionFactory);

        var jsonSerializer = new GenericJackson2JsonRedisSerializer(objectMapper);
        var stringSerializer = new StringRedisSerializer();

        rt.setKeySerializer(stringSerializer);
        rt.setHashKeySerializer(stringSerializer);
        rt.setValueSerializer(jsonSerializer);
        rt.setHashValueSerializer(jsonSerializer);
        rt.afterPropertiesSet();
        return rt;
    }

}