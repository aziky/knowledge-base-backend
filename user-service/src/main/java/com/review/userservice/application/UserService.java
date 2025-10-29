package com.review.userservice.application;

import com.review.common.dto.request.user.GetUserRes;
import com.review.common.dto.response.ApiResponse;

import java.util.List;
import java.util.UUID;

public interface UserService {

    ApiResponse<GetUserRes> getUserProfile(UUID userId);

    ApiResponse<List<GetUserRes>> getUsersProfile(List<UUID> userIds);


}
