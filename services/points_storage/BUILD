load("@ai_intrinsic_sdks//bazel:python_oci_image.bzl", "python_oci_image")
load("@ai_intrinsic_sdks//intrinsic/assets/services/build_defs:services.bzl", "intrinsic_service")
load("@com_github_grpc_grpc//bazel:cc_grpc_library.bzl", "cc_grpc_library")
load("@com_github_grpc_grpc//bazel:python_rules.bzl", "py_grpc_library", "py_proto_library")
load("@com_google_protobuf//bazel:cc_proto_library.bzl", "cc_proto_library")
load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")
load("@rules_python//python:defs.bzl", "py_binary")
load("@points_storage_pip_deps//:requirements.bzl", "requirement")

proto_library(
    name = "points_storage_service_proto",
    srcs = ["points_storage_service.proto"],
)

py_proto_library(
    name = "points_storage_service_py_pb2",
    visibility = ["//visibility:public"],
    deps = [":points_storage_service_proto"],
)

py_grpc_library(
    name = "points_storage_service_py_pb2_grpc",
    srcs = [":points_storage_service_proto"],
    grpc_library = requirement("grpcio"),
    visibility = ["//visibility:public"],
    deps = [":points_storage_service_py_pb2"],
)

cc_proto_library(
    name = "points_storage_service_cc_proto",
    visibility = ["//visibility:public"],
    deps = [":points_storage_service_proto"],
)

cc_grpc_library(
    name = "points_storage_service_cc_grpc_proto",
    srcs = [":points_storage_service_proto"],
    grpc_only = True,
    visibility = ["//visibility:public"],
    deps = [":points_storage_service_cc_proto"],
)

py_binary(
    name = "points_storage_service_bin",
    srcs = ["points_storage_service.py"],
    main = "points_storage_service.py",
    deps = [
        ":points_storage_service_py_pb2_grpc",
        "@ai_intrinsic_sdks//intrinsic/resources/proto:runtime_context_py_pb2",
        requirement("grpcio"),
        "@ai_intrinsic_sdks//intrinsic/platform/pubsub/python:pubsub",
        "@com_google_absl_py//absl:app",
        "@com_google_absl_py//absl/logging",
        "@com_google_protobuf//:protobuf_python",
        "@pybind11_abseil//pybind11_abseil:import_status_module",
    ],
)

python_oci_image(
    name = "points_storage_service_image",
    base = "@distroless_python3",
    binary = "points_storage_service_bin",
    entrypoint = [
        "python3",
        "-u",
        "/services/points_storage/points_storage_service_bin",
    ],
)

intrinsic_service(
    name = "points_storage_service",
    images = [
        ":points_storage_service_image.tar",
    ],
    manifest = ":points_storage_service_manifest.textproto",
    deps = [
        ":points_storage_service_proto",
    ],
)
