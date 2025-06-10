load("@ai_intrinsic_sdks//bazel:python_oci_image.bzl", "python_oci_image")
load("@ai_intrinsic_sdks//intrinsic/assets/services/build_defs:services.bzl", "intrinsic_service")
load("@com_github_grpc_grpc//bazel:cc_grpc_library.bzl", "cc_grpc_library")
load("@com_github_grpc_grpc//bazel:python_rules.bzl", "py_grpc_library", "py_proto_library")
load("@com_google_protobuf//bazel:cc_proto_library.bzl", "cc_proto_library")
load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")
load("@stopwatch_pip_deps//:requirements.bzl", "requirement")

proto_library(
    name = "stopwatch_service_proto",
    srcs = ["stopwatch_service.proto"],
)

py_proto_library(
    name = "stopwatch_service_py_pb2",
    visibility = ["//visibility:public"],
    deps = [":stopwatch_service_proto"],
)

py_grpc_library(
    name = "stopwatch_service_py_pb2_grpc",
    srcs = [":stopwatch_service_proto"],
    grpc_library = requirement("grpcio"),
    visibility = ["//visibility:public"],
    deps = [":stopwatch_service_py_pb2"],
)

cc_proto_library(
    name = "stopwatch_service_cc_proto",
    visibility = ["//visibility:public"],
    deps = [":stopwatch_service_proto"],
)

cc_grpc_library(
    name = "stopwatch_service_cc_grpc_proto",
    srcs = [":stopwatch_service_proto"],
    grpc_only = True,
    visibility = ["//visibility:public"],
    deps = [":stopwatch_service_cc_proto"],
)

py_binary(
    name = "stopwatch_service_bin",
    srcs = ["stopwatch_service.py"],
    main = "stopwatch_service.py",
    deps = [
        ":stopwatch_service_py_pb2_grpc",
        "@ai_intrinsic_sdks//intrinsic/resources/proto:runtime_context_py_pb2",
        requirement("grpcio"),
    ],
)

python_oci_image(
    name = "stopwatch_service_image",
    base = "@distroless_python3",
    binary = "stopwatch_service_bin",
    entrypoint = [
        "python3",
        "-u",
        "/services/stopwatch/stopwatch_service_bin",
    ],
)

intrinsic_service(
    name = "stopwatch_service",
    images = [
        ":stopwatch_service_image.tar",
    ],
    manifest = ":stopwatch_service_manifest.textproto",
    deps = [
        ":stopwatch_service_proto",
    ],
)

py_binary(
    name = "stopwatch_integration_test",
    srcs = ["stopwatch_integration_test.py"],
    main = "stopwatch_integration_test.py",
    deps = [
        "@ai_intrinsic_sdks//intrinsic/solutions:behavior_tree",
        "@ai_intrinsic_sdks//intrinsic/solutions:deployments",
    ],
)
