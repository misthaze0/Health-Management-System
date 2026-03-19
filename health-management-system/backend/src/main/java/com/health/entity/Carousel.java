package com.health.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 轮播图实体类（简化版）
 * 对应数据库表: carousel
 * 只保留核心字段：标题、内容、排序、图片URL
 *
 * @author Health Management System
 * @since 1.0.0
 */
@Data
@TableName("carousel")
public class Carousel {

    /**
     * 轮播图ID，主键，自增
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 轮播图标题
     */
    private String title;

    /**
     * 轮播图内容/描述
     */
    private String content;

    /**
     * 轮播图图片URL
     */
    @TableField("image_url")
    private String imageUrl;

    /**
     * 排序值，越小越靠前
     */
    @TableField("sort_order")
    private Integer sortOrder;

    /**
     * 状态: 0-禁用, 1-启用
     */
    private Integer status;

    /**
     * 创建人ID
     */
    @TableField("created_by")
    private Long createdBy;

    /**
     * 创建时间，自动填充
     */
    @TableField(value = "create_time", fill = FieldFill.INSERT)
    private LocalDateTime createTime;

    /**
     * 更新时间，自动填充
     */
    @TableField(value = "update_time", fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
}
