# SiYuan Note - Modified Version

This repository contains modified builds of [SiYuan Note](https://github.com/siyuan-note/siyuan), focusing on Linux, macOS, iOS, and Docker server deployments. Windows and Android builds are not supported.

## Feature Modifications

### Enhanced Functionality
The modified version includes local access to premium features that typically require a VIP subscription in the official version. These features include:

- Support for third-party S3 storage for data synchronization and backup
- WebDAV integration for data synchronization and backup (excluding Nutstore)
- Full-text search capabilities for resource files
- PDF and image export with watermark functionality

### Privacy and Performance Enhancements
Several changes have been made to improve privacy and user experience:

- Automatic update downloads are disabled
- Google Analytics is disabled by default
- Error reporting and diagnostic data collection are disabled
- VIP badge and custom title bar displays are removed
- System tray minimization is enabled by default when clicking the close button

## Installation Guide

### Desktop Clients (macOS / Linux)
1. Navigate to the [Releases page](https://github.com/MohamedElashri/siyuan-patch/releases)
2. Download the appropriate version for your operating system

### Docker Deployment
Container images are available on Docker Hub:
```
docker pull melashri/siyuan:latest
```
Browse available tags at [Docker Hub](https://hub.docker.com/r/melashri/siyuan/tags)

## Building from Source

### Automated Builds
The repository automatically builds new versions every Tuesday and Friday at 20:00. For the most recent version, you can either:
- Download from the latest release
- Build from source following the instructions below

### Manual Build Instructions

1. Fork this repository to your GitHub account

2. Desktop Client Builds (macOS/Linux)
   - No additional configuration required
   - Proceed with the build workflow

3. Docker Image Builds
   - Generate a Docker Hub access token at https://hub.docker.com/settings/security
   - In your forked repository, navigate to Settings → Secrets and Variables → Actions
   - Add the following repository secrets:
     - `DOCKER_HUB_USER`: Your Docker Hub username
     - `DOCKER_HUB_PWD`: Your Docker Hub access token
   - Trigger the build workflow
   - Build process takes approximately 10 minutes

Note: If you need to rebuild an existing version, first delete it from the Releases page before triggering a new build.


## Troubleshooting

### macOS Security Warning
If you encounter the "SiYuan.app is damaged and can't be opened" error:

1. Download and run the fix script:
   ```bash
   curl -sSL https://raw.githubusercontent.com/MohamedElashri/siyuan-patch/refs/heads/main/fix_mac.sh | bash
   ```
2. Enter your password when prompted (it won’t be visible while typing).
3. Launch SiYuan.app again.

This will remove the macOS quarantine flag, allowing SiYuan to run normally.
