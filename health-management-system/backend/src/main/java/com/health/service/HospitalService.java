package com.health.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.health.entity.Hospital;
import com.health.mapper.HospitalMapper;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 医院/体检机构服务类
 */
@Service
public class HospitalService extends ServiceImpl<HospitalMapper, Hospital> {

    /**
     * 获取医院列表
     */
    public List<Hospital> getHospitals(String city, Boolean recommended) {
        LambdaQueryWrapper<Hospital> wrapper = new LambdaQueryWrapper<>();
        
        if (recommended != null && recommended) {
            wrapper.eq(Hospital::getIsRecommended, true);
        }
        
        // 默认按推荐和评分排序
        wrapper.orderByDesc(Hospital::getIsRecommended)
               .orderByDesc(Hospital::getRating);
        
        return list(wrapper);
    }

    /**
     * 获取附近医院（按距离排序）
     */
    public List<Hospital> getNearbyHospitals(Double lat, Double lng) {
        // 获取所有医院
        List<Hospital> allHospitals = list();
        
        // 计算距离并排序
        return allHospitals.stream()
                .map(hospital -> {
                    // 计算距离
                    double distance = calculateDistance(
                            lat, lng,
                            hospital.getLatitude().doubleValue(),
                            hospital.getLongitude().doubleValue()
                    );
                    hospital.setDistance(distance);
                    return hospital;
                })
                .sorted(Comparator.comparing(Hospital::getDistance))
                .limit(10) // 只返回最近的10家
                .collect(Collectors.toList());
    }

    /**
     * 获取医院详情
     */
    public Hospital getHospitalById(Long id) {
        return getById(id);
    }

    /**
     * 计算两点之间的距离（单位：公里）
     * 使用Haversine公式
     */
    private double calculateDistance(double lat1, double lng1, double lat2, double lng2) {
        final double R = 6371; // 地球半径（公里）
        
        double latDistance = Math.toRadians(lat2 - lat1);
        double lngDistance = Math.toRadians(lng2 - lng1);
        
        double a = Math.sin(latDistance / 2) * Math.sin(latDistance / 2)
                + Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2))
                * Math.sin(lngDistance / 2) * Math.sin(lngDistance / 2);
        
        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        
        return R * c;
    }
}
