package com.health.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * 删除账号DTO
 */
@Data
public class DeleteAccountDTO {

    @NotBlank(message = "密码不能为空")
    private String password;

    @NotBlank(message = "确认文字不能为空")
    private String confirmText;
}
