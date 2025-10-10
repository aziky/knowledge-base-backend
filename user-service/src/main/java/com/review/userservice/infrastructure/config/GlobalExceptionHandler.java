package com.review.userservice.infrastructure.config;

import com.review.common.dto.response.ApiResponse;
import feign.FeignException;
import jakarta.persistence.EntityNotFoundException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.nio.file.AccessDeniedException;

@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {


    @ExceptionHandler(EntityNotFoundException.class)
    public ResponseEntity<ApiResponse<Object>> handleEntityNotFound(EntityNotFoundException ex) {
        log.error("Entity not found: {}", ex.getMessage());
        return ResponseEntity.status(404).body(ApiResponse.notFound("Resource not found"));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<Object>> handleValidationException(MethodArgumentNotValidException ex) {
        String errorMessage = ex.getBindingResult().getFieldError().getDefaultMessage();
        log.warn("Validation failed: {}", errorMessage);
        return ResponseEntity.badRequest().body(ApiResponse.badRequest(errorMessage));
    }

    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ResponseEntity<ApiResponse<Object>> handleBadRequest(HttpMessageNotReadableException ex) {
        log.warn("Invalid request format: {}", ex.getMessage());
        return ResponseEntity.badRequest().body(ApiResponse.badRequest("Malformed JSON or invalid request body"));
    }

    @ExceptionHandler(MissingServletRequestParameterException.class)
    public ResponseEntity<ApiResponse<Object>> handleMissingParam(MissingServletRequestParameterException ex) {
        String message = String.format("Missing request parameter: %s", ex.getParameterName());
        log.warn(message);
        return ResponseEntity.badRequest().body(ApiResponse.badRequest(message));
    }

    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ApiResponse<Object>> handleAccessDenied(AccessDeniedException ex) {
        log.warn("Access denied: {}", ex.getMessage());
        return ResponseEntity.status(401).body(ApiResponse.unauthorized("You are not authorized to perform this action"));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Object>> handleGenericException(Exception ex) {
        log.error("Unhandled exception: ", ex);
        return ResponseEntity.status(500).body(ApiResponse.internalError());
    }

    @ExceptionHandler(FeignException.class)
    public ResponseEntity<ApiResponse<Object>> handleGenericFeignException(FeignException ex) {
        log.error("Feign exception occurred: {}", ex.getMessage());
        if (ex instanceof FeignException.BadRequest) {
            return ResponseEntity.badRequest().body(ApiResponse.badRequest("Invalid request"));
        }
        if (ex instanceof FeignException.NotFound) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(ApiResponse.notFound("Resource not found"));
        }
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResponse.internalError());
    }



}
