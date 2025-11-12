package com.review.userservice.domain.repository;

import com.review.userservice.domain.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface UserRepository extends JpaRepository<User, UUID> {

    Optional<User> findByEmailAndIsActiveTrueAndEmailVerifiedTrue(String email);

    Optional<User> findByEmail(String email);

    List<User> findAllByIsActiveTrue();

    // New: search active users whose fullName contains the given string (case-insensitive)
    List<User> findAllByFullNameContainingIgnoreCaseAndIsActiveTrue(String name);

    List<User> findAllByEmailContainingIgnoreCaseAndIsActiveTrue(String email);

    List<User> findAllByEmailContainingIgnoreCase(String email);

}
