package com.health.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 健康知识文章实体类
 * 对应数据库表: health_articles
 * 用于存储首页健康知识文章和轮播图内容
 *
 * @author Health Management System
 * @since 1.0.0
 */
@Data
@TableName("health_articles")
public class HealthArticle {

    /**
     * 文章ID，主键，自增
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 文章标题
     */
    private String title;

    /**
     * 文章摘要
     */
    private String summary;

    /**
     * 文章内容
     */
    private String content;

    /**
     * 标签
     */
    private String tag;

    /**
     * 标签类型: success/warning/danger/info
     */
    @TableField("tag_type")
    private String tagType;

    /**
     * 图标名称
     */
    private String icon;

    /**
     * 渐变色背景
     */
    private String gradient;

    /**
     * 封面图片URL
     */
    @TableField("image_url")
    private String imageUrl;

    /**
     * 浏览量
     */
    private Integer views;

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
