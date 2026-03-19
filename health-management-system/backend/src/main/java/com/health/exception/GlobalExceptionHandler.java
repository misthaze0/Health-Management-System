package com.health.exception;

import com.health.vo.ResultVO;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import jakarta.servlet.http.HttpServletRequest;

/**
 * 全局异常处理器
 * 统一处理系统中抛出的异常，返回标准化的错误响应
 *
 * @author Health Management System
 * @since 1.0.0
 */
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    /**
     * 处理所有未捕获的异常
     */
    @ExceptionHandler(Exception.class)
    public ResultVO<Object> handleException(Exception e, HttpServletRequest request) {
        log.error("[GlobalExceptionHandler] ==================== 异常开始 ====================");
        log.error("[GlobalExceptionHandler] 请求路径: {}", request.getRequestURI());
        log.error("[GlobalExceptionHandler] 请求方法: {}", request.getMethod());
        log.error("[GlobalExceptionHandler] 异常类型: {}", e.getClass().getName());
        log.error("[GlobalExceptionHandler] 异常信息: {}", e.getMessage());
        log.error("[GlobalExceptionHandler] 异常堆栈:", e);
        log.error("[GlobalExceptionHandler] ==================== 异常结束 ====================");

        // 返回友好的错误信息
        String errorMessage = "服务器内部错误: " + (e.getMessage() != null ? e.getMessage() : "未知错误");
        return ResultVO.error(errorMessage);
    }

    /**
     * 处理运行时异常
     */
    @ExceptionHandler(RuntimeException.class)
    public ResultVO<Object> handleRuntimeException(RuntimeException e, HttpServletRequest request) {
        log.error("[GlobalExceptionHandler] ==================== 运行时异常开始 ====================");
        log.error("[GlobalExceptionHandler] 请求路径: {}", request.getRequestURI());
        log.error("[GlobalExceptionHandler] 异常类型: {}", e.getClass().getName());
        log.error("[GlobalExceptionHandler] 异常信息: {}", e.getMessage());
        log.error("[GlobalExceptionHandler] 异常堆栈:", e);
        log.error("[GlobalExceptionHandler] ==================== 运行时异常结束 ====================");

        return ResultVO.error("运行时错误: " + (e.getMessage() != null ? e.getMessage() : "未知错误"));
    }

    /**
     * 处理空指针异常
     */
    @ExceptionHandler(NullPointerException.class)
    public ResultVO<Object> handleNullPointerException(NullPointerException e, HttpServletRequest request) {
        log.error("[GlobalExceptionHandler] ==================== 空指针异常 ====================");
        log.error("[GlobalExceptionHandler] 请求路径: {}", request.getRequestURI());
        log.error("[GlobalExceptionHandler] 异常信息: {}", e.getMessage());
        log.error("[GlobalExceptionHandler] 异常堆栈:", e);
        log.error("[GlobalExceptionHandler] ==================== 空指针异常结束 ====================");

        return ResultVO.error("服务器错误: 空指针异常");
    }
}
