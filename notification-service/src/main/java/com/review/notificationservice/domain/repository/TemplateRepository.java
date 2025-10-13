package com.review.notificationservice.domain.repository;

import com.review.notificationservice.domain.entity.Template;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface TemplateRepository extends JpaRepository<Template, UUID> {

    Template findByTypeAndStatusIsTrue(String type);

}
