package com.example.impact.controller;

import com.example.impact.model.ImpactResult;
import com.example.impact.service.DiffService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/diff")
public class DiffController {

    @Autowired
    private DiffService diffService;

    @PostMapping("/analyze")
    public ImpactResult analyze(@RequestBody String unifiedDiff) {
        return diffService.analyzeDiff(unifiedDiff);
    }
}
