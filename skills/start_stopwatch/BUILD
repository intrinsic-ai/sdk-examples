load("@ai_intrinsic_sdks//bazel:skills.bzl", "py_skill", "skill_manifest")
load("@com_github_grpc_grpc//bazel:python_rules.bzl", "py_proto_library")
load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")
load("@rules_python//python:defs.bzl", "py_library", "py_test")

proto_library(
    name = "start_stopwatch_proto",
    srcs = ["start_stopwatch.proto"],
)

py_proto_library(
    name = "start_stopwatch_py_pb2",
    deps = [":start_stopwatch_proto"],
)

skill_manifest(
    name = "start_stopwatch_py_manifest",
    src = "start_stopwatch.manifest.textproto",
    deps = [":start_stopwatch_proto"],
)

py_library(
    name = "start_stopwatch",
    srcs = ["start_stopwatch.py"],
    deps = [
        ":start_stopwatch_py_pb2",
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
    name = "start_stopwatch_test",
    size = "small",
    srcs = ["start_stopwatch_test.py"],
    main = "start_stopwatch_test.py",
    deps = [
        ":start_stopwatch",
        "@ai_intrinsic_sdks//intrinsic/skills/testing:skill_test_utils",
    ],
)

py_skill(
    name = "start_stopwatch_skill",
    manifest = ":start_stopwatch_py_manifest",
    deps = [
        ":start_stopwatch",
        ":start_stopwatch_py_pb2",
    ],
)
