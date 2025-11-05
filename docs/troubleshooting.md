# Troubleshooting

Common issues and solutions for Pai Note Exporter.

## Quick Diagnosis

### Check System Requirements

```bash
# Verify Python version
python --version  # Should be 3.11+

# Check available disk space
df -h

# Verify network connectivity
ping -c 3 google.com

# Check if ports are available
netstat -tlnp | grep :8080  # For local servers
```

### Run Diagnostics

```bash
# Test basic functionality
pai-note-exporter --version

# Check configuration
pai-note-exporter export --help

# Test with debug logging
pai-note-exporter export --log-level DEBUG --limit 1
```

## Authentication Issues

### "Login Failed" Error

**Symptoms:**
```
❌ Authentication failed: Invalid credentials
❌ Login failed after multiple attempts
```

**Solutions:**

1. **Verify Credentials:**
   ```bash
   # Check environment variables
   echo $PLAUD_EMAIL
   echo $PLAUD_PASSWORD

   # Or check .env file
   cat .env
   ```

2. **Reset Password:**
   - Visit Plaud.ai website
   - Reset password if forgotten
   - Update environment variables

3. **Check Account Status:**
   - Verify account is active
   - Check for any Plaud.ai service outages
   - Confirm email is verified

4. **Browser Issues:**
   ```bash
   # Clear browser cache (if using playwright)
   playwright install chromium
   ```

### "Session Expired" Error

**Symptoms:**
```
❌ Session expired, please login again
```

**Solutions:**

1. **Automatic Re-authentication:**
   ```python
   # The client handles this automatically
   client = PlaudClient(email, password)
   await client.login()  # Will re-authenticate if needed
   ```

2. **Check Token Validity:**
   - Tokens expire after some time
   - Application handles renewal automatically
   - Manual intervention rarely needed

## Network Issues

### Connection Timeout

**Symptoms:**
```
❌ Network timeout
❌ Connection refused
```

**Solutions:**

1. **Increase Timeout:**
   ```bash
   # Set longer timeout
   export PLAUD_TIMEOUT=120
   pai-note-exporter export
   ```

2. **Check Network:**
   ```bash
   # Test connectivity
   curl -I https://app.plaud.ai

   # Check DNS
   nslookup app.plaud.ai
   ```

3. **Proxy Configuration:**
   ```bash
   # Configure proxy if needed
   export HTTP_PROXY=http://proxy.company.com:8080
   export HTTPS_PROXY=http://proxy.company.com:8080
   ```

4. **Firewall Issues:**
   - Ensure ports 80/443 are open
   - Check corporate firewall rules
   - Try different network connection

### Rate Limiting

**Symptoms:**
```
❌ Too many requests
❌ Rate limit exceeded
```

**Solutions:**

1. **Reduce Concurrency:**
   ```bash
   # Export in smaller batches
   pai-note-exporter export --limit 5
   ```

2. **Add Delays:**
   ```python
   import asyncio

   # Add delays between requests
   recordings = await client.get_recordings()
   for recording in recordings:
       await exporter.export_recording(recording)
       await asyncio.sleep(2)  # 2 second delay
   ```

3. **Check API Limits:**
   - Plaud.ai may have request limits
   - Space out large exports
   - Consider scheduling during off-peak hours

## Export Issues

### No Recordings Found

**Symptoms:**
```
❌ No recordings found
📁 Found 0 recordings
```

**Solutions:**

1. **Check Account:**
   - Verify recordings exist in Plaud.ai web interface
   - Check if recordings are in different account
   - Confirm recordings are fully uploaded

2. **API Access:**
   ```python
   # Test API access
   recordings = await client.get_recordings()
   print(f"API returned {len(recordings)} recordings")
   ```

3. **Filter Issues:**
   - Some recordings may be filtered out
   - Check recording status (processing, failed, etc.)
   - Verify date ranges if using filters

### Transcription Not Available

**Symptoms:**
```
❌ Recording not transcribed yet
⚠️  Transcription in progress
```

**Solutions:**

1. **Wait for Processing:**
   - Transcriptions take time to process
   - Check status in Plaud.ai web interface
   - Retry export later

2. **Check Recording Status:**
   ```python
   recordings = await client.get_recordings()
   for r in recordings:
       print(f"{r.name}: {r.status}")
   ```

3. **Force Reprocessing:**
   - May need to re-upload recording in Plaud.ai
   - Contact Plaud.ai support for stuck transcriptions

### File Write Errors

**Symptoms:**
```
❌ Permission denied
❌ Disk full
❌ File locked
```

**Solutions:**

1. **Check Permissions:**
   ```bash
   # Check directory permissions
   ls -la exports/

   # Fix permissions
   chmod 755 exports/
   ```

2. **Disk Space:**
   ```bash
   # Check available space
   df -h

   # Clean up space if needed
   rm -rf exports/old_files/
   ```

3. **File Locks:**
   - Close any applications using the files
   - Wait for other processes to finish
   - Check for antivirus software interference

## Audio Export Issues

### Audio Download Failed

**Symptoms:**
```
❌ Audio download failed
❌ File corrupted
```

**Solutions:**

1. **Check Audio Availability:**
   ```python
   # Verify audio exists
   recording = await client.get_recording_details(recording_id)
   print(f"Has audio: {recording.has_audio}")
   ```

2. **Network Issues:**
   - Audio files are large
   - May need longer timeouts
   - Check network stability

3. **Storage Issues:**
   ```bash
   # Audio files need significant space
   # Check available space (audio files can be 10MB+ each)
   df -h
   ```

### Audio Format Issues

**Symptoms:**
```
❌ Unsupported format
❌ Codec error
```

**Solutions:**

1. **Check Format Support:**
   - Pai Note Exporter downloads original format
   - Check Plaud.ai supported formats
   - Convert if needed using ffmpeg

2. **Conversion Tools:**
   ```bash
   # Convert audio format
   ffmpeg -i input.mp3 output.wav
   ```

## Performance Issues

### Slow Exports

**Symptoms:**
```
📊 Export taking too long
```

**Solutions:**

1. **Batch Processing:**
   ```bash
   # Process in smaller batches
   pai-note-exporter export --limit 10
   ```

2. **Concurrent Processing:**
   ```python
   # Use asyncio for concurrent downloads
   import asyncio

   async def batch_export():
       tasks = [exporter.export_recording(r) for r in recordings[:5]]
       await asyncio.gather(*tasks)
   ```

3. **Resource Monitoring:**
   ```bash
   # Monitor system resources
   top
   iotop  # I/O monitoring
   nload  # Network monitoring
   ```

### Memory Issues

**Symptoms:**
```
❌ Out of memory
📊 High memory usage
```

**Solutions:**

1. **Reduce Batch Size:**
   ```bash
   # Smaller batches use less memory
   pai-note-exporter export --limit 5
   ```

2. **Monitor Memory:**
   ```python
   import psutil
   import os

   process = psutil.Process(os.getpid())
   print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB")
   ```

3. **Garbage Collection:**
   ```python
   import gc
   # Force cleanup
   gc.collect()
   ```

## Configuration Issues

### Environment Variables

**Symptoms:**
```
❌ Configuration error
❌ Missing required settings
```

**Solutions:**

1. **Check Variables:**
   ```bash
   # List all environment variables
   env | grep PLAUD

   # Check .env file
   cat .env
   ```

2. **Validate Configuration:**
   ```python
   from pai_note_exporter.config import Config

   try:
       config = Config()
       print("Configuration valid")
   except Exception as e:
       print(f"Configuration error: {e}")
   ```

3. **Reset Configuration:**
   ```bash
   # Remove invalid .env file
   rm .env

   # Recreate with correct values
   cat > .env << EOF
   PLAUD_EMAIL=your-email@example.com
   PLAUD_PASSWORD=your-password
   EOF
   ```

### Path Issues

**Symptoms:**
```
❌ File not found
❌ Invalid path
```

**Solutions:**

1. **Check Paths:**
   ```bash
   # Verify export directory exists
   ls -la exports/

   # Check absolute paths
   pwd
   realpath exports/
   ```

2. **Create Directories:**
   ```bash
   # Create export directory
   mkdir -p exports/

   # Set correct permissions
   chmod 755 exports/
   ```

3. **Path Encoding:**
   - Ensure paths don't contain special characters
   - Use absolute paths when possible
   - Check for Unicode issues in directory names

## Browser Automation Issues

### Playwright Errors

**Symptoms:**
```
❌ Browser automation failed
❌ Playwright not installed
```

**Solutions:**

1. **Install Browsers:**
   ```bash
   # Install playwright browsers
   playwright install chromium

   # Or install all browsers
   playwright install
   ```

2. **Update Playwright:**
   ```bash
   # Update to latest version
   pip install --upgrade playwright
   playwright install
   ```

3. **Headless Mode:**
   ```python
   # Force headless mode
   from playwright.async_api import async_playwright

   async with async_playwright() as p:
       browser = await p.chromium.launch(headless=True)
   ```

### Captcha/Verification Issues

**Symptoms:**
```
❌ Captcha detected
❌ Human verification required
```

**Solutions:**

1. **Manual Intervention:**
   - Some sites require manual captcha solving
   - Complete verification in browser first
   - Then run export

2. **Alternative Methods:**
   - Check if API authentication is available
   - Contact Plaud.ai for API access
   - Use different authentication flow

## Logging and Debugging

### Enable Debug Logging

```bash
# Maximum verbosity
pai-note-exporter export --log-level DEBUG

# Log to file
pai-note-exporter export --log-level DEBUG 2>&1 | tee debug.log
```

### Analyze Logs

```bash
# Search for errors
grep ERROR pai_note_exporter.log

# Check recent activity
tail -50 pai_note_exporter.log

# Filter by component
grep "authentication" pai_note_exporter.log
```

### Common Log Patterns

```
# Successful authentication
2025-01-01 12:00:00 - pai_note_exporter.login - INFO - Login successful

# Network issues
2025-01-01 12:00:01 - pai_note_exporter.client - ERROR - Connection timeout

# Export progress
2025-01-01 12:00:02 - pai_note_exporter.export - INFO - Exported recording_2025-01-01_12-00-00
```

## Getting Help

### Community Support

1. **GitHub Issues:**
   - Check existing issues
   - Create new issue with full details
   - Include logs and error messages

2. **Documentation:**
   - Review README.md
   - Check configuration examples
   - Read API documentation

3. **Debug Information:**
   ```bash
   # Collect system information
   uname -a
   python --version
   pip list | grep pai-note-exporter
   ```

### Professional Support

For enterprise support or custom integrations:

- Contact the development team
- Provide detailed error logs
- Include system configuration
- Describe expected vs actual behavior

## Prevention

### Best Practices

1. **Regular Testing:**
   ```bash
   # Test export weekly
   pai-note-exporter export --limit 1
   ```

2. **Monitor Resources:**
   ```bash
   # Check disk space regularly
   df -h
   ```

3. **Backup Configuration:**
   ```bash
   # Backup .env file securely
   cp .env .env.backup
   ```

4. **Update Regularly:**
   ```bash
   # Keep dependencies updated
   pip install --upgrade pai-note-exporter
   ```

### Monitoring Setup

```bash
# Cron job for regular health checks
cat > /etc/cron.daily/pai-health-check << 'EOF'
#!/bin/bash
# Health check script
/usr/local/bin/pai-note-exporter export --limit 1 --log-level ERROR
if [ $? -ne 0 ]; then
    echo "Pai Note Exporter health check failed" | mail -s "Health Check Failed" admin@example.com
fi
EOF

chmod +x /etc/cron.daily/pai-health-check
```

This comprehensive troubleshooting guide should help resolve most issues. If problems persist, please provide detailed logs and system information when seeking support.
