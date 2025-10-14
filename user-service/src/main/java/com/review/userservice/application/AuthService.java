package com.review.userservice.application;

import com.review.common.dto.response.ApiResponse;
import com.review.userservice.api.dto.auth.LoginReq;
import com.review.userservice.api.dto.auth.LoginRes;
import com.review.userservice.api.dto.auth.RegisterReq;
import com.review.userservice.api.dto.auth.RegisterRes;

public interface AuthService {

    ApiResponse<LoginRes> login(LoginReq loginReq);

    ApiResponse<RegisterRes> register(RegisterReq registerReq);

    ApiResponse<Void> verifyAccount(String token);

}
