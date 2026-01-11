# TermGame Error Messages Guide

TermGame provides helpful, actionable error messages to guide you through common issues.

## Windows Container Image Not Found

**When it happens:** Attempting to start a PowerShell mission without Windows containers configured.

**What you see:**
```
Starting mission: powershell/basics/hello-powershell
Creating container environment (this may take a moment)...

Windows Container Image Not Found

What's happening:
  • PowerShell missions require Windows containers
  • Docker Desktop must be in Windows containers mode

How to fix:
  1. Right-click Docker Desktop system tray icon
  2. Select 'Switch to Windows containers...'
  3. Wait for Docker to restart
  4. Pull the Windows image:
     docker pull mcr.microsoft.com/windows/servercore:ltsc2022
  5. Try your mission again

Note: Windows container images are large (~5-10GB)
The first pull will take significant time.

💡 Linux missions will continue to work in Linux containers mode
```

**Solution:** Follow the numbered steps. See [Windows Containers Guide](WINDOWS_CONTAINERS.md) for detailed setup instructions.

---

## Docker Connection Error

**When it happens:** Docker Desktop is not running or not responding.

**What you see:**
```
Docker Connection Error

What's happening:
  • Cannot communicate with Docker daemon
  • Connection unstable or daemon stopped

How to fix:
  1. Check Docker Desktop is running
  2. Run: docker ps
  3. Restart Docker if necessary
  4. Try your command again
```

**Solution:** Start Docker Desktop and wait for it to fully initialize (whale icon in system tray should be steady, not animating).

---

## Container Lost

**When it happens:** Mission container was manually stopped or removed during a mission.

**What you see:**
```
Container Lost

What's happening:
  • Mission container stopped or removed

How to fix:
  1. Type: abandon
  2. Restart the mission
  3. Don't manually stop TermGame containers during missions
```

**Solution:** Use the `abandon` command to clean up, then restart the mission.

---

## Mission Not Found

**When it happens:** Attempting to start a mission with an incorrect ID.

**What you see:**
```
Error starting mission: Mission not found: linux/basics/navigations

Suggestions:
  • Check the mission ID spelling
  • Type 'list' to see all available missions
  • Mission IDs are case-sensitive
```

**Common mistakes:**
- Typos: `linux/basics/navigations` (should be `navigation`)
- Wrong case: `Linux/Basics/Navigation` (should be all lowercase)
- Missing parts: `basics/navigation` (should be `linux/basics/navigation`)

**Solution:** Use the `list` command to see all available missions and copy the exact ID.

---

## Generic Image Pull Error

**When it happens:** Network issues or registry problems when pulling container images.

**What you see:**
```
Image Pull Error

What's happening:
  • Failed to pull container image

How to fix:
  • Check your internet connection
  • Verify Docker can access the registry
  • Try manually: docker pull <image-name>
```

**Common causes:**
- No internet connection
- Corporate firewall/proxy blocking Docker Hub
- Docker Hub rate limiting (free tier)
- Temporary registry outage

**Solution:** Check your network connection and try manually pulling the image.

---

## Validation Failed

**When it happens:** Your solution doesn't match the expected result for the current step.

**What you see:**
```
❌ Validation Failed

Expected output to match: /home/learner
Got: /root

Hint: Use the 'pwd' command to print your current working directory
```

**What to do:**
1. Read the hint carefully
2. Review the step description
3. Try the suggested command
4. Type `validate` again when ready

---

## No Active Mission

**When it happens:** Using mission commands (`validate`, `hint`, `abandon`) without an active mission.

**What you see:**
```
No active mission

Use 'start <mission-id>' to begin
```

**Solution:** Start a mission first with `start <mission-id>`.

---

## Already in Mission

**When it happens:** Trying to start a new mission while already in one.

**What you see:**
```
Warning: Already in mission 'linux/basics/navigation'

Use 'abandon' to quit current mission first
```

**Solution:** Either:
- Continue your current mission
- Use `abandon` to quit, then start the new mission

---

## Troubleshooting Tips

### Enable Debug Logging

If you need more detailed error information:

```bash
# Set environment variable before starting TermGame
export TERMGAME_LOG_LEVEL=DEBUG  # Linux/macOS
set TERMGAME_LOG_LEVEL=DEBUG     # Windows CMD
$env:TERMGAME_LOG_LEVEL="DEBUG"  # PowerShell

termgame tui
```

Debug logs are saved to: `~/.termgame/termgame.log`

### Check Docker Status

```bash
# Verify Docker is running
docker ps

# Check Docker version and mode
docker version

# Should show OS/Arch: windows/amd64 for PowerShell missions
# Should show OS/Arch: linux/amd64 for Linux missions
```

### Common Solutions

| Problem | Quick Fix |
|---------|-----------|
| PowerShell missions fail | Switch to Windows containers |
| Linux missions fail | Switch to Linux containers |
| All missions fail | Restart Docker Desktop |
| Slow startup | Normal for Windows containers (30-60s) |
| Image not found | Pull the image manually first |

### Get More Help

If errors persist:

1. Check logs: `~/.termgame/termgame.log`
2. Verify Docker: `docker version` and `docker ps`
3. Review documentation: [README.md](../README.md)
4. File an issue: [GitHub Issues](https://github.com/RedjiJB/TERMGAME/issues)

Include in bug reports:
- Error message (copy/paste)
- Steps to reproduce
- Docker version: `docker version`
- TermGame version: Type `help` in TermGame
- Operating system
- Mission ID you were trying to start

---

## Error Message Design Philosophy

TermGame error messages follow these principles:

1. **Clear Explanation** - "What's happening" section explains the issue
2. **Actionable Steps** - "How to fix" provides numbered steps
3. **Context** - Additional notes explain technical details
4. **Helpful Tips** - Suggestions for related issues or next steps
5. **No Jargon** - Plain language instead of technical errors
6. **Progressive Disclosure** - Simple message first, details in logs

We aim to make every error a learning opportunity, not a frustrating dead end.
