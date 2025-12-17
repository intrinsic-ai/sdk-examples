load("@ai_intrinsic_sdks//bazel:skills.bzl", "py_skill", "skill_manifest")
load("@com_github_grpc_grpc//bazel:python_rules.bzl", "py_proto_library")
load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")
load("@rules_python//python:defs.bzl", "py_library")

proto_library(
    name = "counter_demo_proto",
    srcs = ["counter_demo.proto"],
)

py_proto_library(
    name = "counter_demo_py_pb2",
    deps = [":counter_demo_proto"],
)

skill_manifest(
    name = "counter_demo_py_manifest",
    src = "counter_demo.manifest.textproto",
    deps = [":counter_demo_proto"],
)

py_library(
    name = "counter_demo",
    srcs = ["counter_demo.py"],
    deps = [
        ":counter_demo_py_pb2",
        "//services/counter:counter_service_py_pb2",
        "//services/counter:counter_service_py_pb2_grpc",
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

py_skill(
    name = "counter_demo_skill",
    manifest = ":counter_demo_py_manifest",
    deps = [
        ":counter_demo",
        ":counter_demo_py_pb2",
    ],
)
