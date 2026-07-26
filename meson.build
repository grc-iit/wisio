project(
    'wisio',
    ['c', 'cpp'],
    version: '0.1.1',
    # Arrow's public headers use std::span, std::popcount and std::bit_width,
    # so c++20 is the floor for anything linking against libarrow (tools/).
    default_options: ['buildtype=debugoptimized', 'cpp_std=c++20', 'warning_level=3'],
)

cc = meson.get_compiler('c')
cpp = meson.get_compiler('cpp')

py = import('python').find_installation(pure: false)
py_dep = py.dependency()

subdir('wisio')

if get_option('enable_tools')
    subdir('tools')
endif