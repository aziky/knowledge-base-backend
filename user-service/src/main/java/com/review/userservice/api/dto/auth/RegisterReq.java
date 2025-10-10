package com.review.userservice.api.dto.auth;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record RegisterReq(
    @Email
    @NotBlank
    @Size(max = 100)
    String email,

    @NotBlank
    @Size(min = 6, max = 100)
    String password,

    @NotBlank
    @Size(max = 100)
    String fullName,

    @NotBlank
    @Size(max = 50)
    String role
) {}
