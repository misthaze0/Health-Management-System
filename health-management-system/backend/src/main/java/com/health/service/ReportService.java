package com.health.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.health.entity.ExamIndicator;
import com.health.entity.PhysicalExamReport;
import com.health.mapper.ExamIndicatorMapper;
import com.health.mapper.PhysicalExamReportMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.stream.Collectors;
import java.util.*;

/**
 * 报告解读服务类
 * 提供体检报告的查询和管理功能
 * AI解读功能已移植到Python AI服务
 *
 * @author Health Management System
 * @since 1.0.0
 */
@Slf4j
@Service
public class ReportService {

    @Autowired
    private PhysicalExamReportMapper reportMapper;

    @Autowired
    private ExamIndicatorMapper indicatorMapper;

    @Value("${file.upload.path:uploads/reports}")
    private String uploadPath;

    /**
     * 获取用户报告列表
     *
     * @param userId 用户ID
     * @return 报告列表
     */
    public List<Map<String, Object>> getReportList(Long userId) {
        List<PhysicalExamReport> reports = reportMapper.selectList(
                new QueryWrapper<PhysicalExamReport>().eq("user_id", userId)
                        .orderByDesc("exam_date")
        );

        return reports.stream().map(report -> {
            Map<String, Object> map = new HashMap<>();
            map.put("id", report.getId());
            map.put("title", report.getCenterName());
            map.put("centerName", report.getCenterName());
            map.put("hospitalName", report.getCenterName());
            map.put("examDate", report.getExamDate());
            map.put("status", report.getStatus());
            map.put("aiAnalysis", report.getAiAnalysis());

            // 获取指标统计
            List<ExamIndicator> indicators = indicatorMapper.selectList(
                    new QueryWrapper<ExamIndicator>().eq("report_id", report.getId())
            );

            Map<String, Object> summary = new HashMap<>();
            summary.put("normal", indicators.stream().filter(i -> i.getStatus() == 0).count());
            summary.put("warning", indicators.stream().filter(i -> i.getStatus() == 2).count());
            summary.put("abnormal", indicators.stream().filter(i -> i.getStatus() == 1).count());
            map.put("indicatorSummary", summary);

            return map;
        }).collect(Collectors.toList());
    }

    /**
     * 获取报告详情及指标
     *
     * @param userId   用户ID
     * @param reportId 报告ID
     * @return 报告详情和指标列表
     */
    public Map<String, Object> getReportDetail(Long userId, Long reportId) {
        PhysicalExamReport report = reportMapper.selectById(reportId);
        if (report == null || !report.getUserId().equals(userId)) {
            throw new RuntimeException("报告不存在");
        }

        List<ExamIndicator> indicators = indicatorMapper.selectList(
                new QueryWrapper<ExamIndicator>().eq("report_id", reportId)
        );

        Map<String, Object> result = new HashMap<>();
        result.put("report", report);
        result.put("indicators", indicators);
        return result;
    }

    /**
     * 更新报告的AI分析结果
     * 由Python AI服务调用此接口保存分析结果
     *
     * @param userId    用户ID
     * @param reportId  报告ID
     * @param analysis  AI分析结果
     * @return 是否更新成功
     */
    public boolean updateReportAnalysis(Long userId, Long reportId, String analysis) {
        PhysicalExamReport report = reportMapper.selectById(reportId);
        if (report == null || !report.getUserId().equals(userId)) {
            throw new RuntimeException("报告不存在");
        }

        report.setAiAnalysis(analysis);
        int result = reportMapper.updateById(report);

        if (result > 0) {
            log.info("报告AI分析已更新 - userId: {}, reportId: {}", userId, reportId);
            return true;
        }
        return false;
    }

    /**
     * 上传体检报告
     *
     * @param userId      用户ID
     * @param file        上传的文件
     * @param title       报告标题
     * @param examDate    体检日期
     * @param centerName  体检机构
     * @return 上传结果
     */
    public Map<String, Object> uploadReport(Long userId, MultipartFile file, String title, String examDate, String centerName) {
        try {
            // 创建上传目录
            Path uploadDir = Paths.get(uploadPath);
            if (!Files.exists(uploadDir)) {
                Files.createDirectories(uploadDir);
            }

            // 生成唯一文件名
            String originalFilename = file.getOriginalFilename();
            String extension = originalFilename != null ? originalFilename.substring(originalFilename.lastIndexOf(".")) : ".pdf";
            String newFilename = UUID.randomUUID().toString() + extension;
            Path filePath = uploadDir.resolve(newFilename);

            // 保存文件
            file.transferTo(filePath.toFile());
            log.info("文件已保存: {}", filePath);

            // 创建报告记录 - 只存相对路径，类似轮播图
            // 数据库存: report/xxx.pdf
            // 前端访问: /api/uploads/report/xxx.pdf
            String relativePath = "report/" + newFilename;

            PhysicalExamReport report = new PhysicalExamReport();
            report.setUserId(userId);
            report.setCenterName(centerName != null ? centerName : title);
            report.setExamDate(LocalDate.parse(examDate));
            report.setReportNo(newFilename);
            report.setFileUrl(relativePath);  // 只存相对路径
            report.setStatus(1); // 1-待解读
            report.setCreateTime(LocalDateTime.now());
            report.setUpdateTime(LocalDateTime.now());

            reportMapper.insert(report);
            log.info("报告记录已创建 - userId: {}, reportId: {}", userId, report.getId());

            Map<String, Object> result = new HashMap<>();
            result.put("reportId", report.getId());
            result.put("fileUrl", relativePath);
            result.put("message", "上传成功");
            return result;

        } catch (IOException e) {
            log.error("文件上传失败: {}", e.getMessage());
            throw new RuntimeException("文件上传失败: " + e.getMessage());
        }
    }

    /**
     * 删除报告
     *
     * @param userId   用户ID
     * @param reportId 报告ID
     */
    public void deleteReport(Long userId, Long reportId) {
        PhysicalExamReport report = reportMapper.selectById(reportId);
        if (report == null || !report.getUserId().equals(userId)) {
            throw new RuntimeException("报告不存在");
        }

        // 删除关联的指标
        indicatorMapper.delete(new QueryWrapper<ExamIndicator>().eq("report_id", reportId));

        // 删除文件
        try {
            String fileUrl = report.getFileUrl();
            if (fileUrl != null && !fileUrl.isEmpty()) {
                Path filePath = Paths.get(fileUrl);
                Files.deleteIfExists(filePath);
                log.info("文件已删除: {}", filePath);
            }
        } catch (IOException e) {
            log.warn("删除文件失败: {}", e.getMessage());
        }

        // 删除报告记录
        reportMapper.deleteById(reportId);
        log.info("报告已删除 - userId: {}, reportId: {}", userId, reportId);
    }

    /**
     * 保存AI分析结果
     *
     * @param userId       用户ID
     * @param reportId     报告ID
     * @param analysisData 分析数据
     */
    public void saveAnalysisResult(Long userId, Long reportId, Map<String, Object> analysisData) {
        PhysicalExamReport report = reportMapper.selectById(reportId);
        if (report == null || !report.getUserId().equals(userId)) {
            throw new RuntimeException("报告不存在");
        }

        // 更新报告状态和分析结果
        report.setStatus(3); // 3-已完成
        report.setAiAnalysis((String) analysisData.get("analysis"));
        report.setOverallResult((String) analysisData.get("summary"));
        report.setOverallSuggestion((String) analysisData.get("suggestions"));
        report.setUpdateTime(LocalDateTime.now());

        reportMapper.updateById(report);
        log.info("AI分析结果已保存 - userId: {}, reportId: {}", userId, reportId);
    }
}
