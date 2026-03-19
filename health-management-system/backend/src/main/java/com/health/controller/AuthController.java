package com.health.controller;

import com.health.dto.LoginDTO;
import com.health.dto.RegisterDTO;
import com.health.service.UserService;
import com.health.vo.ResultVO;
import com.health.vo.UserVO;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * 认证控制器
 */
@RestController
@RequestMapping("/auth")
public class AuthController {
    
    @Autowired
    private UserService userService;
    
    /**
     * 用户登录
     */
    @PostMapping("/login")
    public ResultVO<Map<String, Object>> login(@Valid @RequestBody LoginDTO loginDTO) {
        Map<String, Object> result = userService.login(loginDTO);
        return ResultVO.success(result);
    }
    
    /**
     * 用户注册
     */
    @PostMapping("/register")
    public ResultVO<UserVO> register(@Valid @RequestBody RegisterDTO registerDTO) {
        UserVO user = userService.register(registerDTO);
        return ResultVO.success(user);
    }
}
