package com.health.controller;

import com.health.entity.PhysicalExamReport;
import com.health.service.ReportService;
import com.health.vo.ResultVO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.Map;

/**
 * 报告解读控制器
 * 提供体检报告查询功能
 * AI解读功能已移植到Python AI服务
 */
@RestController
@RequestMapping("/report")
public class ReportController {

    @Autowired
    private ReportService reportService;

    /**
     * 获取报告列表
     */
    @GetMapping("/list")
    public ResultVO<List<Map<String, Object>>> getReportList(
            @RequestAttribute("userId") Long userId) {
        List<Map<String, Object>> list = reportService.getReportList(userId);
        return ResultVO.success(list);
    }

    /**
     * 上传体检报告
     */
    @PostMapping("/upload")
    public ResultVO<Map<String, Object>> uploadReport(
            @RequestAttribute("userId") Long userId,
            @RequestParam("file") MultipartFile file,
            @RequestParam("title") String title,
            @RequestParam("examDate") String examDate,
            @RequestParam(value = "centerName", required = false) String centerName) {
        Map<String, Object> result = reportService.uploadReport(userId, file, title, examDate, centerName);
        return ResultVO.success(result);
    }

    /**
     * 获取报告详情
     */
    @GetMapping("/{reportId}")
    public ResultVO<Map<String, Object>> getReportDetail(
            @RequestAttribute("userId") Long userId,
            @PathVariable Long reportId) {
        Map<String, Object> detail = reportService.getReportDetail(userId, reportId);
        return ResultVO.success(detail);
    }

    /**
     * 删除报告
     */
    @DeleteMapping("/{reportId}")
    public ResultVO<Void> deleteReport(
            @RequestAttribute("userId") Long userId,
            @PathVariable Long reportId) {
        reportService.deleteReport(userId, reportId);
        return ResultVO.success();
    }

    /**
     * 保存AI分析结果
     * 由前端在AI服务完成分析后调用
     */
    @PostMapping("/{reportId}/analysis")
    public ResultVO<Void> saveAnalysisResult(
            @RequestAttribute("userId") Long userId,
            @PathVariable Long reportId,
            @RequestBody Map<String, Object> analysisData) {
        reportService.saveAnalysisResult(userId, reportId, analysisData);
        return ResultVO.success();
    }
}
