package com.example.impact.util;

import java.util.*;

public class GitDiffParser {
    public static List<String> extractChangedFiles(String diff) {
        List<String> files = new ArrayList<>();
        if (diff == null) return files;
        String[] lines = diff.split("\\n");
        for (String line: lines) {
            if (line.startsWith("+++ b/")) {
                files.add(line.substring(6));
            }
        }
        return files;
    }
}
