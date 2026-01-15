load("@rules_python//python:defs.bzl", "py_binary", "py_library")

py_library(
    name = "recording_lib",
    srcs = ["recording_lib.py"],
    visibility = ["//visibility:public"],
    deps = [
        "@ai_intrinsic_sdks//intrinsic/logging/proto:bag_packager_service_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/logging/proto:bag_packager_service_py_pb2_grpc",
        "@ai_intrinsic_sdks//intrinsic/solutions:auth",
        "@com_google_absl_py//absl/logging",
    ],
)

py_binary(
    name = "create_recording_py",
    srcs = ["create_recording.py"],
    main = "create_recording.py",
    deps = [
        "@ai_intrinsic_sdks//intrinsic/logging/proto:bag_metadata_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/logging/proto:logger_service_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/logging/proto:logger_service_py_pb2_grpc",
        "@ai_intrinsic_sdks//intrinsic/solutions:deployments",
        "@com_google_absl_py//absl:app",
        "@com_google_protobuf//:protobuf_python",
    ],
)

py_binary(
    name = "generate_and_download_recording_py",
    srcs = ["generate_and_download_recording.py"],
    main = "generate_and_download_recording.py",
    deps = [
        ":recording_lib",
        "@ai_intrinsic_sdks//intrinsic/logging/proto:bag_packager_service_py_pb2_grpc",
        "@ai_intrinsic_sdks//intrinsic/solutions:auth",
        "@ai_intrinsic_sdks//intrinsic/solutions:dialerutil",
        "@com_google_absl_py//absl:app",
        "@com_google_absl_py//absl/flags",
    ],
)

py_binary(
    name = "generate_and_visualize_recording_py",
    srcs = ["generate_and_visualize_recording.py"],
    main = "generate_and_visualize_recording.py",
    deps = [
        ":recording_lib",
        "@ai_intrinsic_sdks//intrinsic/kubernetes/vmpool/manager/api/v1:lease_api_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/kubernetes/vmpool/manager/api/v1:lease_api_py_pb2_grpc",
        "@ai_intrinsic_sdks//intrinsic/logging/proto:bag_packager_service_py_pb2_grpc",
        "@ai_intrinsic_sdks//intrinsic/logging/proto:replay_service_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/logging/proto:replay_service_py_pb2_grpc",
        "@ai_intrinsic_sdks//intrinsic/solutions:auth",
        "@ai_intrinsic_sdks//intrinsic/solutions:deployments",
        "@ai_intrinsic_sdks//intrinsic/solutions:dialerutil",
        "@com_google_absl_py//absl:app",
        "@com_google_absl_py//absl/flags",
        "@com_google_absl_py//absl/logging",
        "@com_google_protobuf//:protobuf_python",
    ],
)
