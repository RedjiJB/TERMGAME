# Docker Setup for TermGame

## Quick Start

To ensure all commands like `nano`, `vim`, compression tools, and other essentials are available in all missions:

### 1. Build the Enhanced Docker Image

```bash
# From the TermGame root directory
docker build -f docker/Dockerfile.ubuntu-full -t termgame/ubuntu-full:latest .
```

Or use the build script:
```bash
chmod +x docker/build-image.sh
./docker/build-image.sh
```

This takes 2-5 minutes the first time but only needs to be done once.

### 2. Verify the Image

```bash
docker run --rm termgame/ubuntu-full:latest bash -c "
    echo 'Testing essential commands...'
    which nano vim && echo '✓ Text editors found'
    which gzip tar && echo '✓ Compression tools found'
    which curl wget && echo '✓ Network tools found'
    man --version > /dev/null && echo '✓ Man pages available'
    echo 'All tools ready!'
"
```

### 3. Use TermGame

Now all missions will have access to all essential commands automatically!

```bash
# Start TermGame interactive mode
python -m termgame.interactive

# Or use the CLI
python -m termgame.cli list
```

## What's Included

The `termgame/ubuntu-full:latest` image includes:

✅ **Text Editors**: nano, vim
✅ **File Tools**: tree, ncdu, file
✅ **Compression**: gzip, bzip2, xz-utils, zip, unzip, tar
✅ **Network**: curl, wget, ssh, ping, dig, netstat
✅ **Process Management**: htop, ps, top, kill, nice
✅ **Text Processing**: grep, sed, awk, cut, sort, uniq, wc
✅ **Documentation**: man pages, info pages
✅ **Development**: git, make, bc, python3
✅ **Disk Utilities**: parted, fdisk, df, du
✅ **Automation**: cron
✅ **User**: learner user with sudo access

## Troubleshooting

### "Image not found" error

Build the image first:
```bash
docker build -f docker/Dockerfile.ubuntu-full -t termgame/ubuntu-full:latest .
```

### Commands still not found in missions

Make sure the image built successfully and that missions are using `termgame/ubuntu-full:latest` as their base image. Check mission YAML files should have:

```yaml
environment:
  image: "termgame/ubuntu-full:latest"
```

### Using Podman instead of Docker

Replace `docker` with `podman` in all commands:
```bash
podman build -f docker/Dockerfile.ubuntu-full -t termgame/ubuntu-full:latest .
```

## Advanced: Publishing the Image (Optional)

To share the image via Docker Hub:

```bash
# Login to Docker Hub
docker login

# Tag and push
docker tag termgame/ubuntu-full:latest yourusername/termgame-ubuntu:latest
docker push yourusername/termgame-ubuntu:latest
```

## Performance Notes

- **First build**: 2-5 minutes (downloads and installs all packages)
- **Subsequent missions**: Instant (no package installation needed)
- **Disk space**: ~500MB (vs ~100MB for minimal Ubuntu)
- **Worth it**: Yes! Saves time and prevents connection errors

## Migration (Optional)

To update existing missions to remove redundant package installations:

Most missions will automatically benefit from the enhanced image. If you created custom missions, you can simplify their setup sections by removing package installations since everything is already included.
