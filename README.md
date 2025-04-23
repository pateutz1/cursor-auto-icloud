# Cursor Pro (iCloud) Automation Tool - Free Trial Reset Tool

<div align="center">

[![Release](https://img.shields.io/github/v/release/ryan0204/cursor-auto-icloud?style=flat-square&logo=github&color=blue)](https://github.com/ryan0204/cursor-auto-icloud/releases/latest)
[![Stars](https://img.shields.io/github/stars/ryan0204/cursor-auto-icloud?style=flat-square&logo=github)](https://github.com/ryan0204/cursor-auto-icloud/stargazers)

## ⭐️ Give us a Star on GitHub — it's a great encouragement for us!

[🌏 中文 README](README-zh.md)

<img src="https://ai-cursor.com/wp-content/uploads/2024/09/logo-cursor-ai-png.webp" alt="Cursor Logo" width="120"/>

<img src="/assets/img/preview.png" alt="Tool Preview"/>

</div>

## Table of Contents

- [Prerequisites](#prerequisites)
- [Download](#download)
- [Setup](#setup)
- [Running the Tool](#running-the-tool)
- [Disclaimer](#disclaimer)
- [Acknowledgments](#acknowledgments)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

Before using this tool, you should have:

- An Apple account with **iCloud Plus** (email ending with @icloud.com)

## Download

1. Download the latest version from GitHub Releases
2. Choose the version according to your system:

> Windows: Download CursorKeepAlive.exe directly
> Mac (Intel): Choose x64 version
> Mac (M series): Choose ARM64(aarch64) version

### Additional Steps for Mac Users

> Open Terminal, navigate to the application directory
> Execute the following command to make the file executable:
> ```chmod +x ./CursorKeepAlive```

Follow the setup instructions below, then run

## Setup

### Setting Environment Variables

> Mac users: If you cannot rename the file, use `touch .env` to create the file in the same directory.

1. Download [`.env.example`](https://github.com/Ryan0204/cursor-auto-icloud/blob/main/.env.example) file and rename it to `.env`
2. Fill in the `.env` file

```env
ICLOUD_USER=Your Apple ID (!!! without @icloud.com)
ICLOUD_APP_PASSWORD=Your Apple ID app-specific password (explained below)
ICLOUD_COOKIES=Your iCloud cookies (explained below)
```

### Getting iCloud Cookie String

1. Download [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) Chrome extension
2. Go to [iCloud Settings](https://www.icloud.com/settings/) in your browser and log in
3. Click the Cookie-Editor extension and export cookies in `Header String` format
4. Paste the exported cookies into the `.env` file as `ICLOUD_COOKIES`

Cookie example:

```
X_APPLE_WEB_KB-V5590FJFX4ZYGBSJEZRZBTFB9UU="xxxxxx";X-APPLE-DS-WEB-SESSION-TOKEN="xxxxxx";X-APPLE-UNIQUE-CLIENT-ID="xxxxxx";X-APPLE-WEB-ID=28672BD9012631BA3CBAE022A1DBAEE2D0AFD358;X-APPLE-WEBAUTH-HSA-TRUST="xxxxxx";X-APPLE-WEBAUTH-LOGIN="xxxxxx";X-APPLE-WEBAUTH-PCS-Cloudkit="xxxxxx";X-APPLE-WEBAUTH-PCS-Documents="xxxxxx";X-APPLE-WEBAUTH-PCS-Mail="xxxxxx";X-APPLE-WEBAUTH-PCS-News="xxxxxx";X-APPLE-WEBAUTH-PCS-Notes="xxxxxx";X-APPLE-WEBAUTH-PCS-Photos="xxxxxx";X-APPLE-WEBAUTH-PCS-Safari="xxxxxx";X-APPLE-WEBAUTH-PCS-Sharing="xxxxxx";X-APPLE-WEBAUTH-TOKEN="xxxxxx";X-APPLE-WEBAUTH-USER="xxxxxx";X-APPLE-WEBAUTH-VALIDATE="xxxxxx";
```

### Getting Apple ID App-Specific Password

1. Log in to your Apple account at [account.apple.com](https://account.apple.com)
2. In the Sign-in and Security section, select App-Specific Passwords
3. Select Generate App-Specific Password and follow the on-screen instructions
4. Copy the generated password and paste it into the `.env` file as `ICLOUD_APP_PASSWORD`

## Running the Tool

### Windows Users

Double-click the executable file to run the tool.

### Mac Users

1. Open Terminal
2. Navigate to the directory containing the executable
3. Run `./CursorKeepAlive`

### Press `4` to start the automation process

## Disclaimer

This project is created for educational purposes only. The author assumes no responsibility or liability for:

- Any misuse of the code or related materials
- Any damages or legal consequences arising from the use of this project
- The accuracy, completeness, or usefulness of the provided content

By using this project, you agree that you do so at your own risk. This project is not intended for production use and comes with no warranties or guarantees.
If you have any legal or ethical concerns, please do not use this repository.

## Acknowledgments

This project would not have been possible without the help of these excellent projects:

- [cursor-auto-free](https://github.com/chengazhen/cursor-auto-free)
- [go-cursor-help](https://github.com/yuaotian/go-cursor-help)
- [hidemyemail-generator](https://github.com/rtunazzz/hidemyemail-generator)

## Contributing

If you'd like to contribute to this project, feel free to submit pull requests.

## License

This product is distributed under a proprietary license. You can view the complete license agreement at: [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/).
