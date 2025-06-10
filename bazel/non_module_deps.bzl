"""
Module extension for non-module dependencies
"""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

def _non_module_deps_impl(ctx):
    http_archive(
        name = "opencv",
        sha256 = "9dc6a9a95edc133e165e9f6db9412dd899e28d4e5e4979f17cb5966f4b7f3fb1",
        strip_prefix = "opencv-4.8.0",
        url = "https://github.com/opencv/opencv/archive/4.8.0.zip",
        build_file = "//bazel:opencv.BUILD",
    )

non_module_deps_ext = module_extension(implementation = _non_module_deps_impl)
