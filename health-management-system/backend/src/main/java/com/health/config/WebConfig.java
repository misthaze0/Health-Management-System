package com.health.config;

import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.io.File;

/**
 * Web配置类
 * 配置静态资源映射，支持上传文件访问
 *
 * @author Health Management System
 * @since 1.0.0
 */
@Slf4j
@Configuration
public class WebConfig implements WebMvcConfigurer {

    /**
     * 文件上传绝对路径 - 与 AdminController 保持一致
     * 注意：使用 backend/uploads 目录，这是实际存储文件的位置
     */
    private static final String ABSOLUTE_UPLOAD_PATH = "d:/基于KIMI的全流程健康管理系统/health-management-system/backend/uploads/";

    /**
     * 报告文件上传路径
     */
    private static final String REPORT_UPLOAD_PATH = "d:/基于KIMI的全流程健康管理系统/health-management-system/backend/uploads/report/";

    /**
     * URL前缀 - 用于访问上传的文件
     * 注意：由于 server.servlet.context-path=/api，这里的 /uploads/ 会被映射为 /api/uploads/
     */
    private static final String UPLOAD_URL_PREFIX = "/uploads/";

    private String resourceUploadPath;

    @PostConstruct
    public void init() {
        // 转换Windows路径分隔符为Unix风格，并添加 file:/// 前缀（Spring资源定位格式）
        resourceUploadPath = ABSOLUTE_UPLOAD_PATH.replace("\\", "/");
        if (!resourceUploadPath.startsWith("file:")) {
            resourceUploadPath = "file:///" + resourceUploadPath;
        }
        log.info("静态资源映射配置: urlPrefix={}, resourceLocation={}", UPLOAD_URL_PREFIX, resourceUploadPath);
    }

    /**
     * 配置静态资源映射
     * 将上传的文件映射为可访问的URL
     *
     * @param registry 资源处理器注册表
     */
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        // 上传文件资源映射
        // 例如：/api/uploads/carousels/2026/03/14/xxx.jpg -> file:///d:/.../uploads/carousels/2026/03/14/xxx.jpg
        registry.addResourceHandler(UPLOAD_URL_PREFIX + "**")
                .addResourceLocations(resourceUploadPath);

        // 报告文件资源映射 - /api/uploads/report/**
        String reportResourcePath = REPORT_UPLOAD_PATH.replace("\\", "/");
        if (!reportResourcePath.startsWith("file:")) {
            reportResourcePath = "file:///" + reportResourcePath;
        }
        registry.addResourceHandler("/uploads/report/**")
                .addResourceLocations(reportResourcePath);
        log.info("报告文件资源映射: /uploads/report/** -> {}", reportResourcePath);
    }
}
