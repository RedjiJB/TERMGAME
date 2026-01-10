# TermGame Docker Images

This directory contains Dockerfiles for building custom images used by TermGame missions.

## Ubuntu Full Image

The `termgame/ubuntu-full:latest` image is a complete Ubuntu 22.04 environment with all common tools pre-installed. This eliminates the need for package installation during mission setup and prevents connection timeouts.

### Included Packages

- **Text Editors**: nano, vim
- **File Utilities**: tree, ncdu, file
- **Compression Tools**: gzip, bzip2, xz-utils, zip, unzip, tar
- **Network Tools**: curl, wget, openssh-client, ping, traceroute, dig, netstat
- **Process Tools**: htop, ps, top, kill, killall, pgrep, pkill
- **Text Processing**: grep, sed, awk, cut, sort, uniq, wc
- **Documentation**: man-db, manpages, manpages-posix, info
- **Development Tools**: git, make, bc, build-essential, python3, pip
- **Disk Utilities**: parted, fdisk, df, du
- **System Utilities**: cron, sudo, findutils, coreutils
- **User Management**: learner user with sudo access (password: learner)

### Building the Image

#### With Podman (recommended):
```bash
cd docker
podman build -f Dockerfile.ubuntu-full -t termgame/ubuntu-full:latest .
```

#### With Docker:
```bash
cd docker
docker build -f Dockerfile.ubuntu-full -t termgame/ubuntu-full:latest .
```

#### Or use the PowerShell script:
```powershell
cd docker
.\build-images.ps1
```

### Using in Scenarios

Update your scenario YAML files to use the full image:

```yaml
environment:
  image: "termgame/ubuntu-full:latest"
  workdir: "/home/learner"
  setup:
    - "mkdir -p /home/learner"
```

This is much faster than:

```yaml
environment:
  image: "ubuntu:22.04"  # Minimal image
  workdir: "/home/learner"
  setup:
    - "apt-get update && apt-get install -y man-db vim tree ..."  # Slow!
    - "mkdir -p /home/learner"
```

### Benefits

1. **Faster Startup**: No package installation needed
2. **Reliable**: All tools guaranteed to be present
3. **No Connection Errors**: Fewer Docker API calls
4. **Consistent**: Same environment for all users

## Troubleshooting

### Image not found error

Make sure to build the image first:
```bash
podman build -f Dockerfile.ubuntu-full -t termgame/ubuntu-full:latest .
```

### Connection timeout errors

The Docker runtime now uses a 5-minute timeout (300 seconds) by default. If you still see timeouts, you can increase it in `src/termgame/runtimes/docker_runtime.py`:

```python
self._client = docker.DockerClient(base_url=base_url, timeout=600)  # 10 minutes
```

### Podman vs Docker

TermGame works with both Podman and Docker. If you're using Podman, all `docker` commands can be replaced with `podman` commands (they're compatible).
