package com.review.projectservice.application.impl;

import com.review.common.dto.response.ApiResponse;
import com.review.projectservice.api.dto.video.DeleteVideoReq;
import com.review.projectservice.api.dto.video.VideoRes;
import com.review.projectservice.application.VideoService;
import com.review.projectservice.domain.entity.Video;
import com.review.projectservice.domain.repository.VideoRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class VideoServiceImpl implements VideoService {

    private final VideoRepository videoRepository;

    @Override
    @Transactional
    public ApiResponse<?> deleteListVideo(DeleteVideoReq request) {
        // ...existing code...
        List<UUID> ids = request.videoIds();
        List<Video> videos = videoRepository.findAllById(ids);
        videos.forEach(v -> v.setIsActive(false));
        videoRepository.saveAll(videos);
        return ApiResponse.success("Delete list video successfully");
    }

    @Override
    @Transactional
    public ApiResponse<?> updateVideoStatus(UUID videoId, String status) {
        // ...existing code...
        Video video = videoRepository.findById(videoId)
                .orElseThrow(() -> new IllegalArgumentException("Video not found: " + videoId));
        video.setStatus(status);
        videoRepository.save(video);
        return ApiResponse.success("Update video successfully");
    }

}
