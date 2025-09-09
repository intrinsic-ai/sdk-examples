load("@ai_intrinsic_sdks//bazel:skills.bzl", "py_skill", "skill_manifest")
load("@com_github_grpc_grpc//bazel:python_rules.bzl", "py_proto_library")
load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")
load("@rules_python//python:defs.bzl", "py_library", "py_test")

proto_library(
    name = "get_random_number_proto",
    srcs = ["get_random_number.proto"],
)

py_proto_library(
    name = "get_random_number_py_pb2",
    deps = [":get_random_number_proto"],
)

skill_manifest(
    name = "get_random_number_manifest",
    src = "get_random_number_manifest.textproto",
    deps = [":get_random_number_proto"],
)

py_library(
    name = "get_random_number",
    srcs = ["get_random_number.py"],
    deps = [
        ":get_random_number_py_pb2",
        "//services/random_number:random_number_py_pb2",
        "//services/random_number:random_number_py_pb2_grpc",
        "@ai_intrinsic_sdks//intrinsic/skills/python:skill_interface",
        "@ai_intrinsic_sdks//intrinsic/util:decorators",
        "@ai_intrinsic_sdks//intrinsic/util/grpc:connection",
        "@ai_intrinsic_sdks//intrinsic/util/grpc:interceptor",
        "@com_google_absl_py//absl/logging",
        "@com_google_protobuf//:protobuf_python",
    ],
)

py_skill(
    name = "get_random_number_skill",
    manifest = ":get_random_number_manifest",
    deps = [
        "get_random_number_py_pb2",
        ":get_random_number",
    ],
)

py_test(
    name = "get_random_number_test",
    size = "small",
    srcs = ["get_random_number_test.py"],
    main = "get_random_number_test.py",
    deps = [
        ":get_random_number",
        "@ai_intrinsic_sdks//intrinsic/skills/testing:skill_test_utils",
    ],
)
