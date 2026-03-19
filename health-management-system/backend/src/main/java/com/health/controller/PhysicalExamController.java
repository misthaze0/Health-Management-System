package com.health.controller;

import com.health.dto.PhysicalExamAppointmentDTO;
import com.health.entity.PhysicalExamReport;
import com.health.service.PhysicalExamService;
import com.health.vo.ResultVO;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 体检管理控制器
 */
@RestController
@RequestMapping("/physical-exam")
public class PhysicalExamController {
    
    @Autowired
    private PhysicalExamService physicalExamService;
    
    /**
     * 创建体检预约
     */
    @PostMapping("/appointments")
    public ResultVO<PhysicalExamAppointmentDTO> createAppointment(
            @RequestAttribute("userId") Long userId,
            @Valid @RequestBody PhysicalExamAppointmentDTO dto) {
        PhysicalExamAppointmentDTO appointment = physicalExamService.createAppointment(userId, dto);
        return ResultVO.success(appointment);
    }
    
    /**
     * 更新体检预约
     */
    @PutMapping("/appointments/{appointmentId}")
    public ResultVO<PhysicalExamAppointmentDTO> updateAppointment(
            @RequestAttribute("userId") Long userId,
            @PathVariable Long appointmentId,
            @Valid @RequestBody PhysicalExamAppointmentDTO dto) {
        PhysicalExamAppointmentDTO appointment = physicalExamService.updateAppointment(userId, appointmentId, dto);
        return ResultVO.success(appointment);
    }
    
    /**
     * 取消体检预约
     */
    @PutMapping("/appointments/{appointmentId}/cancel")
    public ResultVO<Void> cancelAppointment(
            @RequestAttribute("userId") Long userId,
            @PathVariable Long appointmentId) {
        physicalExamService.cancelAppointment(userId, appointmentId);
        return ResultVO.success();
    }
    
    /**
     * 获取体检预约列表
     */
    @GetMapping("/appointments")
    public ResultVO<List<PhysicalExamAppointmentDTO>> getAppointments(
            @RequestAttribute("userId") Long userId) {
        List<PhysicalExamAppointmentDTO> appointments = physicalExamService.getUserAppointments(userId);
        return ResultVO.success(appointments);
    }
    
    /**
     * 获取体检报告列表
     */
    @GetMapping("/reports")
    public ResultVO<List<PhysicalExamReport>> getReports(
            @RequestAttribute("userId") Long userId) {
        List<PhysicalExamReport> reports = physicalExamService.getUserReports(userId);
        return ResultVO.success(reports);
    }
    
    /**
     * 获取体检报告详情
     */
    @GetMapping("/reports/{reportId}")
    public ResultVO<PhysicalExamReport> getReport(
            @RequestAttribute("userId") Long userId,
            @PathVariable Long reportId) {
        PhysicalExamReport report = physicalExamService.getReportById(userId, reportId);
        return ResultVO.success(report);
    }
}
