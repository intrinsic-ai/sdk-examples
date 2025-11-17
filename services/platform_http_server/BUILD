load("@ai_intrinsic_sdks//bazel:python_oci_image.bzl", "python_oci_image")
load("@ai_intrinsic_sdks//intrinsic/assets/services/build_defs:services.bzl", "intrinsic_service")
load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")
load("@com_google_protobuf//bazel:py_proto_library.bzl", "py_proto_library")
load("@container_structure_test//:defs.bzl", "container_structure_test")
load("@platform_http_server_pip_deps//:requirements.bzl", "requirement")
load("@rules_pkg//:pkg.bzl", "pkg_tar")
load("@rules_python//python:defs.bzl", "py_binary")

proto_library(
    name = "platform_http_server_proto",
    srcs = ["platform_http_server.proto"],
)

py_proto_library(
    name = "platform_http_server_py_pb2",
    visibility = ["//visibility:public"],
    deps = [":platform_http_server_proto"],
)

py_binary(
    name = "server",
    srcs = [
        "data_asset_utils.py",
        "server.py",
    ],
    main = "server.py",
    deps = [
        ":platform_http_server_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/assets/data/proto/v1:data_asset_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/assets/data/proto/v1:data_assets_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/assets/data/proto/v1:data_assets_py_pb2_grpc",
        "@ai_intrinsic_sdks//intrinsic/assets/data/proto/v1:referenced_data_struct_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/assets/services/proto/v1:service_state_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/assets/services/proto/v1:service_state_py_pb2_grpc",
        "@ai_intrinsic_sdks//intrinsic/executive/proto:executive_service_py_pb2_grpc",
        "@ai_intrinsic_sdks//intrinsic/resources/proto:runtime_context_py_pb2",
        requirement("flask"),
        requirement("waitress"),
        requirement("grpcio"),
    ],
)

exports_files(["requirements.txt"])

pkg_tar(
    name = "server_layer",
    srcs = [":server"],
    extension = "tar.gz",
    include_runfiles = True,
    strip_prefix = "/",
)

python_oci_image(
    name = "platform_http_server_image",
    base = "@distroless_python3",
    binary = "server",
    entrypoint = [
        "python3",
        "-u",
        "/services/platform_http_server/server",
    ],
    extra_tars = [
        ":server_layer",
    ],
)

container_structure_test(
    name = "platform_http_server_image_test",
    configs = ["testdata/image_files.yaml"],
    driver = "tar",
    image = ":platform_http_server_image.tar",
)

intrinsic_service(
    name = "platform_http_server",
    default_config = "config/default_config_values.textproto",
    images = [
        ":platform_http_server_image.tar",
    ],
    manifest = ":platform_http_server_manifest.textproto",
    deps = [
        ":platform_http_server_proto",
    ],
)
