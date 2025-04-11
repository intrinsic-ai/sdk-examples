load("@ai_intrinsic_sdks//intrinsic/assets/services/build_defs:services.bzl", "intrinsic_service")
load("@com_github_grpc_grpc//bazel:python_rules.bzl", "py_grpc_library", "py_proto_library")
load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")
load("@ai_intrinsic_sdks//bazel:python_oci_image.bzl", "python_oci_image")
load("@random_number_pip_deps//:requirements.bzl", "requirement")

proto_library(
    name = "random_number_proto",
    srcs = ["random_number.proto"],
)

py_proto_library(
    name = "random_number_py_pb2",
    visibility = ["//visibility:public"],
    deps = [":random_number_proto"],
)

py_grpc_library(
    name = "random_number_py_pb2_grpc",
    srcs = [":random_number_proto"],
    grpc_library = requirement("grpcio"),
    visibility = ["//visibility:public"],
    deps = [":random_number_py_pb2"],
)

py_library(
    name = "random_number",
    srcs = ["random_number.py"],
    deps = [
        ":random_number_py_pb2_grpc",
        "@ai_intrinsic_sdks//intrinsic/assets/services/proto/v1:service_state_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/assets/services/proto/v1:service_state_py_pb2_grpc",
        "@ai_intrinsic_sdks//intrinsic/util/grpc:error_handling",
        "@ai_intrinsic_sdks//intrinsic/util/status:extended_status_py_pb2",
        "@com_google_protobuf//:protobuf_python",
        requirement("grpcio"),
    ],
)

py_binary(
    name = "random_number_service_bin",
    srcs = ["random_number_main.py"],
    main = "random_number_main.py",
    deps = [
        ":random_number",
        ":random_number_py_pb2_grpc",
        "@ai_intrinsic_sdks//intrinsic/assets/services/proto/v1:service_state_py_pb2_grpc",
        "@ai_intrinsic_sdks//intrinsic/resources/proto:runtime_context_py_pb2",
        requirement("grpcio"),
    ],
)

python_oci_image(
    name = "random_number_service_image",
    binary = ":random_number_service_bin",
)

intrinsic_service(
    name = "random_number_service",
    images = [
        ":random_number_service_image.tar",
    ],
    manifest = "random_number_manifest.textproto",
    deps = [
        ":random_number_proto",
    ],
)

py_test(
    name = "random_number_test",
    srcs = ["random_number_test.py"],
    deps = [
        ":random_number",
        ":random_number_py_pb2",
        ":random_number_py_pb2_grpc",
        requirement("grpcio"),
        requirement("portpicker"),
    ],
    main = "random_number_test.py",
    size = "small",
)
