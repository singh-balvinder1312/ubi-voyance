package com.ubivoyance.backend.service;

import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

@Service
public class PythonService {

    private final RestTemplate restTemplate = new RestTemplate();
    private final String pythonBaseUrl = "http://localhost:5000";

    public String checkPythonHealth() {
        return restTemplate.getForObject(pythonBaseUrl + "/python/health", String.class);
    }

    public String runSimulation(MultipartFile vtuFile, MultipartFile jniiFile, int wavelength) throws Exception {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("vtu_file", new ByteArrayResource(vtuFile.getBytes()) {
            @Override
            public String getFilename() {
                return vtuFile.getOriginalFilename();
            }
        });
        body.add("jnii_file", new ByteArrayResource(jniiFile.getBytes()) {
            @Override
            public String getFilename() {
                return jniiFile.getOriginalFilename();
            }
        });
        body.add("wavelength", String.valueOf(wavelength));

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

        ResponseEntity<String> response = restTemplate.postForEntity(
                pythonBaseUrl + "/python/simulate",
                requestEntity,
                String.class
        );

        return response.getBody();
    }
}