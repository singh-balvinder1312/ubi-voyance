package com.ubivoyance.backend.controller;

import com.ubivoyance.backend.service.PythonService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/pipeline")
public class PipelineController {

    @Autowired
    private PythonService pythonService;

    @GetMapping("/status")
    public String getPipelineStatus() {
        return pythonService.checkPythonHealth();
    }
}