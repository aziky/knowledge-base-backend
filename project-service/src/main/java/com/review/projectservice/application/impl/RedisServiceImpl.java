package com.review.projectservice.application.impl;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.review.projectservice.application.RedisService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;

@Service
@RequiredArgsConstructor
@Slf4j
public class RedisServiceImpl implements RedisService {

    private final RedisTemplate<String, Object> redisTemplate;
    private final ObjectMapper objectMapper;

    @Override
    public <T> void save(String key, T value, Duration expiration) {
        redisTemplate.opsForValue().set(key, value, expiration);
        log.debug("Saved to Redis - Key: {}", key);
    }

    @Override
    public <T> T get(String key, Class<T> clazz) {
        Object value = redisTemplate.opsForValue().get(key);
        if (value == null) {
            return null;
        }

        return objectMapper.convertValue(value, clazz);
    }

    @Override
    public void delete(String key) {
        redisTemplate.delete(key);
        log.debug("Deleted from Redis - Key: {}", key);
    }
}