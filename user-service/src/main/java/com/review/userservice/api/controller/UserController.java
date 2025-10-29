package com.review.userservice.api.controller;

import com.review.userservice.application.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/user")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @GetMapping("/{userId}")
    public ResponseEntity<?> getUserProfile(@PathVariable UUID userId) {
        return ResponseEntity.ok(userService.getUserProfile(userId));
    }


    @PostMapping()
    public ResponseEntity<?> getAllUsersByUserId(@RequestBody List<UUID> listUserId ) {
        return ResponseEntity.ok(userService.getUsersProfile(listUserId));
    }

}
