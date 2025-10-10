package com.review.common.shared;

public abstract class BaseException extends RuntimeException {
    private final int httpStatus;

    protected BaseException(String message, int httpStatus) {
        super(message);
        this.httpStatus = httpStatus;
    }

    public static BaseException create(String message, int httpStatus) {
        return new BaseException(message, httpStatus) {
        };
    }

    public int getHttpStatus() {
        return httpStatus;
    }
}