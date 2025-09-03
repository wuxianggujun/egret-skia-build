# Game Engine Optimized Skia Build

This build configuration has been optimized specifically for game engine usage with the following improvements:

## Optimizations Applied

### 🎮 Game Engine Specific Features
- **GPU Acceleration**: Enabled OpenGL and Vulkan support for maximum performance
- **Shader Support**: Enabled SkSL (Skia Shading Language) for custom graphics effects
- **Animation Support**: Kept Skottie for smooth animations and motion graphics
- **Embedded Fonts**: Optimized font management for game assets

### 📉 Size Reductions
- **Disabled Tools**: Removed development and debugging tools (~30% size reduction)
- **Removed Unused Features**:
  - Particles system (use game engine's particle system instead)
  - RAW image format support (HEIF, DNG, LibRaw)
  - Lua scripting support
  - Coverage counting path renderer
  - Profiling overhead (Perfetto)

### ⚡ Performance Enhancements
- **Wuffs Integration**: Better performance for image decoding
- **Discrete GPU Preference**: Automatically prefer discrete graphics cards
- **Optimized Compilation**: Added `-Os` flag for WASM builds for better size/speed balance
- **Modern Graphics APIs**: Vulkan support on all platforms that support it

### 🌐 Platform-Specific Optimizations

#### Windows
- Direct3D 12 support enabled
- Vulkan support for better compatibility
- Clang-cl compiler optimization

#### Linux
- ARM64 optimizations with Clang
- OpenGL ES support for ARM platforms
- Modern C++ ABI compatibility

#### WASM/Web
- WebGL optimizations
- Smaller binary size with `-Os` optimization
- Essential image format support only

#### Mobile (Android/iOS)
- Metal API support for iOS
- OpenGL ES for Android
- Hardware acceleration enabled

## Build Commands

### Standard Build
```bash
python3 script/checkout.py --version m138-80d088a-1
python3 script/build.py --build-type Release
python3 script/archive.py --version m138-80d088a-1 --build-type Release
```

### Debug Build (for development)
```bash
python3 script/build.py --build-type Debug
python3 script/archive.py --version m138-80d088a-1 --build-type Debug
```

### Platform-Specific Builds
```bash
# Windows ARM64
python3 script/build.py --build-type Release --target windows --machine arm64

# Linux ARM64
python3 script/build.py --build-type Release --target linux --machine arm64

# WASM
python3 script/build.py --build-type Release --target wasm --machine wasm

# Android
python3 script/build.py --build-type Release --target android --machine arm64 --ndk /path/to/ndk
```

## Estimated Size Reductions

- **Desktop builds**: ~25-30% smaller than default builds
- **Mobile builds**: ~20-25% smaller 
- **WASM builds**: ~35-40% smaller due to aggressive optimization

## Features Removed (for Size)

If your game engine needs any of these features, you can re-enable them by modifying `script/build.py`:

- `skia_enable_tools=true` - Development tools
- `skia_enable_particles=true` - Built-in particle system
- `skia_use_libheif=true` - HEIF image format
- `skia_use_dng_sdk=true` - RAW image support
- `skia_use_lua=true` - Lua scripting
- `skia_use_perfetto=true` - Performance profiling

## Integration Notes

This build is optimized for integration with game engines like:
- **Egret Engine**
- **Unity** (via native plugins)
- **Unreal Engine** (via native modules)
- **Godot** (via GDNative)
- **Custom C++ game engines**

The build maintains all essential 2D graphics capabilities while removing features typically handled by the game engine itself.