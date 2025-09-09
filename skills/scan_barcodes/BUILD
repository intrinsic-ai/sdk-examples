load("@ai_intrinsic_sdks//bazel:skills.bzl", "cc_skill", "py_skill", "skill_manifest")
load("@com_github_grpc_grpc//bazel:python_rules.bzl", "py_proto_library")
load("@com_google_protobuf//bazel:cc_proto_library.bzl", "cc_proto_library")
load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")
load("@rules_cc//cc:cc_library.bzl", "cc_library")
load("@rules_python//python:defs.bzl", "py_library", "py_test")
load("@scan_barcodes_pip_deps//:requirements.bzl", "requirement")

proto_library(
    name = "scan_barcodes_proto",
    srcs = ["scan_barcodes.proto"],
)

py_proto_library(
    name = "scan_barcodes_py_pb2",
    deps = [":scan_barcodes_proto"],
)

py_library(
    name = "scan_barcodes_py",
    srcs = ["scan_barcodes.py"],
    deps = [
        ":scan_barcodes_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/perception/python/camera:cameras",
        "@ai_intrinsic_sdks//intrinsic/skills/python:proto_utils",
        "@ai_intrinsic_sdks//intrinsic/skills/python:skill_interface",
        "@ai_intrinsic_sdks//intrinsic/util:decorators",
        "@com_google_absl_py//absl/logging",
        "@com_google_protobuf//:protobuf_python",
        requirement("numpy"),
        requirement("opencv-contrib-python-headless"),
        requirement("opencv-python-headless"),
    ],
)

skill_manifest(
    name = "scan_barcodes_py_manifest",
    src = "scan_barcodes_py.manifest.textproto",
    deps = [":scan_barcodes_proto"],
)

py_skill(
    name = "scan_barcodes_py_image",
    manifest = ":scan_barcodes_py_manifest",
    deps = [
        ":scan_barcodes_py",
        ":scan_barcodes_py_pb2",
    ],
)

py_test(
    name = "scan_barcodes_py_test",
    size = "small",
    srcs = ["scan_barcodes_test.py"],
    data = [
        "test/EAN-8_0123456.png",
    ],
    main = "scan_barcodes_test.py",
    deps = [
        ":scan_barcodes_py",
        "@rules_python//python/runfiles",
    ],
)

# Export for pip_parse repository rule
exports_files(["requirements.txt"])

cc_proto_library(
    name = "scan_barcodes_cc_proto",
    deps = [":scan_barcodes_proto"],
)

skill_manifest(
    name = "scan_barcodes_cc_manifest",
    src = "scan_barcodes_cc.manifest.textproto",
    deps = [":scan_barcodes_proto"],
)

cc_library(
    name = "scan_barcodes_cc",
    srcs = ["scan_barcodes.cc"],
    hdrs = ["scan_barcodes.h"],
    deps = [
        ":scan_barcodes_cc_proto",
        "@ai_intrinsic_sdks//intrinsic/perception/proto/v1:camera_config_cc_proto",
        "@ai_intrinsic_sdks//intrinsic/perception/proto/v1:camera_service_cc_grpc",
        "@ai_intrinsic_sdks//intrinsic/skills/cc:equipment_pack",
        "@ai_intrinsic_sdks//intrinsic/skills/cc:skill_interface",
        "@ai_intrinsic_sdks//intrinsic/skills/cc:skill_utils",
        "@ai_intrinsic_sdks//intrinsic/util/grpc",
        "@ai_intrinsic_sdks//intrinsic/util/status:status_conversion_grpc",
        "@ai_intrinsic_sdks//intrinsic/util/status:status_macros",
        "@com_google_absl//absl/log",
        "@com_google_absl//absl/status",
        "@com_google_absl//absl/status:statusor",
        "@com_google_protobuf//:protobuf",
        "@opencv",
    ],
)

cc_skill(
    name = "scan_barcodes_cc_image",
    manifest = ":scan_barcodes_cc_manifest",
    deps = [
        ":scan_barcodes_cc",
        ":scan_barcodes_cc_proto",
    ],
)
