package com.ubivoyance.backend.service;

import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class PythonService {

    private final RestTemplate restTemplate = new RestTemplate();
    private final String pythonBaseUrl = "http://localhost:5000";

    public String checkPythonHealth() {
        return restTemplate.getForObject(pythonBaseUrl + "/python/health", String.class);
    }
}