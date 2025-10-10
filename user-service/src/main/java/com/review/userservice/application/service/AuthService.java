package com.review.userservice.application.service;

import com.review.common.dto.response.ApiResponse;
import com.review.userservice.api.dto.auth.LoginReq;
import com.review.userservice.api.dto.auth.LoginRes;

public interface AuthService {

    ApiResponse<LoginRes> login(LoginReq loginReq);


}
