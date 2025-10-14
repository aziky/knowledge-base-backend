package com.review.projectservice.domain.repository;

import com.review.projectservice.domain.entity.Project;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface ProjectRepository extends JpaRepository<Project, UUID> {

    Boolean existsByName(String name);

}
