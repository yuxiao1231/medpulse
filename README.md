# <p align="center">⚕️ MedPulse</p>

<p align="center">
  <img src="logo.svg" width="128" height="128" alt="MedPulse Logo">
</p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
  <a href="https://developer.android.com"><img src="https://img.shields.io/badge/Platform-Android-green.svg"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Core-Python-blue.svg"></a>
</p>

<p align="center">
  <b>A hardcore, open-source frontline clinical calculation tool.</b><br>
  <i>"Write once, run anywhere" medical logic.</i>
  <br><br>
  <b>硬核开源的一线临床计算工具。</b><br>
  <i>“一次编写，多端运行” 的纯正医疗逻辑内核。</i>
</p>

---

## 🇺🇸 English

**MedPulse** is a robust, cross-platform medical calculator designed to assist clinicians in high-stress, rapid-decision environments (such as the ICU and ED). 

By strictly decoupling the complex, deterministic medical algorithms into a pure Python core (`medpulse/core`), the project ensures accuracy, testability, and portability. The UI layers are completely separate, seamlessly integrating the Python core into native desktop and mobile environments.

### 🛠 Key Features

- **"Write Once, Run Anywhere" Algorithms**
  All calculators (e.g., ABG interpretation, infusion rates, GCS, pediatrics) are implemented in pure Python and strictly unit-tested. If an algorithm changes, it automatically applies to all platforms.
- **Cross-Platform Interfaces**
  - **Desktop**: Powered by `Tkinter`, offering a fast, cross-platform native graphical interface.
  - **Android**: Powered by Jetpack Compose (edge-to-edge UI), directly bridged to the Python core via **Chaquopy**. No need to rewrite complex medical logic in Kotlin!
- **Extensible Data-Driven Checklists & Scores**
  Uses pure JSON structures to define emergency checklists, score criteria, and infusion templates natively in English, allowing easy global localization.
- **Zero Cloud Dependency**
  Calculations run 100% locally on the device, ensuring strict patient data privacy and zero-latency performance in offline hospital zones.

### 🚀 Getting Started

#### Desktop (Python/Tkinter)
Ensure you have Python 3.8+ installed.
```bash
# Clone the repository
git clone https://github.com/yourusername/medpulse.git
cd medpulse

# Run the desktop app
python -m medpulse.ui.windows.app
```

#### Android Build
Ensure the Android SDK is installed. Open the project in Android Studio, or build via Gradle:
```bash
cd forandroidbuild
./gradlew assembleRelease
```
*Note: The Gradle script automatically synchronizes the latest Python core into the Android APK assets during the build phase.*

---

## 🇨🇳 中文 (Chinese)

**MedPulse** 是一款强大的跨平台医学计算器，专为高压、快节奏的临床科室（如重症监护室 ICU、急诊 ED）的医生和护士设计。

通过将复杂、严密的医学计算算法彻底解耦成一个纯 Python 内核 (`medpulse/core`)，我们保证了算法的极度精确性、可测试性和可移植性。UI 显示层与逻辑层完全分离，通过桥接技术完美融入原生桌面和移动端系统。

### 🛠 核心亮点

- **“一次编写，到处运行”**
  所有计算逻辑（如：血气分析、微量泵泵速计算、GCS 评分、儿科补液）均由纯 Python 编写并进行了严格的单元测试。核心算法改动一处，双端自动生效！
- **跨平台原生界面**
  - **桌面端 (Desktop)**：采用 `Tkinter` 构建，提供轻量、跨平台的原生图形界面体验。
  - **安卓端 (Android)**：采用 Jetpack Compose (沉浸式 UI) 编写，通过 **Chaquopy** 将 Python 内核直接植入 Android。不需要用 Kotlin 重复造医学逻辑的轮子！
- **数据驱动的表单与评分系统**
  采用纯 JSON 数据结构定义急救核对表、评分标准和输液模板，底层完全基于英文设计，可轻松拓展并适配全球多语言（自带 `zh_CN.json` 完美支持中文）。
- **完全离线零依赖**
  100% 运行于设备本地，绝不向云端传输数据。不仅保障患者隐私，更能适应医院深区（无信号）等极端网络环境。

### 🚀 快速上手

#### 桌面端 (Python/Tkinter)
请确保你已安装 Python 3.8 及以上版本。
```bash
# 克隆代码库
git clone https://github.com/yourusername/medpulse.git
cd medpulse

# 运行桌面应用程序
python -m medpulse.ui.windows.app
```

#### 安卓端打包 (Android Build)
请确保安装了 Android SDK。你可以使用 Android Studio 打开项目，或者在终端执行 Gradle 构建：
```bash
cd forandroidbuild
./gradlew assembleRelease
```
*提示：Gradle 脚本会在构建阶段自动将最新的 Python 内核代码同步到 Android APK 资产目录中。*

---

## 📜 Acknowledgements & Licenses (开源协议与声明)

- **MedPulse** is licensed under the **MIT License**.
- The Android application utilizes [Chaquopy](https://chaquo.com/chaquopy/) to embed Python into the Android environment.
- Medical formulas are based on established clinical guidelines (e.g., AHA 2020, Sepsis-3, surviving sepsis campaign). *These tools are designed to augment, not replace, clinical judgment. / 这些工具旨在辅助而非替代临床决策。*