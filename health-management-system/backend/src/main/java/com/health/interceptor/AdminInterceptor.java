package com.health.interceptor;

import com.health.annotation.RequireAdmin;
import com.health.entity.User;
import com.health.mapper.UserMapper;
import com.health.utils.JwtUtil;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.method.HandlerMethod;
import org.springframework.web.servlet.HandlerInterceptor;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 管理员权限拦截器
 * 拦截带有 @RequireAdmin 注解的方法
 * 验证当前用户是否具有管理员权限
 *
 * @author Health Management System
 * @since 1.0.0
 */
@Slf4j
@Component
public class AdminInterceptor implements HandlerInterceptor {

    @Autowired
    private JwtUtil jwtUtil;

    @Autowired
    private UserMapper userMapper;

    private static final String AUTHORIZATION_HEADER = "Authorization";
    private static final String BEARER_PREFIX = "Bearer ";
    private static final String ADMIN_ROLE = "admin";

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        // 判断是否是方法处理器
        if (!(handler instanceof HandlerMethod)) {
            return true;
        }

        HandlerMethod handlerMethod = (HandlerMethod) handler;

        // 检查方法是否有 @RequireAdmin 注解
        RequireAdmin requireAdmin = handlerMethod.getMethodAnnotation(RequireAdmin.class);
        if (requireAdmin == null) {
            // 方法上没有注解，检查类上是否有注解
            requireAdmin = handlerMethod.getBeanType().getAnnotation(RequireAdmin.class);
        }

        // 没有 @RequireAdmin 注解，放行
        if (requireAdmin == null) {
            return true;
        }

        // 获取 JWT Token
        String token = extractToken(request);
        if (token == null) {
            log.warn("管理员接口访问失败: 未提供Token");
            writeErrorResponse(response, 401, "未登录或Token已过期");
            return false;
        }

        // 验证 Token 有效性
        if (!jwtUtil.validateToken(token)) {
            log.warn("管理员接口访问失败: Token无效");
            writeErrorResponse(response, 401, "Token无效或已过期");
            return false;
        }

        // 从 Token 中获取用户ID
        Long userId = jwtUtil.getUserIdFromToken(token);
        if (userId == null) {
            log.warn("管理员接口访问失败: 无法从Token获取用户ID");
            writeErrorResponse(response, 401, "Token解析失败");
            return false;
        }

        // 查询用户信息，检查是否为管理员
        User user = userMapper.selectById(userId);
        if (user == null) {
            log.warn("管理员接口访问失败: 用户不存在, userId={}", userId);
            writeErrorResponse(response, 401, "用户不存在");
            return false;
        }

        // 检查用户状态是否正常
        if (user.getStatus() == null || user.getStatus() != 1) {
            log.warn("管理员接口访问失败: 用户已被禁用, userId={}", userId);
            writeErrorResponse(response, 403, "用户已被禁用");
            return false;
        }

        // 查询用户角色，检查是否为管理员
        List<String> userRoles = userMapper.selectUserRoles(userId);
        if (userRoles == null || !userRoles.contains(ADMIN_ROLE)) {
            log.warn("管理员接口访问失败: 用户非管理员, userId={}, roles={}", userId, userRoles);
            writeErrorResponse(response, 403, "无管理员权限");
            return false;
        }

        // 将用户信息存入 request 属性，方便后续使用
        request.setAttribute("currentUserId", userId);
        request.setAttribute("currentUser", user);

        log.debug("管理员权限验证通过: userId={}", userId);
        return true;
    }

    /**
     * 从请求头中提取 JWT Token
     *
     * @param request HTTP请求
     * @return Token字符串，如果不存在则返回null
     */
    private String extractToken(HttpServletRequest request) {
        String bearerToken = request.getHeader(AUTHORIZATION_HEADER);
        if (bearerToken != null && bearerToken.startsWith(BEARER_PREFIX)) {
            return bearerToken.substring(BEARER_PREFIX.length());
        }
        return null;
    }

    /**
     * 写入错误响应
     *
     * @param response HTTP响应
     * @param code     错误码
     * @param message  错误消息
     * @throws IOException IO异常
     */
    private void writeErrorResponse(HttpServletResponse response, int code, String message) throws IOException {
        response.setStatus(code);
        response.setContentType("application/json;charset=UTF-8");

        Map<String, Object> result = new HashMap<>();
        result.put("code", code);
        result.put("message", message);
        result.put("data", null);

        ObjectMapper objectMapper = new ObjectMapper();
        response.getWriter().write(objectMapper.writeValueAsString(result));
    }
}
