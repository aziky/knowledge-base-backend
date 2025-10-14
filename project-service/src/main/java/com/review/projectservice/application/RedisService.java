package com.review.projectservice.application;

import java.time.Duration;

public interface RedisService {
    <T> void save(String key, T value, Duration expiration);
    <T> T get(String key, Class<T> clazz);
    void delete(String key);
}