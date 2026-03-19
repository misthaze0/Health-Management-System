package com.health.utils;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;
import java.io.File;

/**
 * 文件工具类
 * 提供文件删除等通用功能
 */
@Slf4j
@Component
public class FileUtil {

    /**
     * 文件上传绝对路径
     */
    private static String UPLOAD_PATH;

    @Value("${file.upload.path:d:/基于KIMI的全流程健康管理系统/health-management-system/backend/uploads/}")
    private String uploadPath;

    @PostConstruct
    public void init() {
        UPLOAD_PATH = uploadPath;
        // 确保路径以/结尾
        if (!UPLOAD_PATH.endsWith("/") && !UPLOAD_PATH.endsWith("\\")) {
            UPLOAD_PATH += "/";
        }
        log.info("文件工具类初始化完成，上传路径: {}", UPLOAD_PATH);
    }

    /**
     * 删除上传的文件
     * 根据数据库存储的相对路径删除物理文件
     *
     * @param relativePath 相对路径，如 avatar/xxx.jpg, articles/2024/01/xxx.jpg
     * @return 是否删除成功
     */
    public static boolean deleteUploadFile(String relativePath) {
        if (relativePath == null || relativePath.trim().isEmpty()) {
            log.warn("删除文件失败：路径为空");
            return false;
        }

        try {
            // 处理可能包含 /uploads/ 或 /api/uploads/ 前缀的路径
            String cleanPath = cleanPath(relativePath);

            // 构建完整文件路径
            String absoluteFilePath = UPLOAD_PATH + cleanPath;
            File file = new File(absoluteFilePath);

            if (file.exists()) {
                boolean deleted = file.delete();
                if (deleted) {
                    log.info("文件删除成功: {}", absoluteFilePath);
                } else {
                    log.warn("文件删除失败: {}", absoluteFilePath);
                }
                return deleted;
            } else {
                log.warn("文件不存在，无需删除: {}", absoluteFilePath);
                return false;
            }
        } catch (Exception e) {
            log.error("删除文件时发生错误: {}", relativePath, e);
            return false;
        }
    }

    /**
     * 清理路径，移除URL前缀
     *
     * @param path 原始路径
     * @return 清理后的相对路径
     */
    private static String cleanPath(String path) {
        if (path == null) {
            return "";
        }

        // 移除各种可能的前缀
        String[] prefixesToRemove = {
            "/api/uploads/",
            "/uploads/",
            "api/uploads/",
            "uploads/",
            "/api/",
            "http://",
            "https://"
        };

        String cleanPath = path.trim();
        for (String prefix : prefixesToRemove) {
            if (cleanPath.startsWith(prefix)) {
                cleanPath = cleanPath.substring(prefix.length());
                break;
            }
        }

        // 移除开头的/
        while (cleanPath.startsWith("/")) {
            cleanPath = cleanPath.substring(1);
        }

        return cleanPath;
    }

    /**
     * 检查文件是否存在
     *
     * @param relativePath 相对路径
     * @return 是否存在
     */
    public static boolean exists(String relativePath) {
        if (relativePath == null || relativePath.trim().isEmpty()) {
            return false;
        }

        try {
            String cleanPath = cleanPath(relativePath);
            String absoluteFilePath = UPLOAD_PATH + cleanPath;
            File file = new File(absoluteFilePath);
            return file.exists();
        } catch (Exception e) {
            log.error("检查文件是否存在时发生错误: {}", relativePath, e);
            return false;
        }
    }

    /**
     * 获取文件的绝对路径
     *
     * @param relativePath 相对路径
     * @return 绝对路径
     */
    public static String getAbsolutePath(String relativePath) {
        if (relativePath == null) {
            return null;
        }
        String cleanPath = cleanPath(relativePath);
        return UPLOAD_PATH + cleanPath;
    }
}
