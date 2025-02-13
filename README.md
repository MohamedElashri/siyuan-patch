# SiYuan Patch - Local VIP for [SiYuan Note](https://github.com/siyuan-note/siyuan)

## Modified Features

1. Local VIP features (official [`features`](https://b3log.org/siyuan/pricing.html)) including:
    - `Third-party S3 data sync and backup`
    - `Third-party WebDAV data sync and backup (excluding Nutstore)`
    - `Search resource file content`
    - `Add watermark to PDF/image exports`
2. **Disabled** `automatic update package downloads`
3. Google Analytics disabled by default
4. Auto-upload of error reports and diagnostic data disabled by default
5. Title bar display and VIP badge disabled by default
6. *Enabled* by default: `Minimize to system tray when clicking close button`

## How to Download Clients (Windows / Mac / Linux)

1. Go to [Release page](https://github.com/MohamedElashri/siyuan-patch/releases)

2. Download the version for your platform

## Docker Image

<https://hub.docker.com/r/melashri/siyuan/tags>

## Latest Version Updates

For the latest version, please follow the "How to Build" tutorial to build it yourself.

By default, it attempts to get and build the latest version every Tuesday and Friday at 20:00.

## How to Build

1. Fork this project to your own repository
2. For building Electron clients (Windows/Mac/Linux), no environment variables needed
3. For building Docker images:
    1. Go to `https://hub.docker.com/settings/security`, click `New Access Token`, save the token
    2. Go to your project's `settings`-`Secrets and variables`-`Actions`, click `New repository secret`
    3. Add `DOCKER_HUB_USER` - your Docker account name
    4. Add `DOCKER_HUB_PWD` - the saved token

4. Follow the operation shown in image, wait about 10 minutes then check the `Release` page
*(If the latest version already exists, you can delete it from the `Release` page and click again)*

## Mac "SiYuan.app is damaged" Error

If you see "SiYuan.app is damaged and can't be opened" error:

Download [Fix "damaged" error.zip](https://github.com/MohamedElashri/siyuan-patch/files/14783846/default.zip), unzip and run it, then reopen `SiYuan.app`
