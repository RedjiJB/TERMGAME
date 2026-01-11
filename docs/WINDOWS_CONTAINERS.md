# Windows Containers for PowerShell Missions

PowerShell missions in TermGame run in Windows Server Core containers, which require special Docker Desktop configuration.

## Prerequisites

- **Windows 10/11 Pro, Enterprise, or Education** (Windows Home does NOT support Windows containers)
- **Docker Desktop for Windows** (latest version)
- **Hyper-V enabled** (required for Windows containers)
- **Approximately 10-15 GB free disk space** (Windows container images are large)

## Quick Setup

### 1. Switch Docker to Windows Containers Mode

Docker Desktop can run either Linux OR Windows containers, but not both simultaneously.

**Steps:**
1. Right-click the Docker Desktop icon in the system tray
2. Select **"Switch to Windows containers..."**
3. Click **"Switch"** in the confirmation dialog
4. Wait for Docker to restart (this may take 1-2 minutes)

![Switch to Windows Containers](https://docs.docker.com/desktop/images/switch-to-windows-containers.png)

### 2. Pull the Windows Server Core Image

The first time you run a PowerShell mission, Docker will pull the Windows Server Core image. This is a ~5-10 GB download and may take 10-30 minutes depending on your internet connection.

**Manual pull (recommended):**
```bash
docker pull mcr.microsoft.com/windows/servercore:ltsc2022
```

**What to expect:**
```
ltsc2022: Pulling from windows/servercore
4612f6d0b889: Downloading [============>      ]  1.234GB/5.123GB
a3ed95caeb02: Download complete
...
```

### 3. Verify Windows Containers

```bash
# Check Docker is in Windows containers mode
docker version

# Should show:
# Server:
#  OS/Arch:          windows/amd64

# List available Windows images
docker images

# Should show mcr.microsoft.com/windows/servercore
```

## Running PowerShell Missions

Once Windows containers are configured:

```bash
# Start TermGame
termgame tui

# List all missions (Linux and PowerShell)
> list

# Start a PowerShell mission
> start powershell/basics/hello-powershell
```

## Switching Between Linux and PowerShell Missions

### To Run Linux Missions:
1. Right-click Docker Desktop icon
2. Select **"Switch to Linux containers..."**
3. Wait for restart
4. Linux missions will now work

### To Run PowerShell Missions:
1. Right-click Docker Desktop icon
2. Select **"Switch to Windows containers..."**
3. Wait for restart
4. PowerShell missions will now work

**Note:** You cannot run both Linux and PowerShell missions simultaneously. You must switch Docker Desktop's container mode.

## Common Issues

### Issue: "Image not found: mcr.microsoft.com/windows/servercore:ltsc2022"

**Cause:** Docker is in Linux containers mode

**Solution:**
```bash
1. Switch to Windows containers (see above)
2. Pull the image: docker pull mcr.microsoft.com/windows/servercore:ltsc2022
3. Try the mission again
```

### Issue: "This system does not support Windows containers"

**Cause:** Running Windows Home or missing Hyper-V

**Solutions:**
- **Windows Home:** Upgrade to Windows Pro/Enterprise/Education
- **Missing Hyper-V:** Enable it via Control Panel → Programs → Turn Windows features on/off → Hyper-V

### Issue: Container startup is very slow (30-60 seconds)

**This is normal!** Windows containers take longer to start than Linux containers due to:
- Larger image size (5-10 GB vs 50-200 MB for Linux)
- Windows kernel initialization
- PowerShell environment setup

**Expected startup times:**
- Linux containers: 1-3 seconds
- Windows containers: 30-60 seconds (first time), 15-30 seconds (subsequent runs)

### Issue: "Failed to pull image" or download errors

**Possible causes:**
1. **Internet connection issues** - Check your connection
2. **Corporate proxy/firewall** - Configure Docker to use your proxy
3. **Disk space** - Ensure 10-15 GB free space
4. **Docker Hub rate limiting** - Wait a few minutes and try again

**Solutions:**
```bash
# Check disk space
docker system df

# Clean up unused images if needed
docker system prune -a

# Retry the pull
docker pull mcr.microsoft.com/windows/servercore:ltsc2022
```

## Performance Optimization

### Keep Windows Containers Mode If Using PowerShell Primarily

If you're primarily working through PowerShell missions:
1. Stay in Windows containers mode
2. Pre-pull the image before starting missions
3. Don't switch back to Linux containers unless needed

### Pre-pull All Mission Images

```bash
# Pull the main Windows Server Core image
docker pull mcr.microsoft.com/windows/servercore:ltsc2022

# This single image is used for ALL PowerShell missions
```

### Allocate More Resources to Docker Desktop

Windows containers benefit from more resources:

1. Open Docker Desktop → Settings → Resources
2. Increase:
   - **CPUs:** 4 or more (recommended)
   - **Memory:** 4 GB or more (recommended)
   - **Disk image size:** 60 GB or more (required for Windows containers)

## Image Size Comparison

| Platform | Image | Size | Pull Time (100 Mbps) |
|----------|-------|------|---------------------|
| Linux | ubuntu:22.04 | ~77 MB | ~10 seconds |
| Linux | alpine:latest | ~7 MB | ~2 seconds |
| Windows | servercore:ltsc2022 | ~5-10 GB | ~10-30 minutes |

## FAQ

### Q: Can I run both Linux and PowerShell missions at the same time?

**A:** No. Docker Desktop for Windows runs in either Linux containers mode OR Windows containers mode, not both simultaneously. You must switch modes to run different mission types.

### Q: Do I need Windows Pro/Enterprise for PowerShell missions?

**A:** Yes. Windows Home does not support Hyper-V or Windows containers. You need Windows 10/11 Pro, Enterprise, or Education.

### Q: Why are Windows containers so large?

**A:** Windows containers include the Windows Server Core operating system, which provides the full Windows API, Registry, PowerShell, and all Windows features. Linux containers can be minimal because they share the Linux kernel with the host.

### Q: Can I use WSL2 for PowerShell missions instead of Windows containers?

**A:** No. WSL2 runs Linux, and PowerShell in WSL2 is PowerShell Core (cross-platform), not Windows PowerShell. PowerShell missions require true Windows features like:
- Windows Registry
- BitLocker
- Windows Services
- Active Directory cmdlets
- SMB file shares
- Windows-specific ACLs

These features are only available in real Windows containers.

### Q: Will my PC slow down with Windows containers?

**A:** Windows containers use Hyper-V isolation, which requires dedicated resources. Your PC may be slower while containers are running, especially if you have limited RAM (less than 8 GB). Recommended system specs:
- 8 GB+ RAM
- 4+ CPU cores
- SSD storage
- 50+ GB free disk space

## Troubleshooting Checklist

Before starting PowerShell missions:

- [ ] Running Windows 10/11 Pro/Enterprise/Education (not Home)
- [ ] Docker Desktop installed and running
- [ ] Docker in Windows containers mode
- [ ] Windows Server Core image pulled (`docker images` shows it)
- [ ] At least 10 GB free disk space
- [ ] Docker allocated 4+ GB RAM and 4+ CPUs

## Additional Resources

- [Docker Desktop for Windows documentation](https://docs.docker.com/desktop/install/windows-install/)
- [Windows Container Documentation](https://docs.microsoft.com/en-us/virtualization/windowscontainers/)
- [Windows Server Core Container Images](https://hub.docker.com/_/microsoft-windows-servercore)
- [Hyper-V on Windows 10/11](https://docs.microsoft.com/en-us/virtualization/hyper-v-on-windows/)

## Getting Help

If you encounter issues not covered here:

1. Check Docker Desktop logs: Settings → Troubleshoot → View logs
2. Run diagnostics: `docker system info`
3. File an issue: [GitHub Issues](https://github.com/RedjiJB/TERMGAME/issues)
4. Include in your report:
   - Windows version (`winver`)
   - Docker version (`docker version`)
   - Error messages
   - Steps to reproduce
