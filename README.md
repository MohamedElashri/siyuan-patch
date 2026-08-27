# SiYuan Note - Modified Version

This repository contains modified builds of [SiYuan Note](https://github.com/siyuan-note/siyuan), focusing on Linux, Windows, macOS, iOS, Android, and Docker server deployments. Linux and Windows desktop builds are available for both x86-64 and ARM64.

## Downloads

<table>
<tr><th>OS</th><th>Architecture</th><th>Packages</th><th>Downloads</th></tr>
<tr>
  <td rowspan="4">Linux</td>
  <td>x86_64</td>
  <td>tar.gz, AppImage, DEB, RPM</td>
  <td>[tar.gz](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-linux.tar.gz)<br>[AppImage](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-linux.AppImage)<br>[DEB](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-amd64.deb)<br>[RPM](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-linux.rpm)</td>
</tr>
<tr>
  <td>ARM64</td>
  <td>tar.gz, AppImage, DEB, RPM</td>
  <td>[tar.gz](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-linux-arm64.tar.gz)<br>[AppImage](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-linux-arm64.AppImage)<br>[DEB](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-arm64.deb)<br>[RPM](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-linux-arm64.rpm)</td>
</tr>
<tr>
  <td>Arch x86_64</td>
  <td>pkg.tar.zst</td>
  <td>[pkg.tar.zst](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-archlinux-x86_64.pkg.tar.zst)</td>
</tr>
<tr>
  <td>Arch ARM64</td>
  <td>pkg.tar.zst</td>
  <td>[pkg.tar.zst](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-archlinux-aarch64.pkg.tar.zst)</td>
</tr>
<tr>
  <td rowspan="2">Windows</td>
  <td>x86_64</td>
  <td>EXE</td>
  <td>[EXE](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-win.exe)</td>
</tr>
<tr>
  <td>ARM64</td>
  <td>EXE</td>
  <td>[EXE](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-win-arm64.exe)</td>
</tr>
<tr>
  <td rowspan="2">macOS</td>
  <td>x86_64</td>
  <td>DMG</td>
  <td>[DMG](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-mac.dmg)</td>
</tr>
<tr>
  <td>ARM64</td>
  <td>DMG</td>
  <td>[DMG](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-mac-arm64.dmg)</td>
</tr>
<tr>
  <td>iOS</td>
  <td>ARM64</td>
  <td>IPA</td>
  <td>[IPA](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-ios.ipa)</td>
</tr>
<tr>
  <td>Android</td>
  <td>ARM64</td>
  <td>APK</td>
  <td>[APK](https://github.com/MohamedElashri/siyuan-patch/releases/latest/download/siyuan-latest-android-arm64.apk)</td>
</tr>
<tr>
  <td>Docker</td>
  <td>Multi-arch</td>
  <td>Image</td>
  <td>[docker pull melashri/siyuan:latest](https://hub.docker.com/r/melashri/siyuan)</td>
</tr>
</table>

> Use `SHA256SUMS.txt` from the [latest release](https://github.com/MohamedElashri/siyuan-patch/releases/latest) to verify downloaded assets.

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
