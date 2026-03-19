package com.health.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 医院/体检机构实体类
 */
@Data
@TableName("hospital")
public class Hospital {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    /**
     * 医院名称
     */
    private String name;
    
    /**
     * 医院地址
     */
    private String address;
    
    /**
     * 经度
     */
    private BigDecimal longitude;
    
    /**
     * 纬度
     */
    private BigDecimal latitude;
    
    /**
     * 联系电话
     */
    private String phone;
    
    /**
     * 医院评分
     */
    private BigDecimal rating;
    
    /**
     * 标签，逗号分隔
     */
    private String tags;
    
    /**
     * 特色服务，逗号分隔
     */
    private String features;
    
    /**
     * 价格范围
     */
    private String priceRange;
    
    /**
     * 是否推荐
     */
    private Boolean isRecommended;
    
    /**
     * 医院简介
     */
    private String description;
    
    /**
     * 营业时间
     */
    private String businessHours;
    
    /**
     * 图片URL
     */
    private String imageUrl;
    
    /**
     * 距离（公里），非持久化字段
     */
    @TableField(exist = false)
    private Double distance;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
    
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
}
