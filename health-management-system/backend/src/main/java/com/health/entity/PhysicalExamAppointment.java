package com.health.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 体检预约实体类
 */
@Data
@TableName("physical_exam_appointment")
public class PhysicalExamAppointment {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private Long userId;
    
    private Long centerId;
    
    private LocalDate appointmentDate;
    
    private String appointmentTime;
    
    private String examPackage;
    
    private Integer status;
    
    private String notes;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
    
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
}
