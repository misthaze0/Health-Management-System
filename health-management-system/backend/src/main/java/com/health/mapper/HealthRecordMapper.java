package com.health.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.health.entity.HealthRecord;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.time.LocalDate;
import java.util.List;

/**
 * 健康记录Mapper接口
 * 继承BaseMapper提供基础CRUD操作
 * 定义自定义查询方法
 *
 * @author Health Management System
 * @since 1.0.0
 */
@Mapper
public interface HealthRecordMapper extends BaseMapper<HealthRecord> {

    /**
     * 根据用户ID和指标类型查询健康记录
     * 按记录日期降序排列
     *
     * @param userId     用户ID
     * @param metricType 指标类型
     * @return 健康记录列表
     */
    @Select("SELECT * FROM health_record " +
            "WHERE user_id = #{userId} AND metric_type = #{metricType} " +
            "ORDER BY record_date DESC, create_time DESC")
    List<HealthRecord> selectByUserAndMetricType(@Param("userId") Long userId,
                                                  @Param("metricType") String metricType);

    /**
     * 根据用户ID和日期范围查询健康记录
     * 按记录日期降序排列
     *
     * @param userId    用户ID
     * @param startDate 开始日期
     * @param endDate   结束日期
     * @return 健康记录列表
     */
    @Select("SELECT * FROM health_record " +
            "WHERE user_id = #{userId} AND record_date BETWEEN #{startDate} AND #{endDate} " +
            "ORDER BY record_date DESC, create_time DESC")
    List<HealthRecord> selectByDateRange(@Param("userId") Long userId,
                                          @Param("startDate") LocalDate startDate,
                                          @Param("endDate") LocalDate endDate);

    /**
     * 根据用户ID、指标类型和日期范围查询健康记录
     * 按记录日期降序排列
     *
     * @param userId     用户ID
     * @param metricType 指标类型
     * @param startDate  开始日期
     * @param endDate    结束日期
     * @return 健康记录列表
     */
    @Select("SELECT * FROM health_record " +
            "WHERE user_id = #{userId} AND metric_type = #{metricType} " +
            "AND record_date BETWEEN #{startDate} AND #{endDate} " +
            "ORDER BY record_date DESC, create_time DESC")
    List<HealthRecord> selectByUserAndMetricTypeAndDateRange(@Param("userId") Long userId,
                                                              @Param("metricType") String metricType,
                                                              @Param("startDate") LocalDate startDate,
                                                              @Param("endDate") LocalDate endDate);

    /**
     * 查询用户最新的健康记录（按指标类型分组）
     * 使用子查询获取每种指标类型的最新记录
     *
     * @param userId 用户ID
     * @return 最新健康记录列表
     */
    @Select("SELECT hr.* FROM health_record hr " +
            "INNER JOIN (" +
            "    SELECT metric_type, MAX(record_date) as max_date " +
            "    FROM health_record " +
            "    WHERE user_id = #{userId} " +
            "    GROUP BY metric_type" +
            ") latest ON hr.metric_type = latest.metric_type AND hr.record_date = latest.max_date " +
            "WHERE hr.user_id = #{userId} " +
            "ORDER BY hr.metric_type")
    List<HealthRecord> selectLatestByUserId(@Param("userId") Long userId);

    /**
     * 查询用户指定指标类型的最新记录
     *
     * @param userId     用户ID
     * @param metricType 指标类型
     * @return 最新健康记录
     */
    @Select("SELECT * FROM health_record " +
            "WHERE user_id = #{userId} AND metric_type = #{metricType} " +
            "ORDER BY record_date DESC, create_time DESC LIMIT 1")
    HealthRecord selectLatestByUserAndMetricType(@Param("userId") Long userId,
                                                  @Param("metricType") String metricType);
}
