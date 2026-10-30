<p align="center">
  <img src="docs/brand/artcraft-logo-white.svg" alt="ZETICA" width="380">
</p>

# Zetica Hub ⚡

<p align="center">
  <strong>Native desktop launcher, installer, and update manager for the ZETICA Creative Suite.</strong>
</p>

<p align="center">
  <a href="https://github.com/ZETIC7Z/craft-launcher/actions"><img src="https://img.shields.io/badge/Release-Passing-success.svg?style=flat-square" alt="Build Status"></a>
  <a href="LICENSE-MIT"><img src="https://img.shields.io/badge/License-MIT%20%2F%20Apache--2.0-blue.svg?style=flat-square" alt="License"></a>
  <a href="https://www.zeticuz.xyz/"><img src="https://img.shields.io/badge/Developed%20By-Sam%20Pangilinan-orange.svg?style=flat-square" alt="Sam Pangilinan"></a>
  <a href="https://zetica.xyz"><img src="https://img.shields.io/badge/Website-zetica.xyz-blueviolet.svg?style=flat-square" alt="Website"></a>
</p>

---

## ⚡ Overview

**Zetica Hub** is the lightweight, native desktop application designed to install, update, and manage the complete **ZETICA Creative Suite** (including **Zetica Motion**, **Zetica Photo**, **Zetica Vector**, **Zetica Film**, and more).

- **100% Native Rust Performance**: Built with `egui` and `eframe` for sub-50ms startup times, tiny memory footprint (<30 MB RAM), and smooth 60fps UI.
- **One-Click Installation**: Automatically resolves platform architectures (Windows x64/arm64, macOS universal, Linux AppImage/tarball) and handles updates silently or on-demand.
- **Privacy First & Open Source**: No cloud accounts required, no telemetry, no subscription lock-ins. Runs standalone and completely offline.

---

## 🎨 The Zetica Creative Suite

| App | Description | Repository |
|---|---|---|
| **Zetica Motion** | Motion graphics, visual effects, and 3D compositor in pure Rust | [ZETIC7Z/effectcraft](https://github.com/ZETIC7Z/effectcraft) |
| **Zetica Photo** | Non-destructive RAW & raster image editing with layer masks | [ZETIC7Z/photocraft](https://github.com/ZETIC7Z) |
| **Zetica Vector** | Precision vector illustration and parametric SVG design | [ZETIC7Z/vectorcraft](https://github.com/ZETIC7Z) |
| **Zetica Film** | Timeline video editing, multicam grading, and spatial audio | [ZETIC7Z/filmcraft](https://github.com/ZETIC7Z) |
| **Zetica Design** | Desktop publishing, typography layout, and export tools | [ZETIC7Z/designcraft](https://github.com/ZETIC7Z) |

---

## 🚀 Building from Source

Ensure you have Rust 1.85+ installed:

```bash
# Clone the repository
git clone https://github.com/ZETIC7Z/craft-launcher.git
cd craft-launcher

# Run in debug mode
cargo run -p artcraft-launcher

# Build release binary
cargo build --release -p artcraft-launcher
```

---

## 🔄 Automated Upstream Synchronization

This repository includes automated GitHub Actions workflows (`.github/workflows/sync-upstream.yml`) that continuously monitor upstream `storytold/craft-launcher` releases and commits, merging core engine improvements while maintaining full **ZETICA** brand identity.

---

## 📄 License & Credits

- Maintained and developed by **Sam Pangilinan** ([zeticuz.xyz](https://www.zeticuz.xyz/)).
- Dual-licensed under the [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE) license at your option.
- Core architecture based on open-source foundations from the ArtCraft project under MIT/Apache-2.0. All trademarks and brand assets replaced with official ZETICA designs.
