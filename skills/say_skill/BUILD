load("@ai_intrinsic_sdks//bazel:skills.bzl", "cc_skill", "py_skill", "skill_manifest")
load("@com_github_grpc_grpc//bazel:python_rules.bzl", "py_proto_library")
load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")

proto_library(
    name = "say_skill_proto",
    srcs = ["say_skill.proto"],
)

py_proto_library(
    name = "say_skill_py_pb2",
    deps = [":say_skill_proto"],
)

py_library(
    name = "say_skill_py",
    srcs = ["say_skill.py"],
    deps = [
        ":say_skill_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/skills/python:proto_utils",
        "@ai_intrinsic_sdks//intrinsic/skills/python:skill_interface",
        "@ai_intrinsic_sdks//intrinsic/util:decorators",
        "@com_google_absl_py//absl/logging",
        "@com_google_protobuf//:protobuf_python",
    ],
)

skill_manifest(
    name = "say_skill_py_manifest",
    src = "say_skill_py.manifest.textproto",
    deps = [":say_skill_proto"],
)

py_skill(
    name = "say_skill_py_image",
    manifest = ":say_skill_py_manifest",
    deps = [
        ":say_skill_py",
        ":say_skill_py_pb2",
    ],
)

py_test(
    name = "say_skill_py_test",
    size = "small",
    srcs = ["say_skill_test.py"],
    main = "say_skill_test.py",
    deps = [
        ":say_skill_py",
    ],
)

cc_proto_library(
    name = "say_skill_cc_proto",
    deps = [":say_skill_proto"],
)

skill_manifest(
    name = "say_skill_cc_manifest",
    src = "say_skill_cc.manifest.textproto",
    deps = [":say_skill_proto"],
)

cc_library(
    name = "say_skill_cc",
    srcs = ["say_skill.cc"],
    hdrs = ["say_skill.h"],
    deps = [
        ":say_skill_cc_proto",
        "@ai_intrinsic_sdks//intrinsic/skills/cc:skill_interface",
        "@ai_intrinsic_sdks//intrinsic/skills/cc:skill_utils",
        "@ai_intrinsic_sdks//intrinsic/util/status:status_macros",
        "@com_google_absl//absl/log",
        "@com_google_absl//absl/status",
        "@com_google_absl//absl/status:statusor",
        "@com_google_absl//absl/synchronization",
        "@com_google_protobuf//:protobuf",
    ],
)

cc_skill(
    name = "say_skill_cc_image",
    manifest = ":say_skill_cc_manifest",
    deps = [
        ":say_skill_cc",
        ":say_skill_cc_proto",
    ],
)

cc_test(
    name = "say_skill_cc_test",
    srcs = ["say_skill_test.cc"],
    deps = [
        ":say_skill_cc",
        "@ai_intrinsic_sdks//intrinsic/skills/testing:skill_test_utils_cc",
        "@com_google_googletest//:gtest_main",
    ],
)
