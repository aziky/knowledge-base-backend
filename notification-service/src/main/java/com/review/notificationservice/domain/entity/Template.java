package com.review.notificationservice.domain.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.Setter;

import java.util.UUID;

@Getter
@Setter
@Entity
@Table(name = "templates", schema = "kb_notification")
public class Template {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "template_id", nullable = false)
    private UUID id;

    @Size(max = 100)
    @Column(name = "type", length = 100)
    private String type;

    @Size(max = 255)
    @Column(name = "subject")
    private String subject;

    @Column(name = "template", length = Integer.MAX_VALUE)
    private String template;

    @Column(name = "status")
    private Boolean status;

}