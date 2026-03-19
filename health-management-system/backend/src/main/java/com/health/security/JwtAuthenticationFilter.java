package com.health.security;

import com.health.utils.JwtUtil;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.ArrayList;

/**
 * JWT认证过滤器
 */
@Slf4j
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    
    @Autowired
    private JwtUtil jwtUtil;
    
    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {

        // 获取请求路径
        String path = request.getRequestURI();
        String method = request.getMethod();
        log.info("[DEBUG JwtFilter] ==================== 请求开始 ====================");
        log.info("[DEBUG JwtFilter] 请求路径: {}", path);
        log.info("[DEBUG JwtFilter] 请求方法: {}", method);
        log.info("[DEBUG JwtFilter] QueryString: {}", request.getQueryString());

        // 放行登录和注册接口
        if (path.contains("/auth/login") || path.contains("/auth/register")) {
            log.info("[DEBUG JwtFilter] 放行登录/注册接口");
            filterChain.doFilter(request, response);
            return;
        }

        // 放行文章公开接口（轮播图、文章列表等）
        // 注意：不能匹配 /api/admin/articles/，那是管理员接口
        if (path.contains("/api/articles/") && !path.contains("/api/admin/")) {
            log.info("[DEBUG JwtFilter] 放行公开文章接口");
            // 设置匿名认证，让Spring Security通过
            UsernamePasswordAuthenticationToken anonymousAuth = 
                new UsernamePasswordAuthenticationToken("anonymous", null, new ArrayList<>());
            SecurityContextHolder.getContext().setAuthentication(anonymousAuth);
            filterChain.doFilter(request, response);
            return;
        }

        // 放行医院/体检机构公开接口
        if (path.contains("/api/hospitals")) {
            log.info("[DEBUG JwtFilter] 放行医院公开接口");
            UsernamePasswordAuthenticationToken anonymousAuth = 
                new UsernamePasswordAuthenticationToken("anonymous", null, new ArrayList<>());
            SecurityContextHolder.getContext().setAuthentication(anonymousAuth);
            filterChain.doFilter(request, response);
            return;
        }

        // 放行Swagger文档和API文档接口
        if (path.contains("/swagger-ui") || path.contains("/v3/api-docs") || path.contains("/swagger-resources")) {
            log.info("[DEBUG JwtFilter] 放行Swagger接口");
            filterChain.doFilter(request, response);
            return;
        }

        // 放行Actuator健康检查端点
        if (path.contains("/actuator/")) {
            log.info("[DEBUG JwtFilter] 放行Actuator接口");
            filterChain.doFilter(request, response);
            return;
        }

        // 放行静态资源 - 图片等上传文件
        // 注意：Spring Security配置已放行 /uploads/** 和 /api/uploads/**
        if (path.contains("/uploads/")) {
            log.info("[DEBUG JwtFilter] 放行静态资源: {}", path);
            filterChain.doFilter(request, response);
            return;
        }
        
        // 获取Authorization头
        String authHeader = request.getHeader("Authorization");
        log.info("[DEBUG JwtFilter] Authorization头: {}", authHeader != null ? "存在" : "不存在");
        
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);
            log.info("[DEBUG JwtFilter] Token: {}...", token.length() > 10 ? token.substring(0, 10) : token);
            
            // 验证Token
            if (jwtUtil.validateToken(token)) {
                // 获取用户ID并设置到请求属性中
                Long userId = jwtUtil.getUserIdFromToken(token);
                request.setAttribute("userId", userId);
                log.info("[DEBUG JwtFilter] Token验证成功, userId: {}", userId);
                
                // 设置SecurityContext，让Spring Security知道已认证
                UsernamePasswordAuthenticationToken authentication = 
                    new UsernamePasswordAuthenticationToken(userId, null, new ArrayList<>());
                SecurityContextHolder.getContext().setAuthentication(authentication);
            } else {
                log.warn("[DEBUG JwtFilter] Token验证失败");
                // Token 无效，返回 401
                response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                response.setContentType("application/json;charset=UTF-8");
                response.getWriter().write("{\"code\":401,\"message\":\"登录已过期，请重新登录\"}");
                return;
            }
        } else {
            log.warn("[DEBUG JwtFilter] 没有Authorization头，返回401");
            // 没有 Token，返回 401
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.setContentType("application/json;charset=UTF-8");
            response.getWriter().write("{\"code\":401,\"message\":\"请先登录\"}");
            return;
        }
        
        log.info("[DEBUG JwtFilter] 认证通过，继续处理请求");
        log.info("[DEBUG JwtFilter] ==================== 请求结束 ====================");
        filterChain.doFilter(request, response);
    }
}
