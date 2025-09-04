#! /usr/bin/env python3

# Skia构建脚本
# 支持轻量级Debug模式以减小体积:
#   正常Debug构建: python build.py
#   轻量级Debug构建: SKIA_LITE_DEBUG=1 python build.py
# 
# 轻量级Debug模式会：
# - 禁用性能追踪功能 (减少约100-150MB)
# - 禁用开发工具 (减少约50-100MB)  
# - 启用体积优化 (减少约20-30%)
# - 保留调试符号 (可正常调试)

import common, os, shutil, subprocess, sys

def main():
  os.chdir(os.path.join(os.path.dirname(__file__), os.pardir, 'skia'))

  build_type = common.build_type()
  machine = common.machine()
  host = common.host()
  host_machine = common.host_machine()
  target = common.target()
  ndk = common.ndk()

  tools_dir = "depot_tools"
  ninja = 'ninja.bat' if 'windows' == host else 'ninja'
  isIos = 'ios' == target or 'iosSim' == target
  isTvos = 'tvos' == target or 'tvosSim' == target
  isIosSim = 'iosSim' == target
  isTvosSim = 'tvosSim' == target
  isMacos = 'macos' == target

  if build_type == 'Debug':
    args = ['is_debug=true']
    # Debug-specific game engine configuration
    # 可通过环境变量 SKIA_LITE_DEBUG=1 启用轻量级Debug模式减小体积
    lite_debug = os.getenv('SKIA_LITE_DEBUG', '0') == '1'
    
    if lite_debug:
      # 轻量级Debug配置 - 保留核心调试功能但减小体积
      debug_optimizations = [
        'skia_disable_tracing=true',         # 禁用追踪减小体积
        'skia_enable_tools=false',           # 禁用开发工具减小体积
        'skia_enable_optimize_size=true',    # 启用体积优化
        'skia_enable_precompile=false',      # 保持调试友好性
        'strip_debug_info=false',            # 保留调试符号
      ]
    else:
      # 完整Debug配置 - 最佳调试体验
      debug_optimizations = [
        'skia_disable_tracing=false',        # Keep tracing for debugging
        'skia_enable_tools=true',            # Enable debug tools
        'skia_enable_optimize_size=false',   # Still optimize for performance
        'skia_enable_precompile=false',      # No precompilation to aid debugging
      ]
  else:
    args = ['is_official_build=true']
    # Release-specific game engine configuration  
    debug_optimizations = [
      'skia_disable_tracing=true',         # Remove tracing overhead in production
      'skia_enable_tools=false',           # No development tools in release
      'skia_enable_optimize_size=false',   # Optimize for performance, not size
      'skia_enable_precompile=true',       # Precompile shaders for better performance
    ]

  # Game engine optimized configuration - performance focused
  args += [
    'target_cpu="' + machine + '"',
    
    # System dependencies - standard Skia configuration
    'skia_use_system_expat=false',
    'skia_use_system_libjpeg_turbo=false',
    'skia_use_system_libpng=false',
    'skia_use_system_libwebp=false',
    'skia_use_system_zlib=false',
    'skia_use_sfntly=false',
    'skia_use_system_freetype2=false',
    'skia_use_system_harfbuzz=false',
    'skia_pdf_subset_harfbuzz=true',
    'skia_use_system_icu=false',
    
    # Essential game engine features (same for Debug and Release)
    'skia_enable_skottie=true',           # Animation support
    'skia_enable_ganesh=true',            # Modern GPU backend (Ganesh)
    'skia_enable_graphite=false',         # Disable experimental Graphite backend
    
    # Features games typically don't need (same for Debug and Release)
    'skia_use_dawn=false',                # No WebGPU backend needed
    'skia_use_lua=false',                 # No Lua scripting
  ]
  
  # Add Debug/Release specific optimizations
  args += debug_optimizations

  if isMacos or isIos or isTvos:
    if isMacos:
        args += ['skia_use_fonthost_mac=true']
    args += ['extra_cflags_cc=["-frtti"]']
    args += ['skia_use_metal=true']
    if isIos:
      args += ['target_os="ios"']
      if isIosSim:
        args += ['ios_use_simulator=true']
        args += ['extra_cflags=["-mios-simulator-version-min=12.0"]']
      else:
        args += ['ios_min_target="12.0"']
    else:
      if isTvos:
        args += ['target_os="tvos"']
        # Metal needs tvOS version 14 and SK_BUILD_FOR_TVOS to skip legacy iOS checks
        if isTvosSim:
          args += ['ios_use_simulator=true']
          args += ['extra_cflags=["-mtvos-simulator-version-min=14", "-DSK_BUILD_FOR_TVOS"]']
        else:
          args += ['extra_cflags=["-mtvos-version-min=14", "-DSK_BUILD_FOR_TVOS"]'] 
      else:
        if 'arm64' == machine:
          args += ['extra_cflags=["-stdlib=libc++"]']
        else:
          args += ['extra_cflags=["-stdlib=libc++", "-mmacosx-version-min=10.13"]']
  elif 'linux' == target:
    if 'arm64' == machine:
        # TODO: use clang on all targets!
        args += [
            'skia_gl_standard="gles"',
            'skia_use_gl=true',                   # OpenGL ES for ARM64
            'skia_enable_discrete_gpu=true',      # Prefer discrete GPU
            'extra_cflags_cc=["-fno-exceptions", "-fno-rtti", "-flax-vector-conversions=all", "-D_GLIBCXX_USE_CXX11_ABI=0"]',
            'cc="clang"',
            'cxx="clang++"',
        ]
    else:
        args += [
            'skia_use_gl=true',                   # OpenGL support
            'skia_use_vulkan=true',               # Vulkan for better performance on x64
            'skia_enable_discrete_gpu=true',      # Prefer discrete GPU
            'extra_cflags_cc=["-fno-exceptions", "-fno-rtti","-D_GLIBCXX_USE_CXX11_ABI=0"]',
            'cc="gcc"',
            'cxx="g++"',
        ]
  elif 'windows' == target:
    args += [
      'skia_use_direct3d=true',             # Direct3D 12 for Windows
      'skia_use_gl=true',                   # Also enable OpenGL
      'skia_use_vulkan=true',               # Vulkan support for high performance
      'skia_enable_discrete_gpu=true',      # Prefer discrete GPU
    ]
    # Windows runtime library configuration
    if build_type == 'Debug':
      args += ['extra_cflags=["-DSK_FONT_HOST_USE_SYSTEM_SETTINGS", "/MDd", "-D_ITERATOR_DEBUG_LEVEL=2"]']
    else:
      args += ['extra_cflags=["-DSK_FONT_HOST_USE_SYSTEM_SETTINGS", "/MD", "-D_ITERATOR_DEBUG_LEVEL=0"]']
    if 'windows' == host:
      clang_path = shutil.which('clang-cl.exe')
      if not clang_path:
        raise Exception("Please install LLVM from https://releases.llvm.org/, and make sure that clang-cl.exe is available in PATH")
      args += [
        'clang_win="' + os.path.dirname(os.path.dirname(clang_path)) + '"',
        'is_trivial_abi=false',
      ]
  elif 'android' == target:
    args += [
      'ndk="'+ ndk + '"'
    ]
  elif 'wasm' == target:
    # Game engine optimized WebAssembly build
    args += [
        # Essential image formats for games
        'skia_use_dng_sdk=false',
        'skia_use_libjpeg_turbo_decode=true',
        'skia_use_libjpeg_turbo_encode=true',
        'skia_use_libpng_decode=true',
        'skia_use_libpng_encode=true',
        'skia_use_libwebp_decode=true',
        'skia_use_libwebp_encode=true',
        'skia_use_wuffs=true',                    # Fast image decoding
        
        # Disable unused features
        'skia_use_lua=false',                     # No Lua scripting
        'skia_use_piex=false',                    # No RAW image support
        'skia_enable_tools=false',                # No dev tools
        
        # Graphics optimization for games
        'skia_use_webgl=true',
        'skia_gl_standard="webgl"',
        'skia_use_gl=true',
        'skia_enable_ganesh=true',                # GPU backend
        'skia_enable_discrete_gpu=true',          # Prefer discrete GPU
        
        # Text rendering for games
        'skia_enable_fontmgr_custom_directory=false',
        'skia_enable_fontmgr_custom_embedded=true',   # Embedded fonts
        'skia_enable_fontmgr_custom_empty=true',
        
        # System library configuration
        'skia_use_system_libpng=false',
        'skia_use_system_freetype2=false',
        'skia_use_system_libjpeg_turbo=false',
        'skia_use_system_libwebp=false',
        
        # Game engine essentials
        'skia_enable_svg=true',                   # SVG for UI
        'skia_use_expat=true',                    # XML parsing
        'skia_enable_skottie=true',               # Animations
        
        # Performance optimizations for WASM
        'extra_cflags=["-DSK_SUPPORT_GPU=1", "-DSK_GL", "-DSK_DISABLE_LEGACY_SHADERCONTEXT", "-sSUPPORT_LONGJMP=wasm", "-O3"]'
    ]

  if 'linux' == host and 'arm64' == host_machine:
    tools_dir = 'tools'
    ninja = 'ninja-linux-arm64'

  out = os.path.join('out', build_type + '-' + target + '-' + machine + '-v4')
  gn = 'gn.exe' if 'windows' == host else 'gn'
  print([os.path.join('bin', gn), 'gen', out, '--args=' + ' '.join(args)])
  subprocess.check_call([os.path.join('bin', gn), 'gen', out, '--args=' + ' '.join(args)])
  subprocess.check_call([os.path.join('..', tools_dir, ninja), '-C', out, 'skia', 'modules'])

  return 0

if __name__ == '__main__':
  sys.exit(main())
