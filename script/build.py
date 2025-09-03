#! /usr/bin/env python3

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
  else:
    args = ['is_official_build=true']

  # Game engine optimized configuration
  args += [
    'target_cpu="' + machine + '"',
    # System dependencies - use system libraries where possible to reduce size
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
    
    # Gaming specific optimizations
    'skia_enable_skottie=true',           # Keep for animations
    'skia_enable_sksl=true',              # Keep for shaders
    'skia_enable_gpu=true',               # Essential for games
    'skia_use_gl=true',                   # OpenGL support
    'skia_use_vulkan=true',               # Vulkan support for better performance
    
    # Reduce binary size - disable features not needed for games
    'skia_enable_tools=false',            # No development tools
    'skia_enable_ccpr=false',             # Disable coverage counting path renderer
    'skia_enable_skrive=false',           # Disable Skrive (experimental feature)
    'skia_enable_particles=false',        # Disable particles system (use game engine's instead)
    'skia_use_dawn=false',                # Disable Dawn WebGPU backend
    'skia_enable_discrete_gpu=true',      # Prefer discrete GPU
    
    # Image format optimizations
    'skia_use_libheif=false',             # Disable HEIF support
    'skia_use_wuffs=true',                # Use Wuffs for better performance
    'skia_use_dng_sdk=false',             # No RAW image support needed
    'skia_use_libraw=false',
    
    # Text/Font optimizations
    'skia_enable_fontmgr_FontConfigInterface=false',  # Reduce font manager complexity
    'skia_enable_fontmgr_custom_directory=true',      # Custom font loading for games
    'skia_enable_fontmgr_custom_embedded=true',       # Embedded fonts support
    'skia_enable_fontmgr_custom_empty=false',
    
    # Performance optimizations
    'skia_use_perfetto=false',            # Disable profiling overhead
    'skia_enable_winuwp=false',           # No UWP support needed
  ]

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
            'extra_cflags_cc=["-fno-exceptions", "-fno-rtti", "-flax-vector-conversions=all", "-D_GLIBCXX_USE_CXX11_ABI=0"]',
            'cc="clang"',
            'cxx="clang++"',
        ]
    else:
        args += [
            'extra_cflags_cc=["-fno-exceptions", "-fno-rtti","-D_GLIBCXX_USE_CXX11_ABI=0"]',
            'cc="gcc-9"',
            'cxx="g++-9"',
        ]
  elif 'windows' == target:
    args += [
      'skia_use_direct3d=true',             # Enable D3D on Windows
      'skia_use_vulkan=true',               # Also keep Vulkan for Windows
      'extra_cflags=["-DSK_FONT_HOST_USE_SYSTEM_SETTINGS"]',
    ]
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
    # brew install emscripten binaryen llvm nodejs
    # echo "BINARYEN_ROOT = '/usr/local'" >> ~/.emscripten
    # echo "LLVM_ROOT = '/opt/homebrew/opt/llvm/bin'" >> ~/.emscripten
    # echo "NODE_JS = '/opt/homebrew/bin/node'" >> ~/.emscripten

    # Game engine optimized WASM build
    args += [
        # Essential image formats for games
        'skia_use_dng_sdk=false',
        'skia_use_libjpeg_turbo_decode=true',
        'skia_use_libjpeg_turbo_encode=true',
        'skia_use_libpng_decode=true',
        'skia_use_libpng_encode=true',
        'skia_use_libwebp_decode=true',
        'skia_use_libwebp_encode=true',
        'skia_use_wuffs=true',
        
        # Disable unused features for smaller binary
        'skia_use_lua=false',                     # No Lua scripting
        'skia_use_piex=false',                    # No RAW preview
        'skia_enable_tools=false',                # No development tools
        'skia_enable_ccpr=false',                 # Disable coverage counting
        'skia_enable_particles=false',            # Use game engine particles
        
        # Graphics backends
        'skia_use_webgl=true',
        'skia_gl_standard="webgl"',
        'skia_use_gl=true',
        'skia_enable_gpu=true',
        
        # Text rendering
        'skia_enable_fontmgr_custom_directory=false',
        'skia_enable_fontmgr_custom_embedded=true',   # Embedded fonts for games
        'skia_enable_fontmgr_custom_empty=true',
        
        # System integrations
        'skia_use_system_libpng=false',
        'skia_use_system_freetype2=false',
        'skia_use_system_libjpeg_turbo=false',
        'skia_use_system_libwebp=false',
        
        # Keep essential features
        'skia_enable_svg=true',                   # SVG support for UI
        'skia_use_expat=true',                    # XML parsing for SVG
        'skia_enable_skottie=true',               # Animations
        'skia_enable_sksl=true',                  # Shaders
        
        # Optimization flags for smaller binary and better performance
        'extra_cflags=["-DSK_SUPPORT_GPU=1", "-DSK_GL", "-DSK_DISABLE_LEGACY_SHADERCONTEXT", "-sSUPPORT_LONGJMP=wasm", "-Os", "-DNDEBUG"]'
    ]

  if 'linux' == host and 'arm64' == host_machine:
    tools_dir = 'tools'
    ninja = 'ninja-linux-arm64'

  out = os.path.join('out', build_type + '-' + target + '-' + machine)
  gn = 'gn.exe' if 'windows' == host else 'gn'
  print([os.path.join('bin', gn), 'gen', out, '--args=' + ' '.join(args)])
  subprocess.check_call([os.path.join('bin', gn), 'gen', out, '--args=' + ' '.join(args)])
  subprocess.check_call([os.path.join('..', tools_dir, ninja), '-C', out, 'skia', 'modules'])

  return 0

if __name__ == '__main__':
  sys.exit(main())
