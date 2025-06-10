load("@ai_intrinsic_sdks//bazel:python_oci_image.bzl", "python_oci_image")
load("@ai_intrinsic_sdks//intrinsic/assets/services/build_defs:services.bzl", "intrinsic_service")
load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")
load("@com_google_protobuf//bazel:py_proto_library.bzl", "py_proto_library")
load("@rules_python//python:defs.bzl", "py_binary")

proto_library(
    name = "configurable_service_proto",
    srcs = ["configurable_service.proto"],
)

py_proto_library(
    name = "configurable_service_py_pb2",
    visibility = ["//visibility:public"],
    deps = [":configurable_service_proto"],
)

py_binary(
    name = "configurable_service_bin",
    srcs = ["configurable_service.py"],
    main = "configurable_service.py",
    deps = [
        ":configurable_service_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/resources/proto:runtime_context_py_pb2",
    ],
)

python_oci_image(
    name = "configurable_service_image",
    base = "@distroless_python3",
    binary = "configurable_service_bin",
    entrypoint = [
        "python3",
        "-u",
        "/services/configurable_service/configurable_service_bin",
    ],
)

intrinsic_service(
    name = "configurable_service",
    default_config = "default_config_values.textproto",
    images = [
        ":configurable_service_image.tar",
    ],
    manifest = ":configurable_service_manifest.textproto",
    deps = [
        ":configurable_service_proto",
    ],
)
