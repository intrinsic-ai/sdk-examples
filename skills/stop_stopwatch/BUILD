load("@ai_intrinsic_sdks//bazel:skills.bzl", "cc_skill", "py_skill", "skill_manifest")
load("@com_github_grpc_grpc//bazel:python_rules.bzl", "py_proto_library")
load("@com_google_protobuf//bazel:cc_proto_library.bzl", "cc_proto_library")
load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")
load("@rules_cc//cc:cc_library.bzl", "cc_library")
load("@rules_cc//cc:cc_test.bzl", "cc_test")
load("@rules_python//python:defs.bzl", "py_library", "py_test")

proto_library(
    name = "stop_stopwatch_proto",
    srcs = ["stop_stopwatch.proto"],
)

#########
# Python
#########

py_proto_library(
    name = "stop_stopwatch_py_pb2",
    deps = [":stop_stopwatch_proto"],
)

skill_manifest(
    name = "stop_stopwatch_py_manifest",
    src = "stop_stopwatch_py.manifest.textproto",
    deps = [":stop_stopwatch_proto"],
)

py_library(
    name = "stop_stopwatch_py",
    srcs = ["stop_stopwatch.py"],
    deps = [
        ":stop_stopwatch_py_pb2",
        "//services/stopwatch:stopwatch_service_py_pb2",
        "//services/stopwatch:stopwatch_service_py_pb2_grpc",
        "@ai_intrinsic_sdks//intrinsic/skills/proto:equipment_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/skills/python:proto_utils",
        "@ai_intrinsic_sdks//intrinsic/skills/python:skill_interface",
        "@ai_intrinsic_sdks//intrinsic/util:decorators",
        "@ai_intrinsic_sdks//intrinsic/util/grpc:connection",
        "@ai_intrinsic_sdks//intrinsic/util/grpc:interceptor",
        "@com_google_absl_py//absl/logging",
        "@com_google_protobuf//:protobuf_python",
    ],
)

py_test(
    name = "stop_stopwatch_py_test",
    size = "small",
    srcs = ["stop_stopwatch_test.py"],
    main = "stop_stopwatch_test.py",
    deps = [
        ":stop_stopwatch_py",
        "@ai_intrinsic_sdks//intrinsic/skills/testing:skill_test_utils",
    ],
)

py_skill(
    name = "stop_stopwatch_py_skill",
    manifest = ":stop_stopwatch_py_manifest",
    deps = [
        ":stop_stopwatch_py",
        ":stop_stopwatch_py_pb2",
    ],
)

#########
# C++
#########

cc_proto_library(
    name = "stop_stopwatch_cc_proto",
    deps = [":stop_stopwatch_proto"],
)

skill_manifest(
    name = "stop_stopwatch_cc_manifest",
    src = "stop_stopwatch_cc.manifest.textproto",
    deps = [":stop_stopwatch_proto"],
)

cc_library(
    name = "stop_stopwatch_cc",
    srcs = ["stop_stopwatch.cc"],
    hdrs = ["stop_stopwatch.h"],
    deps = [
        ":stop_stopwatch_cc_proto",
        "//services/stopwatch:stopwatch_service_cc_grpc_proto",
        "//services/stopwatch:stopwatch_service_cc_proto",
        "@ai_intrinsic_sdks//intrinsic/skills/cc:skill_interface",
        "@ai_intrinsic_sdks//intrinsic/skills/cc:skill_utils",
        "@ai_intrinsic_sdks//intrinsic/skills/proto:equipment_cc_proto",
        "@ai_intrinsic_sdks//intrinsic/util/status:status_macros",
        "@ai_intrinsic_sdks//intrinsic/util/status:status_macros_grpc",
        "@com_github_grpc_grpc//:grpc++",
        "@com_google_absl//absl/container:flat_hash_map",
        "@com_google_absl//absl/log",
        "@com_google_absl//absl/status",
        "@com_google_absl//absl/status:statusor",
        "@com_google_protobuf//:protobuf",
    ],
)

cc_test(
    name = "stop_stopwatch_cc_test",
    size = "small",
    srcs = ["stop_stopwatch_test.cc"],
    deps = [
        ":stop_stopwatch_cc",
        "@ai_intrinsic_sdks//intrinsic/skills/testing:skill_test_utils_cc",
        "@com_google_absl//absl/status:status_matchers",
        "@com_google_googletest//:gtest_main",
    ],
)

cc_skill(
    name = "stop_stopwatch_cc_skill",
    manifest = ":stop_stopwatch_cc_manifest",
    deps = [
        ":stop_stopwatch_cc",
        ":stop_stopwatch_cc_proto",
    ],
)
