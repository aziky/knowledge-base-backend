package com.review.projectservice.domain.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;
import lombok.Getter;
import lombok.Setter;
import org.hibernate.annotations.CreationTimestamp;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.Instant;
import java.time.LocalDateTime;
import java.util.UUID;

@Getter
@Setter
@Entity
@EntityListeners(AuditingEntityListener.class)
@Data
@Table(name = "project_members", schema = "kb_project")
public class ProjectMember {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "project_member_id", nullable = false)
    private UUID id;

    @NotNull
    @Column(name = "user_id", nullable = false)
    private UUID userId;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "project_id", insertable = false, updatable = false)
    private Project project;

    @NotNull
    @Column(name = "project_id", nullable = false)
    private UUID projectId;

    @Size(max = 50)
    @Column(name = "project_role", length = 50)
    private String projectRole;

    @Column(name = "is_creator")
    private Boolean isCreator;

    @CreationTimestamp
    @Column(name = "joined_at")
    private LocalDateTime joinedAt;

    @Column(name = "removed_at")
    private LocalDateTime removedAt;

}