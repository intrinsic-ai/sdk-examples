load("@ai_intrinsic_sdks//bazel:skills.bzl", "cc_skill", "py_skill", "skill_manifest")
load("@com_github_grpc_grpc//bazel:python_rules.bzl", "py_proto_library")
load("@com_google_protobuf//bazel:cc_proto_library.bzl", "cc_proto_library")
load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")
load("@rules_cc//cc:cc_library.bzl", "cc_library")
load("@rules_python//python:defs.bzl", "py_library", "py_test")

proto_library(
    name = "validate_pose_proto",
    srcs = ["validate_pose.proto"],
    deps = ["@ai_intrinsic_sdks//intrinsic/world/proto:object_world_refs_proto"],
)

py_proto_library(
    name = "validate_pose_py_pb2",
    deps = [":validate_pose_proto"],
)

py_library(
    name = "validate_pose_py",
    srcs = ["validate_pose.py"],
    deps = [
        ":validate_pose_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/skills/python:proto_utils",
        "@ai_intrinsic_sdks//intrinsic/skills/python:skill_interface",
        "@ai_intrinsic_sdks//intrinsic/util:decorators",
        "@ai_intrinsic_sdks//intrinsic/world/python:object_world_client",
        "@com_google_absl_py//absl/logging",
        "@com_google_protobuf//:protobuf_python",
    ],
)

skill_manifest(
    name = "validate_pose_py_manifest",
    src = "validate_pose_py.manifest.textproto",
    deps = [":validate_pose_proto"],
)

py_skill(
    name = "validate_pose_py_image",
    manifest = ":validate_pose_py_manifest",
    deps = [
        ":validate_pose_py",
        ":validate_pose_py_pb2",
    ],
)

py_test(
    name = "validate_pose_py_test",
    size = "small",
    srcs = ["validate_pose_test.py"],
    main = "validate_pose_test.py",
    deps = [
        ":validate_pose_py",
        "@ai_intrinsic_sdks//intrinsic/math/python:pose3",
    ],
)

cc_proto_library(
    name = "validate_pose_cc_proto",
    deps = [":validate_pose_proto"],
)

skill_manifest(
    name = "validate_pose_cc_manifest",
    src = "validate_pose_cc.manifest.textproto",
    deps = [":validate_pose_proto"],
)

cc_library(
    name = "validate_pose_cc",
    srcs = ["validate_pose.cc"],
    hdrs = ["validate_pose.h"],
    deps = [
        ":validate_pose_cc_proto",
        "@ai_intrinsic_sdks//intrinsic/skills/cc:skill_interface",
        "@ai_intrinsic_sdks//intrinsic/skills/cc:skill_utils",
        "@ai_intrinsic_sdks//intrinsic/util/status:status_macros",
        "@ai_intrinsic_sdks//intrinsic/world/objects:object_world_client",
        "@com_google_absl//absl/log",
        "@com_google_absl//absl/status",
        "@com_google_absl//absl/status:statusor",
        "@com_google_protobuf//:protobuf",
    ],
    alwayslink = True,
)

cc_skill(
    name = "validate_pose_cc_image",
    manifest = ":validate_pose_cc_manifest",
    deps = [
        ":validate_pose_cc",
        ":validate_pose_cc_proto",
    ],
)
