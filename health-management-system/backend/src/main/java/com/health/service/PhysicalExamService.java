package com.health.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.health.dto.PhysicalExamAppointmentDTO;
import com.health.entity.PhysicalExamAppointment;
import com.health.entity.PhysicalExamReport;
import com.health.mapper.PhysicalExamAppointmentMapper;
import com.health.mapper.PhysicalExamReportMapper;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

/**
 * 体检服务类
 */
@Service
public class PhysicalExamService {
    
    @Autowired
    private PhysicalExamAppointmentMapper appointmentMapper;
    
    @Autowired
    private PhysicalExamReportMapper reportMapper;
    
    // ============== 体检预约 ==============
    
    /**
     * 创建体检预约
     */
    public PhysicalExamAppointmentDTO createAppointment(Long userId, PhysicalExamAppointmentDTO dto) {
        PhysicalExamAppointment appointment = new PhysicalExamAppointment();
        BeanUtils.copyProperties(dto, appointment);
        appointment.setUserId(userId);
        appointment.setStatus(0); // 待确认
        
        appointmentMapper.insert(appointment);
        
        dto.setId(appointment.getId());
        dto.setStatus(0);
        return dto;
    }
    
    /**
     * 更新体检预约
     */
    public PhysicalExamAppointmentDTO updateAppointment(Long userId, Long appointmentId, PhysicalExamAppointmentDTO dto) {
        PhysicalExamAppointment appointment = appointmentMapper.selectById(appointmentId);
        if (appointment == null || !appointment.getUserId().equals(userId)) {
            throw new RuntimeException("预约不存在");
        }
        
        BeanUtils.copyProperties(dto, appointment);
        appointment.setId(appointmentId);
        appointment.setUserId(userId);
        
        appointmentMapper.updateById(appointment);
        
        dto.setId(appointmentId);
        return dto;
    }
    
    /**
     * 取消体检预约
     */
    public void cancelAppointment(Long userId, Long appointmentId) {
        PhysicalExamAppointment appointment = appointmentMapper.selectById(appointmentId);
        if (appointment == null || !appointment.getUserId().equals(userId)) {
            throw new RuntimeException("预约不存在");
        }
        
        appointment.setStatus(3); // 已取消
        appointmentMapper.updateById(appointment);
    }
    
    /**
     * 获取用户的体检预约列表
     */
    public List<PhysicalExamAppointmentDTO> getUserAppointments(Long userId) {
        List<PhysicalExamAppointment> appointments = appointmentMapper.selectList(
            new QueryWrapper<PhysicalExamAppointment>()
                .eq("user_id", userId)
                .orderByDesc("create_time")
        );
        
        return appointments.stream().map(this::convertAppointmentToDTO).collect(Collectors.toList());
    }
    
    // ============== 体检报告 ==============
    
    /**
     * 获取用户的体检报告列表
     */
    public List<PhysicalExamReport> getUserReports(Long userId) {
        return reportMapper.selectList(
            new QueryWrapper<PhysicalExamReport>()
                .eq("user_id", userId)
                .orderByDesc("exam_date")
        );
    }
    
    /**
     * 获取体检报告详情
     */
    public PhysicalExamReport getReportById(Long userId, Long reportId) {
        PhysicalExamReport report = reportMapper.selectById(reportId);
        if (report == null || !report.getUserId().equals(userId)) {
            throw new RuntimeException("报告不存在");
        }
        return report;
    }
    
    // ============== 转换方法 ==============
    
    private PhysicalExamAppointmentDTO convertAppointmentToDTO(PhysicalExamAppointment appointment) {
        PhysicalExamAppointmentDTO dto = new PhysicalExamAppointmentDTO();
        BeanUtils.copyProperties(appointment, dto);
        return dto;
    }
}
