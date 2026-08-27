# SiYuan Note - Modified Version

This repository contains modified builds of [SiYuan Note](https://github.com/siyuan-note/siyuan), focusing on Linux, Windows, macOS, iOS, Android, and Docker server deployments. Linux and Windows desktop builds are available for both x86-64 and ARM64.

## Downloads

| OS | Architecture | Package Type | Download |
|----|--------------|--------------|----------|
| Linux | x86_64 | tar.gz | [siyuan-latest-linux.tar.gz](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-linux.tar.gz) |
| Linux | x86_64 | AppImage | [siyuan-latest-linux.AppImage](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-linux.AppImage) |
| Linux | x86_64 | DEB | [siyuan-latest-amd64.deb](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-amd64.deb) |
| Linux | x86_64 | RPM | [siyuan-latest-linux.rpm](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-linux.rpm) |
| Linux | ARM64 | tar.gz | [siyuan-latest-linux-arm64.tar.gz](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-linux-arm64.tar.gz) |
| Linux | ARM64 | AppImage | [siyuan-latest-linux-arm64.AppImage](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-linux-arm64.AppImage) |
| Linux | ARM64 | DEB | [siyuan-latest-arm64.deb](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-arm64.deb) |
| Linux | ARM64 | RPM | [siyuan-latest-linux-arm64.rpm](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-linux-arm64.rpm) |
| Linux (Arch) | x86_64 | pkg.tar.zst | [siyuan-latest-archlinux-x86_64.pkg.tar.zst](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-archlinux-x86_64.pkg.tar.zst) |
| Linux (Arch) | ARM64 | pkg.tar.zst | [siyuan-latest-archlinux-aarch64.pkg.tar.zst](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-archlinux-aarch64.pkg.tar.zst) |
| Windows | x86_64 | EXE | [siyuan-latest-win.exe](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-win.exe) |
| Windows | ARM64 | EXE | [siyuan-latest-win-arm64.exe](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-win-arm64.exe) |
| macOS | x86_64 | DMG | [siyuan-latest-mac.dmg](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-mac.dmg) |
| macOS | ARM64 | DMG | [siyuan-latest-mac-arm64.dmg](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-mac-arm64.dmg) |
| iOS | ARM64 | IPA | [siyuan-latest-ios.ipa](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-ios.ipa) |
| Android | ARM64 | APK | [siyuan-latest-android-arm64.apk](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-android-arm64.apk) |
| Docker | Multi-arch | Image | [docker pull melashri/siyuan:latest](https://hub.docker.com/r/melashri/siyuan) |

> Use `SHA256SUMS.txt` from the [latest release](https://github.com/MohamedElashri/siyuan-patch/releases/latest) to verify downloaded assets.

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

### Desktop Clients (macOS / Linux / Windows)
1. Navigate to the [Releases page](https://github.com/MohamedElashri/siyuan-patch/releases)
2. Download the appropriate version for your operating system

Linux releases include tar.gz, DEB, AppImage, RPM, and Arch Linux packages for x86-64 and ARM64. Use `SHA256SUMS.txt` from the release to verify downloaded assets.

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

2. Desktop Client Builds (macOS/Linux/Windows)
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
