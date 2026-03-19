package com.health.controller;

import com.health.entity.Hospital;
import com.health.service.HospitalService;
import com.health.vo.ResultVO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 医院/体检机构控制器
 */
@RestController
@RequestMapping("/hospitals")
public class HospitalController {

    @Autowired
    private HospitalService hospitalService;

    /**
     * 获取医院列表
     */
    @GetMapping
    public ResultVO<List<Hospital>> getHospitals(
            @RequestParam(required = false) String city,
            @RequestParam(required = false) Boolean recommended) {
        List<Hospital> hospitals = hospitalService.getHospitals(city, recommended);
        return ResultVO.success(hospitals);
    }

    /**
     * 获取附近医院
     * @param params 包含 lat(纬度), lng(经度)
     */
    @PostMapping("/nearby")
    public ResultVO<List<Hospital>> getNearbyHospitals(@RequestBody Map<String, Object> params) {
        Double lat = Double.valueOf(params.get("lat").toString());
        Double lng = Double.valueOf(params.get("lng").toString());
        List<Hospital> hospitals = hospitalService.getNearbyHospitals(lat, lng);
        return ResultVO.success(hospitals);
    }

    /**
     * 获取医院详情
     */
    @GetMapping("/{id}")
    public ResultVO<Hospital> getHospitalDetail(@PathVariable Long id) {
        Hospital hospital = hospitalService.getHospitalById(id);
        return ResultVO.success(hospital);
    }
}
