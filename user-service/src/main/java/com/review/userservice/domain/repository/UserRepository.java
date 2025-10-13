package com.review.userservice.domain.repository;

import com.review.userservice.domain.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

public interface UserRepository extends JpaRepository<User, UUID> {

    Optional<User> findByEmailAndIsActiveTrue(String email);

    Optional<User> findByEmail(String email);


}
