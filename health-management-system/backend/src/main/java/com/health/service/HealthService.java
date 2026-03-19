package com.health.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.health.dto.HealthRecordDTO;
import com.health.entity.HealthRecord;
import com.health.mapper.HealthRecordMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 健康服务类
 * 提供健康记录的增删改查和统计分析功能
 *
 * @author Health Management System
 * @since 1.0.0
 */
@Slf4j
@Service
public class HealthService {

    @Autowired
    private HealthRecordMapper healthRecordMapper;

    // ==================== 健康记录管理 ====================

    /**
     * 获取用户的健康记录列表
     * 支持按指标类型筛选
     *
     * @param userId     用户ID
     * @param metricType 指标类型（可选）
     * @param startDate  开始日期（可选）
     * @param endDate    结束日期（可选）
     * @return 健康记录DTO列表
     */
    public List<HealthRecordDTO> getUserHealthRecords(Long userId,
                                                       String metricType,
                                                       LocalDate startDate,
                                                       LocalDate endDate) {
        log.info("获取用户健康记录, userId: {}, metricType: {}, startDate: {}, endDate: {}",
                userId, metricType, startDate, endDate);

        List<HealthRecord> records;

        if (metricType != null && !metricType.isEmpty() && startDate != null && endDate != null) {
            // 按指标类型和日期范围查询
            records = healthRecordMapper.selectByUserAndMetricTypeAndDateRange(userId, metricType, startDate, endDate);
        } else if (metricType != null && !metricType.isEmpty()) {
            // 只按指标类型查询
            records = healthRecordMapper.selectByUserAndMetricType(userId, metricType);
        } else if (startDate != null && endDate != null) {
            // 只按日期范围查询
            records = healthRecordMapper.selectByDateRange(userId, startDate, endDate);
        } else {
            // 查询所有记录
            records = healthRecordMapper.selectList(
                    new QueryWrapper<HealthRecord>()
                            .eq("user_id", userId)
                            .orderByDesc("record_date", "create_time")
            );
        }

        log.info("查询到 {} 条健康记录", records.size());
        return records.stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    /**
     * 添加健康记录
     *
     * @param userId 用户ID
     * @param dto    健康记录DTO
     * @return 添加后的健康记录DTO
     */
    public HealthRecordDTO addHealthRecord(Long userId, HealthRecordDTO dto) {
        log.info("添加健康记录, userId: {}, metricType: {}, metricValue: {}",
                userId, dto.getMetricType(), dto.getMetricValue());

        HealthRecord record = new HealthRecord();
        BeanUtils.copyProperties(dto, record);
        record.setUserId(userId);

        healthRecordMapper.insert(record);

        dto.setId(record.getId());
        dto.setUserId(userId);
        dto.setCreateTime(record.getCreateTime());
        dto.setUpdateTime(record.getUpdateTime());

        log.info("健康记录添加成功, recordId: {}", record.getId());
        return dto;
    }

    /**
     * 更新健康记录
     *
     * @param userId    用户ID
     * @param recordId  记录ID
     * @param dto       健康记录DTO
     * @return 更新后的健康记录DTO
     */
    public HealthRecordDTO updateHealthRecord(Long userId, Long recordId, HealthRecordDTO dto) {
        log.info("更新健康记录, userId: {}, recordId: {}", userId, recordId);

        HealthRecord record = healthRecordMapper.selectById(recordId);
        if (record == null || !record.getUserId().equals(userId)) {
            log.warn("健康记录不存在或无权访问, recordId: {}", recordId);
            throw new RuntimeException("健康记录不存在");
        }

        BeanUtils.copyProperties(dto, record);
        record.setId(recordId);
        record.setUserId(userId);

        healthRecordMapper.updateById(record);

        dto.setId(recordId);
        dto.setUserId(userId);

        log.info("健康记录更新成功, recordId: {}", recordId);
        return dto;
    }

    /**
     * 删除健康记录
     *
     * @param userId   用户ID
     * @param recordId 记录ID
     */
    public void deleteHealthRecord(Long userId, Long recordId) {
        log.info("删除健康记录, userId: {}, recordId: {}", userId, recordId);

        HealthRecord record = healthRecordMapper.selectById(recordId);
        if (record == null || !record.getUserId().equals(userId)) {
            log.warn("健康记录不存在或无权访问, recordId: {}", recordId);
            throw new RuntimeException("健康记录不存在");
        }

        healthRecordMapper.deleteById(recordId);
        log.info("健康记录删除成功, recordId: {}", recordId);
    }

    // ==================== 健康统计分析 ====================

    /**
     * 获取健康统计数据
     * 包括平均值、最大值、最小值、记录数量等
     *
     * @param userId     用户ID
     * @param metricType 指标类型
     * @param startDate  开始日期
     * @param endDate    结束日期
     * @return 统计数据Map
     */
    public Map<String, Object> getHealthStatistics(Long userId,
                                                    String metricType,
                                                    LocalDate startDate,
                                                    LocalDate endDate) {
        log.info("获取健康统计数据, userId: {}, metricType: {}, startDate: {}, endDate: {}",
                userId, metricType, startDate, endDate);

        List<HealthRecord> records;
        if (metricType != null && !metricType.isEmpty()) {
            records = healthRecordMapper.selectByUserAndMetricTypeAndDateRange(userId, metricType, startDate, endDate);
        } else {
            records = healthRecordMapper.selectByDateRange(userId, startDate, endDate);
        }

        Map<String, Object> statistics = new HashMap<>();

        if (records.isEmpty()) {
            statistics.put("count", 0);
            statistics.put("average", 0);
            statistics.put("max", 0);
            statistics.put("min", 0);
            return statistics;
        }

        // 计算统计数据
        BigDecimal sum = BigDecimal.ZERO;
        BigDecimal max = records.get(0).getMetricValue();
        BigDecimal min = records.get(0).getMetricValue();

        for (HealthRecord record : records) {
            BigDecimal value = record.getMetricValue();
            sum = sum.add(value);
            if (value.compareTo(max) > 0) {
                max = value;
            }
            if (value.compareTo(min) < 0) {
                min = value;
            }
        }

        BigDecimal average = sum.divide(new BigDecimal(records.size()), 2, RoundingMode.HALF_UP);

        statistics.put("count", records.size());
        statistics.put("average", average);
        statistics.put("max", max);
        statistics.put("min", min);
        statistics.put("metricType", metricType);
        statistics.put("startDate", startDate);
        statistics.put("endDate", endDate);

        log.info("健康统计数据计算完成, count: {}, average: {}", records.size(), average);
        return statistics;
    }

    // ==================== 最新指标数据 ====================

    /**
     * 获取用户最新的各项指标数据
     *
     * @param userId 用户ID
     * @return 最新指标数据列表
     */
    public List<HealthRecordDTO> getLatestMetrics(Long userId) {
        log.info("获取用户最新指标数据, userId: {}", userId);

        List<HealthRecord> records = healthRecordMapper.selectLatestByUserId(userId);

        log.info("查询到 {} 条最新指标记录", records.size());
        return records.stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    /**
     * 获取用户指定指标类型的最新记录
     *
     * @param userId     用户ID
     * @param metricType 指标类型
     * @return 最新健康记录DTO
     */
    public HealthRecordDTO getLatestMetricByType(Long userId, String metricType) {
        log.info("获取用户最新指标数据, userId: {}, metricType: {}", userId, metricType);

        HealthRecord record = healthRecordMapper.selectLatestByUserAndMetricType(userId, metricType);

        if (record == null) {
            log.warn("未找到指标记录, userId: {}, metricType: {}", userId, metricType);
            return null;
        }

        return convertToDTO(record);
    }

    // ==================== 转换方法 ====================

    /**
     * 将实体类转换为DTO
     *
     * @param record 健康记录实体
     * @return 健康记录DTO
     */
    private HealthRecordDTO convertToDTO(HealthRecord record) {
        HealthRecordDTO dto = new HealthRecordDTO();
        BeanUtils.copyProperties(record, dto);
        return dto;
    }
}
