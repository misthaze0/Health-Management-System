package com.health.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;
import java.time.LocalDate;

/**
 * 体检预约DTO
 */
@Data
public class PhysicalExamAppointmentDTO {
    
    private Long id;
    
    @NotNull(message = "预约日期不能为空")
    private LocalDate appointmentDate;
    
    private String appointmentTime;
    
    private String examPackage;
    
    private Integer status;
    
    private String notes;
}
