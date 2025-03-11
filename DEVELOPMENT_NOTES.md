# Development Notes

This document outlines potential improvements, considerations, and known limitations in the **Bubbles Cloud Converter** codebase. Contributors are encouraged to review these points and propose solutions or enhancements via pull requests.

---

## 1. Concurrency & Temporary Files

- **Iterative Video Compression**  
  In `converter.py`’s `convert_video()` function, we create a temporary file (`.temp`) for each bitrate tested.  
  - **Issue:** If multiple users convert the same file name concurrently, they could overwrite each other’s `.temp` file.  
  - **Suggestion:** Use a unique identifier (e.g., UUID) or random string to ensure each job’s temp file is unique.

- **Renaming Temp Files**  
  The code renames the `.temp` file to the final output after a successful pass.  
  - **Issue:** Another process could still be using or writing to that `.temp` file, leading to race conditions.  
  - **Suggestion:** Again, unique filenames and robust error handling can mitigate concurrency issues.

---

## 2. Large File Handling & Performance

- **Iterative Approaches**  
  - **Images:** Repeatedly lowering JPEG quality can be CPU-intensive, especially for large images or very low target sizes.  
  - **Audio/Video:** Testing multiple bitrates increases CPU/disk usage, particularly for large media files.  
  - **Suggestion:** Implement user-defined single-pass compression for more control, or ensure you have enough server resources for iterative methods.

- **Memory Usage**  
  - Handling large media files fully in memory can spike RAM usage.  
  - **Suggestion:** For extremely large files, consider a streaming or chunk-based approach.

---

## 3. File Validation & Security

- **File Extension vs. Actual Format**  
  - **Issue:** The code decides how to convert based on the file extension, which can be spoofed.  
  - **Suggestion:** Implement deeper file-type checks (e.g., using Python’s `imghdr`, reading headers, or verifying magic numbers).

- **Path Sanitization**  
  - **Issue:** Uploaded filenames might include special characters or path traversal attempts.  
  - **Suggestion:** Sanitize or randomize filenames before saving.

- **Rate Limiting / Authentication**  
  - **Issue:** Without limits, a malicious user could upload huge files or spam conversions.  
  - **Suggestion:** Implement file-size checks, rate limiting, or user authentication to prevent abuse.

---

## 4. `run.py` Considerations

- **Debug Mode**  
  - Currently uses `app.run(debug=True)`.  
  - **Suggestion:** Use `debug=False` for production and run behind a production WSGI server (e.g., Gunicorn) with Nginx.

- **File Size Limits**  
  - Flask doesn’t impose an upload limit by default.  
  - **Suggestion:** Set `app.config['MAX_CONTENT_LENGTH']` to prevent overly large uploads.

- **Parallel Requests**  
  - Multiple conversions happening at once can cause resource contention.  
  - **Suggestion:** Ensure concurrency is handled properly, possibly by using a queue or job manager (e.g., Celery or RQ) for large or time-consuming conversions.

---

## 5. Logging & Error Handling

- **Error Reporting**  
  - Currently, conversion errors are flashed to the user in a generic way.  
  - **Suggestion:** Implement structured logging to capture detailed errors for debugging or analytics.

- **No Logging of Completed Jobs**  
  - The code does not store logs of successful conversions.  
  - **Suggestion:** Record usage metrics (file size, duration, success/failure) for insights or auditing.

---

## Summary

- **Local / Small Scale Usage:** The code is generally fine for local development or small-scale usage.
- **Production Readiness:** Address concurrency, security, file validation, logging, and resource management if you plan to deploy publicly or handle large workloads.

Feel free to open an issue or pull request if you’d like to tackle any of these improvements. We welcome contributions and feedback from the community—together, we can make Bubbles Cloud Converter more robust and feature-rich!

---
