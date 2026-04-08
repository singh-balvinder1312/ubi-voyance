package com.ubivoyance.backend.controller;

import com.ubivoyance.backend.service.PythonService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/pipeline")
public class PipelineController {

    @Autowired
    private PythonService pythonService;

    @GetMapping("/status")
    public String getPipelineStatus() {
        return pythonService.checkPythonHealth();
    }

    @PostMapping("/simulate")
    public ResponseEntity<String> simulate(
            @RequestParam("vtu_file") MultipartFile vtuFile,
            @RequestParam("jnii_file") MultipartFile jniiFile,
            @RequestParam(value = "wavelength", defaultValue = "750") int wavelength) {
        try {
            String result = pythonService.runSimulation(vtuFile, jniiFile, wavelength);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.status(500).body("{\"error\": \"" + e.getMessage() + "\"}");
        }
    }
}