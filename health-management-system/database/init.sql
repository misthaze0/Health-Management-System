-- ========================================================
-- 健康管理系统数据库初始化脚本
-- ========================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS health_management 
DEFAULT CHARACTER SET utf8mb4 
DEFAULT COLLATE utf8mb4_unicode_ci;

USE health_management;

-- ========================================================
-- 1. 用户相关表
-- ========================================================

-- 用户表
CREATE TABLE IF NOT EXISTS sys_user (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '用户ID，主键',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    password VARCHAR(100) NOT NULL COMMENT '密码',
    email VARCHAR(100) NULL COMMENT '邮箱',
    phone VARCHAR(20) NULL COMMENT '手机号',
    avatar VARCHAR(255) NULL COMMENT '头像URL',
    real_name VARCHAR(50) NULL COMMENT '真实姓名',
    gender TINYINT DEFAULT 0 COMMENT '性别: 0-未知, 1-男, 2-女',
    birthday DATE NULL COMMENT '出生日期',
    id_card VARCHAR(18) NULL COMMENT '身份证号',
    status TINYINT DEFAULT 1 COMMENT '状态: 0-禁用, 1-启用',
    deleted TINYINT DEFAULT 0 COMMENT '删除标记: 0-未删除, 1-已删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_username (username),
    UNIQUE KEY uk_email (email),
    UNIQUE KEY uk_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 角色表
CREATE TABLE IF NOT EXISTS sys_role (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '角色ID，主键',
    role_name VARCHAR(50) NOT NULL COMMENT '角色名称',
    role_code VARCHAR(50) NOT NULL COMMENT '角色编码',
    description VARCHAR(255) NULL COMMENT '描述',
    status TINYINT DEFAULT 1 COMMENT '状态: 0-禁用, 1-启用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_role_code (role_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表';

-- 用户角色关联表
CREATE TABLE IF NOT EXISTS sys_user_role (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    role_id BIGINT NOT NULL COMMENT '角色ID',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_user_role (user_id, role_id),
    KEY idx_user_id (user_id),
    KEY idx_role_id (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户角色关联表';

-- ========================================================
-- 2. AI对话相关表
-- ========================================================

-- AI对话历史表
CREATE TABLE IF NOT EXISTS ai_chat_history (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    session_id VARCHAR(50) NULL COMMENT '会话ID',
    message_role TINYINT NOT NULL COMMENT '角色: 1-用户, 2-AI',
    message_content TEXT NOT NULL COMMENT '消息内容',
    tokens_used INT NULL COMMENT '使用的token数',
    response_time INT NULL COMMENT '响应时间(ms)',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_user_id (user_id),
    KEY idx_session_id (session_id),
    KEY idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI对话历史表';

-- ========================================================
-- 3. 血糖管理相关表
-- ========================================================

-- 血糖记录表
CREATE TABLE IF NOT EXISTS blood_sugar_record (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    measure_time DATETIME NOT NULL COMMENT '测量时间',
    glucose_value DECIMAL(4,2) NOT NULL COMMENT '血糖值(mmol/L)',
    measure_type TINYINT NOT NULL COMMENT '测量类型: 1-空腹, 2-餐后1h, 3-餐后2h, 4-随机',
    device_sn VARCHAR(50) NULL COMMENT '设备序列号',
    notes VARCHAR(500) NULL COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_user_id (user_id),
    KEY idx_measure_time (measure_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='血糖记录表';

-- ========================================================
-- 4. 体检管理相关表
-- ========================================================

-- 体检预约表
CREATE TABLE IF NOT EXISTS physical_exam_appointment (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    center_id BIGINT NULL COMMENT '体检中心ID',
    appointment_date DATE NOT NULL COMMENT '预约日期',
    appointment_time VARCHAR(20) NULL COMMENT '预约时间段',
    exam_package VARCHAR(100) NULL COMMENT '体检套餐',
    status TINYINT DEFAULT 0 COMMENT '状态: 0-待确认, 1-已确认, 2-已完成, 3-已取消',
    notes VARCHAR(500) NULL COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    KEY idx_user_id (user_id),
    KEY idx_appointment_date (appointment_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='体检预约表';

-- 体检报告表
CREATE TABLE IF NOT EXISTS physical_exam_report (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    appointment_id BIGINT NULL COMMENT '预约ID',
    exam_date DATE NOT NULL COMMENT '体检日期',
    center_name VARCHAR(100) NULL COMMENT '体检中心',
    report_no VARCHAR(50) NULL COMMENT '报告编号',
    overall_result TEXT NULL COMMENT '总体结果',
    overall_suggestion TEXT NULL COMMENT '总体建议',
    ai_analysis TEXT NULL COMMENT 'AI分析报告',
    status TINYINT DEFAULT 0 COMMENT '状态: 0-待上传, 1-已上传, 2-分析中, 3-已完成',
    file_url VARCHAR(255) NULL COMMENT '报告文件URL',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    KEY idx_user_id (user_id),
    KEY idx_exam_date (exam_date),
    KEY idx_appointment_id (appointment_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='体检报告表';

-- 体检指标表
CREATE TABLE IF NOT EXISTS exam_indicator (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
    report_id BIGINT NOT NULL COMMENT '报告ID',
    indicator_code VARCHAR(50) NULL COMMENT '指标编码',
    indicator_name VARCHAR(100) NOT NULL COMMENT '指标名称',
    indicator_value VARCHAR(50) NULL COMMENT '指标值',
    unit VARCHAR(20) NULL COMMENT '单位',
    reference_range VARCHAR(100) NULL COMMENT '参考范围',
    status TINYINT NULL COMMENT '状态: 0-正常, 1-偏高, 2-偏低, 3-异常',
    ai_interpretation TEXT NULL COMMENT 'AI解读',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_report_id (report_id),
    KEY idx_indicator_code (indicator_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='体检指标表';

-- ========================================================-- 5. 健康管理相关表-- ========================================================

-- 健康记录表
CREATE TABLE IF NOT EXISTS health_record (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    metric_type VARCHAR(50) NOT NULL COMMENT '指标类型: resting_heart_rate-静息心率, spo2-血氧, hrv-心率变异性, sleep_efficiency-睡眠效率, deep_sleep-深睡占比, respiratory_rate-呼吸频率, night_hr_variability-夜间心率波动, steps-步数, calories-卡路里, exercise_duration-运动时长',
    metric_value DECIMAL(10,2) NOT NULL COMMENT '指标值',
    record_date DATE NOT NULL COMMENT '记录日期',
    notes VARCHAR(500) NULL COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_user_id (user_id),
    KEY idx_metric_type (metric_type),
    KEY idx_record_date (record_date),
    KEY idx_user_metric_date (user_id, metric_type, record_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='健康记录表';

-- ========================================================-- 6. 健康文章管理表-- ========================================================

-- 健康文章表
CREATE TABLE IF NOT EXISTS health_articles (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '文章ID，主键',
    title VARCHAR(200) NOT NULL COMMENT '文章标题',
    summary TEXT NULL COMMENT '文章摘要',
    content LONGTEXT NULL COMMENT '文章内容',
    tag VARCHAR(50) NULL COMMENT '标签',
    tag_type VARCHAR(20) NULL COMMENT '标签类型: success/warning/danger/info',
    icon VARCHAR(50) NULL COMMENT '图标名称',
    gradient VARCHAR(200) NULL COMMENT '渐变色背景',
    image_url VARCHAR(500) NULL COMMENT '封面图片URL',
    views INT DEFAULT 0 COMMENT '浏览量',
    sort_order INT DEFAULT 0 COMMENT '排序值，越小越靠前',
    status TINYINT DEFAULT 1 COMMENT '状态: 0-禁用, 1-启用',
    created_by BIGINT NULL COMMENT '创建人ID',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    KEY idx_status (status),
    KEY idx_sort_order (sort_order),
    KEY idx_created_by (created_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='健康文章表';

-- 轮播图表
CREATE TABLE IF NOT EXISTS carousel (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '轮播图ID，主键',
    title VARCHAR(200) NOT NULL COMMENT '轮播图标题',
    content TEXT NULL COMMENT '轮播图内容/描述',
    image_url VARCHAR(500) NULL COMMENT '封面图片URL',
    sort_order INT DEFAULT 0 COMMENT '排序值，越小越靠前',
    status TINYINT DEFAULT 1 COMMENT '状态: 0-禁用, 1-启用',
    created_by BIGINT NULL COMMENT '创建人ID',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    KEY idx_status (status),
    KEY idx_sort_order (sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='轮播图表';

-- ========================================================
-- 7. 插入初始数据
-- ========================================================

-- 插入默认角色
INSERT INTO sys_role (id, role_name, role_code, description, status) VALUES
(1, '超级管理员', 'ROLE_ADMIN', '系统超级管理员，拥有所有权限', 1),
(2, '普通用户', 'ROLE_USER', '普通用户角色', 1)
ON DUPLICATE KEY UPDATE role_name = VALUES(role_name);

-- 插入默认管理员账号 (密码: admin123)
INSERT INTO sys_user (id, username, password, email, phone, real_name, gender, status) VALUES
(1, 'admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EO', 'admin@health.com', '13800138000', '管理员', 1, 1)
ON DUPLICATE KEY UPDATE username = VALUES(username);

-- 关联管理员角色
INSERT INTO sys_user_role (user_id, role_id) VALUES
(1, 1)
ON DUPLICATE KEY UPDATE user_id = VALUES(user_id);

-- 插入示例健康文章
INSERT INTO health_articles (id, title, summary, content, tag, tag_type, icon, views, status, created_by) VALUES
(1, '高血压患者的饮食指南', '详细介绍高血压患者应该如何合理饮食，控制血压。', '高血压患者的饮食指南内容...', '饮食', 'success', 'Food', 100, 1, 1),
(2, '糖尿病的早期症状', '了解糖尿病的早期症状，及时发现并治疗。', '糖尿病的早期症状内容...', '疾病', 'warning', 'FirstAidKit', 150, 1, 1),
(3, '科学运动指南', '如何科学运动，保持身体健康。', '科学运动指南内容...', '运动', 'primary', 'Basketball', 80, 1, 1)
ON DUPLICATE KEY UPDATE title = VALUES(title);

-- 插入示例轮播图
-- 注意：图片路径使用一级目录结构 /uploads/carousel/
INSERT INTO carousel (id, title, content, image_url, sort_order, status, created_by) VALUES
(1, '健康管理系统上线', '欢迎使用全新的健康管理系统', '/uploads/carousel/banner1.jpg', 1, 1, 1),
(2, 'AI智能健康助手', 'AI技术助力健康管理', '/uploads/carousel/banner2.jpg', 2, 1, 1)
ON DUPLICATE KEY UPDATE title = VALUES(title);

-- ========================================================
-- 8. 创建视图（可选）
-- ========================================================

-- 用户健康概览视图
CREATE OR REPLACE VIEW v_user_health_overview AS
SELECT 
    u.id AS user_id,
    u.username,
    u.real_name,
    u.gender,
    u.birthday,
    COUNT(DISTINCT bsr.id) AS blood_sugar_record_count,
    COUNT(DISTINCT pear.id) AS exam_appointment_count,
    COUNT(DISTINCT per.id) AS exam_report_count,
    COUNT(DISTINCT hr.id) AS health_record_count
FROM sys_user u
LEFT JOIN blood_sugar_record bsr ON u.id = bsr.user_id AND bsr.deleted = 0
LEFT JOIN physical_exam_appointment pear ON u.id = pear.user_id
LEFT JOIN physical_exam_report per ON u.id = per.user_id
LEFT JOIN health_record hr ON u.id = hr.user_id
WHERE u.deleted = 0
GROUP BY u.id;

-- ========================================================
-- 完成
-- ========================================================

SELECT '数据库初始化完成！' AS message;
