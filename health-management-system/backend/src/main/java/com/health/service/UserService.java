package com.health.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.health.dto.BindEmailDTO;
import com.health.dto.BindPhoneDTO;
import com.health.dto.ChangePasswordDTO;
import com.health.dto.LoginDTO;
import com.health.dto.RegisterDTO;
import com.health.dto.UpdateUserDTO;
import com.health.entity.User;
import com.health.mapper.UserMapper;
import com.health.utils.FileUtil;
import com.health.utils.JwtUtil;
import com.health.vo.UserVO;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * 用户服务类
 */
@Slf4j
@Service
public class UserService {

    @Autowired
    private UserMapper userMapper;

    @Autowired
    private JwtUtil jwtUtil;

    @Autowired
    private BCryptPasswordEncoder passwordEncoder;

    @Value("${file.upload.path:d:/基于KIMI的全流程健康管理系统/health-management-system/backend/uploads/avatar}")
    private String uploadPath;

    @Value("${file.upload.url-prefix:avatar}")
    private String urlPrefix;
    
    /**
     * 用户登录
     */
    public Map<String, Object> login(LoginDTO loginDTO) {
        // 查询用户
        User user = userMapper.selectOne(
            new QueryWrapper<User>().eq("username", loginDTO.getUsername())
        );
        
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }
        
        // 验证密码
        if (!passwordEncoder.matches(loginDTO.getPassword(), user.getPassword())) {
            throw new RuntimeException("密码错误");
        }
        
        // 检查用户状态
        if (user.getStatus() != 1) {
            throw new RuntimeException("用户已被禁用");
        }
        
        // 生成Token
        String token = jwtUtil.generateToken(user.getId(), user.getUsername());
        
        // 返回结果
        Map<String, Object> result = new HashMap<>();
        result.put("token", token);
        result.put("user", convertToVO(user));
        
        return result;
    }
    
    /**
     * 管理员注册邀请码
     */
    private static final String ADMIN_INVITE_CODE = "123456";

    /**
     * 用户注册
     * 支持选择角色，管理员角色需要邀请码
     */
    public UserVO register(RegisterDTO registerDTO) {
        // 检查用户名是否已存在
        User existUser = userMapper.selectOne(
            new QueryWrapper<User>().eq("username", registerDTO.getUsername())
        );

        if (existUser != null) {
            throw new RuntimeException("用户名已存在");
        }

        // 检查密码是否一致
        if (!registerDTO.getPassword().equals(registerDTO.getConfirmPassword())) {
            throw new RuntimeException("两次输入的密码不一致");
        }

        // 验证角色和邀请码
        String roleCode = registerDTO.getRoleCode();
        if (roleCode == null || roleCode.trim().isEmpty()) {
            roleCode = "user"; // 默认为普通用户
        }

        // 如果选择的是管理员角色，验证邀请码
        if ("admin".equals(roleCode)) {
            String inviteCode = registerDTO.getInviteCode();
            if (inviteCode == null || !ADMIN_INVITE_CODE.equals(inviteCode)) {
                throw new RuntimeException("管理员邀请码错误");
            }
        }

        // 验证角色是否有效
        List<String> validRoles = Arrays.asList("user", "doctor", "admin");
        if (!validRoles.contains(roleCode)) {
            throw new RuntimeException("无效的角色类型");
        }

        // 创建新用户
        User user = new User();
        user.setUsername(registerDTO.getUsername());
        user.setPassword(passwordEncoder.encode(registerDTO.getPassword()));
        user.setEmail(registerDTO.getEmail());
        user.setPhone(registerDTO.getPhone());
        user.setRealName(registerDTO.getRealName());
        user.setStatus(1);

        userMapper.insert(user);

        // 分配角色
        assignUserRole(user.getId(), roleCode);
        log.info("用户注册成功: username={}, role={}", user.getUsername(), roleCode);

        return convertToVO(user);
    }

    /**
     * 为用户分配角色
     *
     * @param userId   用户ID
     * @param roleCode 角色编码
     */
    private void assignUserRole(Long userId, String roleCode) {
        try {
            userMapper.insertUserRoleByCode(userId, roleCode);
            log.debug("分配角色成功: userId={}, roleCode={}", userId, roleCode);
        } catch (Exception e) {
            log.error("分配角色失败: userId={}, roleCode={}", userId, roleCode, e);
            // 角色分配失败不影响注册成功，记录日志即可
        }
    }
    
    /**
     * 根据ID获取用户信息
     */
    public UserVO getUserById(Long userId) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }
        return convertToVO(user);
    }
    
    /**
     * 更新用户信息
     */
    public UserVO updateUserInfo(Long userId, UpdateUserDTO dto) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }

        // 更新字段
        if (dto.getRealName() != null) {
            user.setRealName(dto.getRealName());
        }
        if (dto.getGender() != null) {
            user.setGender(dto.getGender());
        }
        if (dto.getBirthday() != null) {
            user.setBirthday(dto.getBirthday());
        }
        if (dto.getEmail() != null) {
            user.setEmail(dto.getEmail());
        }
        if (dto.getPhone() != null) {
            user.setPhone(dto.getPhone());
        }

        userMapper.updateById(user);
        return convertToVO(user);
    }

    /**
     * 修改密码
     */
    public void changePassword(Long userId, ChangePasswordDTO dto) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }

        // 验证原密码
        if (!passwordEncoder.matches(dto.getOldPassword(), user.getPassword())) {
            throw new RuntimeException("原密码错误");
        }

        // 验证新密码和确认密码是否一致
        if (!dto.getNewPassword().equals(dto.getConfirmPassword())) {
            throw new RuntimeException("两次输入的新密码不一致");
        }

        // 更新密码
        user.setPassword(passwordEncoder.encode(dto.getNewPassword()));
        userMapper.updateById(user);
    }

    /**
     * 上传头像
     */
    public String uploadAvatar(Long userId, MultipartFile file) {
        if (file.isEmpty()) {
            throw new RuntimeException("请选择要上传的文件");
        }

        // 检查文件类型
        String contentType = file.getContentType();
        if (contentType == null || !contentType.startsWith("image/")) {
            throw new RuntimeException("只能上传图片文件");
        }

        // 生成文件名
        String originalFilename = file.getOriginalFilename();
        String extension = originalFilename != null ?
                originalFilename.substring(originalFilename.lastIndexOf(".")) : ".jpg";
        String newFilename = UUID.randomUUID().toString() + extension;

        // 创建上传目录
        File uploadDir = new File(uploadPath);
        if (!uploadDir.exists()) {
            uploadDir.mkdirs();
        }

        // 保存文件
        File destFile = new File(uploadDir, newFilename);
        try {
            file.transferTo(destFile);
        } catch (IOException e) {
            log.error("头像上传失败", e);
            throw new RuntimeException("头像上传失败");
        }

        // 获取旧头像URL并删除旧头像
        User user = userMapper.selectById(userId);
        if (user != null && user.getAvatar() != null && !user.getAvatar().isEmpty()) {
            String oldAvatarUrl = user.getAvatar();
            // 使用FileUtil删除旧头像
            boolean deleted = FileUtil.deleteUploadFile(oldAvatarUrl);
            if (deleted) {
                log.info("删除旧头像成功: {}", oldAvatarUrl);
            } else {
                log.warn("删除旧头像失败或文件不存在: {}", oldAvatarUrl);
            }
        }

        // 更新用户头像URL
        String avatarUrl = urlPrefix + "/" + newFilename;
        if (user != null) {
            user.setAvatar(avatarUrl);
            userMapper.updateById(user);
        }

        return avatarUrl;
    }

    /**
     * 绑定手机号
     * 简化版：直接绑定，不发送验证码（实际生产环境应发送验证码）
     */
    public UserVO bindPhone(Long userId, BindPhoneDTO dto) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }

        // 检查手机号是否已被其他用户绑定
        User existUser = userMapper.selectOne(
            new QueryWrapper<User>().eq("phone", dto.getPhone())
        );
        if (existUser != null && !existUser.getId().equals(userId)) {
            throw new RuntimeException("该手机号已被其他用户绑定");
        }

        // TODO: 验证验证码（实际生产环境需要实现验证码验证）
        // 简化版：直接绑定
        user.setPhone(dto.getPhone());
        userMapper.updateById(user);

        log.info("用户绑定手机号成功: userId={}, phone={}", userId, dto.getPhone());
        return convertToVO(user);
    }

    /**
     * 绑定邮箱
     * 简化版：直接绑定，不发送验证码（实际生产环境应发送验证码）
     */
    public UserVO bindEmail(Long userId, BindEmailDTO dto) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }

        // 检查邮箱是否已被其他用户绑定
        User existUser = userMapper.selectOne(
            new QueryWrapper<User>().eq("email", dto.getEmail())
        );
        if (existUser != null && !existUser.getId().equals(userId)) {
            throw new RuntimeException("该邮箱已被其他用户绑定");
        }

        // TODO: 验证验证码（实际生产环境需要实现验证码验证）
        // 简化版：直接绑定
        user.setEmail(dto.getEmail());
        userMapper.updateById(user);

        log.info("用户绑定邮箱成功: userId={}, email={}", userId, dto.getEmail());
        return convertToVO(user);
    }

    /**
     * 删除账号（逻辑删除）
     */
    public void deleteAccount(Long userId, String password) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }

        // 验证密码
        if (!passwordEncoder.matches(password, user.getPassword())) {
            throw new RuntimeException("密码错误");
        }

        // 逻辑删除
        user.setDeleted(1);
        user.setStatus(0);
        userMapper.updateById(user);

        log.info("用户删除账号成功: userId={}", userId);
    }

    /**
     * 转换为VO
     */
    private UserVO convertToVO(User user) {
        UserVO vo = new UserVO();
        BeanUtils.copyProperties(user, vo);
        // 查询并设置用户角色
        List<String> roles = userMapper.selectUserRoles(user.getId());
        if (roles != null && !roles.isEmpty()) {
            vo.setRole(roles.get(0).toLowerCase());
        }
        return vo;
    }
}
