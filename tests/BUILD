load("@rules_python//python:defs.bzl", "py_binary", "py_library")

py_library(
    name = "stopwatch_sbl_ci_test",
    srcs = ["stopwatch_sbl_ci_test.py"],
    srcs_version = "PY3",
    deps = [
        "@ai_intrinsic_sdks//intrinsic/solutions:deployments",
        "@ai_intrinsic_sdks//intrinsic/solutions:solutions_lib",
        "@com_google_absl_py//absl/logging",
    ],
)

py_library(
    name = "points_crud_sbl_ci_test",
    srcs = ["points_crud_sbl_ci_test.py"],
    srcs_version = "PY3",
    deps = [
        "//services/point_storage:point_storage_service_py_pb2",
        "//skills/points_crud:points_crud_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/solutions:deployments",
        "@ai_intrinsic_sdks//intrinsic/solutions:solutions_lib",
        "@com_google_absl_py//absl/logging",
    ],
)

py_binary(
    name = "sbl_ci",
    srcs = ["sbl_ci.py"],
    srcs_version = "PY3",
    deps = [
        ":points_crud_sbl_ci_test",
        ":stopwatch_sbl_ci_test",
        "@com_google_absl_py//absl/logging",
    ],
)
