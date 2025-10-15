package com.review.projectservice.domain.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Builder;
import lombok.Data;
import lombok.Getter;
import lombok.Setter;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.Instant;
import java.time.LocalDateTime;
import java.util.Map;
import java.util.UUID;

@Data
@Getter
@Setter
@Entity
@EntityListeners(AuditingEntityListener.class)
@Table(name = "videos", schema = "kb_project")
public class Video {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "video_id", nullable = false)
    private UUID id;

    @NotNull
    @Column(name = "uploaded_by", nullable = false)
    private UUID uploadedBy;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "project_id", insertable = false, updatable = false)
    private Project project;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "folder_id", insertable = false, updatable = false)
    private Folder folder;

    @Column(name = "folder_id")
    private UUID folderId;

    @Size(max = 255)
    @NotNull
    @Column(name = "name", nullable = false)
    private String name;

    @Column(name = "file_path", length = Integer.MAX_VALUE)
    private String filePath;

    @Size(max = 20)
    @Column(name = "file_type", length = 20)
    private String fileType;

    @Column(name = "transcript", length = Integer.MAX_VALUE)
    private String transcript;

    @Column(name = "metadata")
    @JdbcTypeCode(SqlTypes.JSON)
    private Map<String, Object> metadata;

    @CreationTimestamp
    @Column(name = "uploaded_at")
    private LocalDateTime uploadedAt;

}
