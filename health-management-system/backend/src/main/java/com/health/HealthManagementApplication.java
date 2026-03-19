package com.health;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 健康管理系统主启动类
 * 基于Kimi AI技术的全流程健康管理平台
 */
@SpringBootApplication
@MapperScan({"com.health.mapper", "com.health.repository"})
public class HealthManagementApplication {

    public static void main(String[] args) {
        SpringApplication.run(HealthManagementApplication.class, args);
        System.out.println("========================================");
        System.out.println("健康管理系统启动成功！");
        System.out.println("Health Management System Started Successfully!");
        System.out.println("========================================");
    }
}
