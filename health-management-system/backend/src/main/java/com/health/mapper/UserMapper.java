package com.health.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.health.entity.User;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 用户Mapper接口
 */
@Mapper
public interface UserMapper extends BaseMapper<User> {

    /**
     * 查询用户的角色编码列表
     *
     * @param userId 用户ID
     * @return 角色编码列表
     */
    @Select("SELECT r.role_code FROM sys_role r " +
            "INNER JOIN sys_user_role ur ON r.id = ur.role_id " +
            "WHERE ur.user_id = #{userId} AND r.status = 1")
    List<String> selectUserRoles(@Param("userId") Long userId);

    /**
     * 根据角色编码为用户分配角色
     *
     * @param userId   用户ID
     * @param roleCode 角色编码
     */
    @Insert("INSERT INTO sys_user_role (user_id, role_id) " +
            "SELECT #{userId}, id FROM sys_role WHERE role_code = #{roleCode} AND status = 1")
    void insertUserRoleByCode(@Param("userId") Long userId, @Param("roleCode") String roleCode);
}
