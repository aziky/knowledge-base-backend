package com.review.userservice.api.controller;


import com.review.userservice.api.dto.auth.LoginReq;
import com.review.userservice.api.dto.auth.RegisterReq;
import com.review.userservice.application.AuthService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
@Slf4j
public class AuthController {

    private final AuthService authService;

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginReq request) {
        log.info("Start handle login request");
        return ResponseEntity.ok(authService.login(request));
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody RegisterReq request) {
        return ResponseEntity.ok(authService.register(request));
    }

    @GetMapping("/verify-account/{token}")
    public ResponseEntity<?> verifyAccount(@PathVariable String token) {
        return ResponseEntity.ok(authService.verifyAccount(token));
    }




}
