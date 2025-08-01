load("@rules_python//python:defs.bzl", "py_binary")

py_binary(
    name = "sbl_ci",
    srcs = ["sbl_ci.py"],
    srcs_version = "PY3",
    deps = [
        "@ai_intrinsic_sdks//intrinsic/solutions:deployments",
        "@ai_intrinsic_sdks//intrinsic/solutions:solutions_lib",
    ],
)
