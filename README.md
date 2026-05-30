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
</p>

---

**MedPulse** is a robust, cross-platform medical calculator designed to assist clinicians in high-stress, rapid-decision environments (such as the ICU and ED). 

By strictly decoupling the complex, deterministic medical algorithms into a pure Python core (`medpulse/core`), the project ensures accuracy, testability, and portability. The UI layers are completely separate, seamlessly integrating the Python core into native desktop and mobile environments.

## 🛠 Key Features

- **"Write Once, Run Anywhere" Algorithms**
  All calculators (e.g., ABG interpretation, infusion rates, GCS, pediatrics) are implemented in pure Python and strictly unit-tested. If an algorithm changes, it automatically applies to all platforms.
- **Cross-Platform Interfaces**
  - **Desktop**: Powered by `Tkinter`, offering a fast, cross-platform native graphical interface.
  - **Android**: Powered by Jetpack Compose (edge-to-edge UI), directly bridged to the Python core via **Chaquopy**. No need to rewrite complex medical logic in Kotlin!
- **Extensible Data-Driven Checklists & Scores**
  Uses pure JSON structures to define emergency checklists, score criteria, and infusion templates natively in English, allowing easy global localization.
- **Zero Cloud Dependency**
  Calculations run 100% locally on the device, ensuring strict patient data privacy and zero-latency performance in offline hospital zones.

## 🚀 Getting Started

### Desktop (Python/Tkinter)
Ensure you have Python 3.8+ installed.
```bash
# Clone the repository
git clone https://github.com/yourusername/medpulse.git
cd medpulse

# Run the desktop app
python -m medpulse.ui.windows.app
```

### Android Build
Ensure the Android SDK is installed. Open the project in Android Studio, or build via Gradle:
```bash
cd forandroidbuild
./gradlew assembleRelease
```
*Note: The Gradle script automatically synchronizes the latest Python core into the Android APK assets during the build phase.*

## 📜 Acknowledgements & Licenses

- **MedPulse** is licensed under the **MIT License**.
- The Android application utilizes [Chaquopy](https://chaquo.com/chaquopy/) to embed Python into the Android environment.
- Medical formulas are based on established clinical guidelines (e.g., AHA 2020, Sepsis-3, surviving sepsis campaign). *These tools are designed to augment, not replace, clinical judgment.*