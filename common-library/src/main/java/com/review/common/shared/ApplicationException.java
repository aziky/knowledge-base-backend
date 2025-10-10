package com.review.common.shared;


public final class ApplicationException {

    public static class DuplicateInformation extends BaseException {
        public DuplicateInformation(String message) {
            super(message, 404);
        }
    }


    private ApplicationException() {
        throw new UnsupportedOperationException("Utility class cannot be instantiated");
    }
}