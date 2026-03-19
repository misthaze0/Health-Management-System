package com.health.controller;

import com.health.dto.HealthRecordDTO;
import com.health.service.HealthService;
import com.health.vo.ResultVO;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

/**
 * 健康管理控制器
 * 提供健康记录的查询、添加、统计等功能
 *
 * @author Health Management System
 * @since 1.0.0
 */
@Slf4j
@RestController
@RequestMapping("/health")
@Tag(name = "健康管理", description = "健康记录管理相关接口")
public class HealthController {

    @Autowired
    private HealthService healthService;

    // ==================== 健康记录查询 ====================

    /**
     * 获取健康记录列表
     * 支持按指标类型和日期范围筛选
     *
     * @param userId     用户ID（从JWT中获取）
     * @param metricType 指标类型（可选）
     * @param startDate  开始日期（可选）
     * @param endDate    结束日期（可选）
     * @return 健康记录列表
     */
    @GetMapping("/records")
    @Operation(summary = "获取健康记录列表", description = "获取当前用户的健康记录列表，支持按指标类型和日期范围筛选")
    public ResultVO<List<HealthRecordDTO>> getHealthRecords(
            @RequestAttribute("userId") Long userId,
            @Parameter(description = "指标类型，如：blood_pressure、blood_sugar、weight、heart_rate")
            @RequestParam(required = false) String metricType,
            @Parameter(description = "开始日期，格式：yyyy-MM-dd")
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @Parameter(description = "结束日期，格式：yyyy-MM-dd")
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {

        log.info("获取健康记录列表, userId: {}, metricType: {}, startDate: {}, endDate: {}",
                userId, metricType, startDate, endDate);

        List<HealthRecordDTO> records = healthService.getUserHealthRecords(userId, metricType, startDate, endDate);
        return ResultVO.success(records);
    }

    /**
     * 获取健康统计数据
     * 统计指定时间范围内的指标平均值、最大值、最小值等
     *
     * @param userId     用户ID（从JWT中获取）
     * @param metricType 指标类型
     * @param startDate  开始日期
     * @param endDate    结束日期
     * @return 统计数据
     */
    @GetMapping("/statistics")
    @Operation(summary = "获取健康统计数据", description = "获取指定时间范围内的健康统计数据，包括平均值、最大值、最小值等")
    public ResultVO<Map<String, Object>> getHealthStatistics(
            @RequestAttribute("userId") Long userId,
            @Parameter(description = "指标类型，如：blood_pressure、blood_sugar、weight、heart_rate", required = true)
            @RequestParam String metricType,
            @Parameter(description = "开始日期，格式：yyyy-MM-dd", required = true)
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @Parameter(description = "结束日期，格式：yyyy-MM-dd", required = true)
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {

        log.info("获取健康统计数据, userId: {}, metricType: {}, startDate: {}, endDate: {}",
                userId, metricType, startDate, endDate);

        Map<String, Object> statistics = healthService.getHealthStatistics(userId, metricType, startDate, endDate);
        return ResultVO.success(statistics);
    }

    /**
     * 获取最新指标数据
     * 获取用户各项指标的最新记录
     *
     * @param userId 用户ID（从JWT中获取）
     * @return 最新指标数据列表
     */
    @GetMapping("/latest")
    @Operation(summary = "获取最新指标数据", description = "获取用户各项指标的最新记录")
    public ResultVO<List<HealthRecordDTO>> getLatestMetrics(
            @RequestAttribute("userId") Long userId) {

        log.info("获取最新指标数据, userId: {}", userId);

        List<HealthRecordDTO> records = healthService.getLatestMetrics(userId);
        return ResultVO.success(records);
    }

    /**
     * 获取指定指标类型的最新记录
     *
     * @param userId     用户ID（从JWT中获取）
     * @param metricType 指标类型
     * @return 最新健康记录
     */
    @GetMapping("/latest/{metricType}")
    @Operation(summary = "获取指定指标类型的最新记录", description = "获取用户指定指标类型的最新记录")
    public ResultVO<HealthRecordDTO> getLatestMetricByType(
            @RequestAttribute("userId") Long userId,
            @Parameter(description = "指标类型，如：blood_pressure、blood_sugar、weight、heart_rate", required = true)
            @PathVariable String metricType) {

        log.info("获取指定指标类型的最新记录, userId: {}, metricType: {}", userId, metricType);

        HealthRecordDTO record = healthService.getLatestMetricByType(userId, metricType);
        return ResultVO.success(record);
    }

    // ==================== 健康记录管理 ====================

    /**
     * 添加健康记录
     *
     * @param userId 用户ID（从JWT中获取）
     * @param dto    健康记录DTO
     * @return 添加后的健康记录
     */
    @PostMapping("/records")
    @Operation(summary = "添加健康记录", description = "添加新的健康记录")
    public ResultVO<HealthRecordDTO> addHealthRecord(
            @RequestAttribute("userId") Long userId,
            @Valid @RequestBody HealthRecordDTO dto) {

        log.info("添加健康记录, userId: {}, metricType: {}", userId, dto.getMetricType());

        HealthRecordDTO record = healthService.addHealthRecord(userId, dto);
        return ResultVO.success(record);
    }

    /**
     * 更新健康记录
     *
     * @param userId   用户ID（从JWT中获取）
     * @param recordId 记录ID
     * @param dto      健康记录DTO
     * @return 更新后的健康记录
     */
    @PutMapping("/records/{recordId}")
    @Operation(summary = "更新健康记录", description = "更新指定的健康记录")
    public ResultVO<HealthRecordDTO> updateHealthRecord(
            @RequestAttribute("userId") Long userId,
            @Parameter(description = "记录ID", required = true)
            @PathVariable Long recordId,
            @Valid @RequestBody HealthRecordDTO dto) {

        log.info("更新健康记录, userId: {}, recordId: {}", userId, recordId);

        HealthRecordDTO record = healthService.updateHealthRecord(userId, recordId, dto);
        return ResultVO.success(record);
    }

    /**
     * 删除健康记录
     *
     * @param userId   用户ID（从JWT中获取）
     * @param recordId 记录ID
     * @return 操作结果
     */
    @DeleteMapping("/records/{recordId}")
    @Operation(summary = "删除健康记录", description = "删除指定的健康记录")
    public ResultVO<Void> deleteHealthRecord(
            @RequestAttribute("userId") Long userId,
            @Parameter(description = "记录ID", required = true)
            @PathVariable Long recordId) {

        log.info("删除健康记录, userId: {}, recordId: {}", userId, recordId);

        healthService.deleteHealthRecord(userId, recordId);
        return ResultVO.success();
    }
}
