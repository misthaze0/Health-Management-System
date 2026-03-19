package com.health.controller;

import com.health.dto.BindEmailDTO;
import com.health.dto.BindPhoneDTO;
import com.health.dto.ChangePasswordDTO;
import com.health.dto.DeleteAccountDTO;
import com.health.dto.UpdateUserDTO;
import com.health.service.UserService;
import com.health.vo.ResultVO;
import com.health.vo.UserVO;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

/**
 * 用户控制器
 */
@RestController
@RequestMapping("/user")
public class UserController {

    @Autowired
    private UserService userService;

    /**
     * 获取当前用户信息
     */
    @GetMapping("/info")
    public ResultVO<UserVO> getUserInfo(@RequestAttribute("userId") Long userId) {
        UserVO user = userService.getUserById(userId);
        return ResultVO.success(user);
    }

    /**
     * 更新用户信息
     */
    @PutMapping("/info")
    public ResultVO<UserVO> updateUserInfo(
            @RequestAttribute("userId") Long userId,
            @Valid @RequestBody UpdateUserDTO dto) {
        UserVO user = userService.updateUserInfo(userId, dto);
        return ResultVO.success(user);
    }

    /**
     * 修改密码
     */
    @PutMapping("/password")
    public ResultVO<Void> changePassword(
            @RequestAttribute("userId") Long userId,
            @Valid @RequestBody ChangePasswordDTO dto) {
        userService.changePassword(userId, dto);
        return ResultVO.success();
    }

    /**
     * 上传头像
     */
    @PostMapping("/avatar")
    public ResultVO<String> uploadAvatar(
            @RequestAttribute("userId") Long userId,
            @RequestParam("file") MultipartFile file) {
        String avatarUrl = userService.uploadAvatar(userId, file);
        return ResultVO.success(avatarUrl);
    }

    /**
     * 绑定手机号
     */
    @PostMapping("/bind-phone")
    public ResultVO<UserVO> bindPhone(
            @RequestAttribute("userId") Long userId,
            @Valid @RequestBody BindPhoneDTO dto) {
        UserVO user = userService.bindPhone(userId, dto);
        return ResultVO.success(user);
    }

    /**
     * 绑定邮箱
     */
    @PostMapping("/bind-email")
    public ResultVO<UserVO> bindEmail(
            @RequestAttribute("userId") Long userId,
            @Valid @RequestBody BindEmailDTO dto) {
        UserVO user = userService.bindEmail(userId, dto);
        return ResultVO.success(user);
    }

    /**
     * 删除账号
     */
    @DeleteMapping("/account")
    public ResultVO<Void> deleteAccount(
            @RequestAttribute("userId") Long userId,
            @Valid @RequestBody DeleteAccountDTO dto) {
        // 验证确认文字
        if (!"删除账号".equals(dto.getConfirmText())) {
            return ResultVO.error(400, "确认文字错误，请输入\"删除账号\"");
        }
        userService.deleteAccount(userId, dto.getPassword());
        return ResultVO.success();
    }
}
