package com.health.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

import com.health.security.JwtAuthenticationFilter;

/**
 * Spring Security 配置类
 */
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public BCryptPasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http, JwtAuthenticationFilter jwtAuthenticationFilter) throws Exception {
        http
            // 禁用 CSRF
            .csrf(csrf -> csrf.disable())
            
            // 配置授权规则 - 注意顺序：先配置permitAll，最后配置authenticated
            .authorizeHttpRequests(auth -> auth
                // 1. 静态资源 - 上传的图片文件（最高优先级）
                .requestMatchers("/uploads/**", "/api/uploads/**").permitAll()
                // 2. 公开访问的接口
                .requestMatchers("/auth/login", "/auth/register").permitAll()
                // 3. 文章公开接口
                .requestMatchers("/api/articles", "/api/articles/**").permitAll()
                // 4. 医院/体检机构公开接口
                .requestMatchers("/api/hospitals", "/api/hospitals/**").permitAll()
                // 5. Swagger 文档
                .requestMatchers("/swagger-ui/**", "/v3/api-docs/**").permitAll()
                // 6. 健康检查
                .requestMatchers("/actuator/**").permitAll()
                // 7. 其他所有请求需要认证
                .anyRequest().authenticated()
            )
            
            // 无状态会话（使用 JWT）
            .sessionManagement(session -> 
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            
            // 添加 JWT 过滤器
            .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class)
            
            // 配置HTTP头 - 允许iframe嵌入（用于PDF预览）
            .headers(headers -> headers
                .frameOptions(frameOptions -> frameOptions.sameOrigin())
            );

        return http.build();
    }
}
