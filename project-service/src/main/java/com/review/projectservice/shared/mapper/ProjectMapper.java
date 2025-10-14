package com.review.projectservice.shared.mapper;

import com.review.projectservice.api.dto.project.GetProjectRes;
import com.review.projectservice.domain.entity.ProjectMember;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

@Mapper(componentModel = "spring")
public interface ProjectMapper {

    @Mapping(source = "project.name", target = "projectName")
    @Mapping(source = "joinedAt", target = "joinedAt", dateFormat = "dd-MM-yyyy")
    @Mapping(source = "removedAt", target = "removedAt", dateFormat = "dd-MM-yyyy")
    GetProjectRes toGetProjectRes(ProjectMember projectMember);


}
