load("@ai_intrinsic_sdks//bazel:python_oci_image.bzl", "python_oci_image")
load("@ai_intrinsic_sdks//intrinsic/assets/services/build_defs:services.bzl", "intrinsic_service")
load("@com_github_grpc_grpc//bazel:cc_grpc_library.bzl", "cc_grpc_library")
load("@com_github_grpc_grpc//bazel:python_rules.bzl", "py_grpc_library", "py_proto_library")
load("@com_google_protobuf//bazel:cc_proto_library.bzl", "cc_proto_library")
load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")
load("@point_storage_pip_deps//:requirements.bzl", "requirement")
load("@rules_python//python:defs.bzl", "py_binary")

proto_library(
    name = "point_storage_service_proto",
    srcs = ["point_storage_service.proto"],
    visibility = [
        "//skills/points_crud:__subpackages__",
        "//tests:__subpackages__",
    ],
)

py_proto_library(
    name = "point_storage_service_py_pb2",
    visibility = ["//visibility:public"],
    deps = [":point_storage_service_proto"],
)

py_grpc_library(
    name = "point_storage_service_py_pb2_grpc",
    srcs = [":point_storage_service_proto"],
    grpc_library = requirement("grpcio"),
    visibility = ["//visibility:public"],
    deps = [":point_storage_service_py_pb2"],
)

cc_proto_library(
    name = "point_storage_service_cc_proto",
    visibility = ["//visibility:public"],
    deps = [":point_storage_service_proto"],
)

cc_grpc_library(
    name = "point_storage_service_cc_grpc_proto",
    srcs = [":point_storage_service_proto"],
    grpc_only = True,
    visibility = ["//visibility:public"],
    deps = [":point_storage_service_cc_proto"],
)

py_binary(
    name = "point_storage_service_bin",
    srcs = ["point_storage_service.py"],
    main = "point_storage_service.py",
    deps = [
        ":point_storage_service_py_pb2_grpc",
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
    name = "point_storage_service_image",
    base = "@distroless_python3",
    binary = "point_storage_service_bin",
    entrypoint = [
        "python3",
        "-u",
        "/services/point_storage/point_storage_service_bin",
    ],
)

intrinsic_service(
    name = "point_storage_service",
    images = [
        ":point_storage_service_image.tar",
    ],
    manifest = ":point_storage_service_manifest.textproto",
    deps = [
        ":point_storage_service_proto",
    ],
)
