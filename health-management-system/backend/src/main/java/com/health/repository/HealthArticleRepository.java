package com.health.repository;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.health.entity.HealthArticle;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 健康知识文章数据访问层
 * 提供对health_articles表的CRUD操作
 *
 * @author Health Management System
 * @since 1.0.0
 */
@Mapper
public interface HealthArticleRepository extends BaseMapper<HealthArticle> {

    /**
     * 查询所有启用的文章，按创建时间倒序
     */
    @Select("SELECT * FROM health_articles WHERE status = 1 ORDER BY create_time DESC")
    List<HealthArticle> selectAllActiveArticles();
}
