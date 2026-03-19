package com.health.vo;

import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 用户信息VO
 */
@Data
public class UserVO {

    private Long id;
    private String username;
    private String email;
    private String phone;
    private String avatar;
    private String realName;
    private Integer gender;
    private LocalDate birthday;
    private LocalDateTime createTime;
    /** 用户角色 */
    private String role;
}
