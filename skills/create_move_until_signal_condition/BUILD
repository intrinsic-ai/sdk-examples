load("@ai_intrinsic_sdks//bazel:skills.bzl", "py_skill", "skill_manifest")
load("@com_github_grpc_grpc//bazel:python_rules.bzl", "py_proto_library")
load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")
load("@rules_python//python:defs.bzl", "py_library", "py_test")

proto_library(
    name = "create_move_until_signal_condition_proto",
    srcs = ["create_move_until_signal_condition.proto"],
    deps = [
        "@ai_intrinsic_sdks//intrinsic/icon/proto/v1:condition_types_proto",
    ],
)

py_proto_library(
    name = "create_move_until_signal_condition_py_pb2",
    deps = [":create_move_until_signal_condition_proto"],
)

skill_manifest(
    name = "create_move_until_signal_condition_py_manifest",
    src = "create_move_until_signal_condition_manifest.textproto",
    deps = [":create_move_until_signal_condition_proto"],
)

py_library(
    name = "create_move_until_signal_condition_py",
    srcs = ["create_move_until_signal_condition.py"],
    deps = [
        ":create_move_until_signal_condition_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/icon/proto/v1:condition_types_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/icon/python:icon",
        "@ai_intrinsic_sdks//intrinsic/skills/python:proto_utils",
        "@ai_intrinsic_sdks//intrinsic/skills/python:skill_interface",
        "@ai_intrinsic_sdks//intrinsic/util:decorators",
        "@com_google_absl_py//absl/logging",
        "@com_google_protobuf//:protobuf_python",
    ],
)

py_skill(
    name = "create_move_until_signal_condition_py_image",
    manifest = ":create_move_until_signal_condition_py_manifest",
    deps = [
        ":create_move_until_signal_condition_py",
        ":create_move_until_signal_condition_py_pb2",
    ],
)

py_test(
    name = "create_move_until_signal_condition_py_test",
    size = "small",
    srcs = ["create_move_until_signal_condition_test.py"],
    data = [
    ],
    main = "create_move_until_signal_condition_test.py",
    deps = [
        ":create_move_until_signal_condition_py",
        ":create_move_until_signal_condition_py_pb2",
    ],
)
