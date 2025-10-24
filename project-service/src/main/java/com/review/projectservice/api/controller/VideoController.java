package com.review.projectservice.api.controller;

import com.review.projectservice.api.dto.video.DeleteVideoReq;
import com.review.projectservice.application.VideoService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/video")
@RequiredArgsConstructor
public class VideoController {

    private final VideoService videoService;

    @DeleteMapping()
    public ResponseEntity<?> deleteListVideo(@RequestBody DeleteVideoReq request) {
        return ResponseEntity.ok(videoService.deleteListVideo(request));
    }

    @PatchMapping("/{videoId}/status")
    public ResponseEntity<?> updateVideoStatus(@PathVariable("videoId") UUID videoId, @RequestParam("status") String status) {
        return ResponseEntity.ok(videoService.updateVideoStatus(videoId, status));
    }

}
