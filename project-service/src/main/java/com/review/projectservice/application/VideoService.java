package com.review.projectservice.application;

import com.review.common.dto.response.ApiResponse;
import com.review.projectservice.api.dto.video.DeleteVideoReq;

import java.util.UUID;

public interface VideoService {

    ApiResponse<?> deleteListVideo(DeleteVideoReq request);

    ApiResponse<?> updateVideoStatus(UUID videoId, String status);

}
