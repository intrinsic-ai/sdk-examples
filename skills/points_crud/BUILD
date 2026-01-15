load("@ai_intrinsic_sdks//bazel:skills.bzl", "py_skill", "skill_manifest")
load("@com_github_grpc_grpc//bazel:python_rules.bzl", "py_proto_library")
load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")
load("@rules_python//python:defs.bzl", "py_library", "py_test")

proto_library(
    name = "points_crud_proto",
    srcs = ["points_crud.proto"],
    deps = [
        "//services/point_storage:point_storage_service_proto",
    ],
)

py_proto_library(
    name = "points_crud_py_pb2",
    visibility = [
        "//tests:__subpackages__",
    ],
    deps = [":points_crud_proto"],
)

skill_manifest(
    name = "points_crud_py_manifest",
    src = "points_crud.manifest.textproto",
    deps = [":points_crud_proto"],
)

py_library(
    name = "points_crud",
    srcs = ["points_crud.py"],
    deps = [
        ":points_crud_py_pb2",
        "//services/point_storage:point_storage_service_py_pb2",
        "//services/point_storage:point_storage_service_py_pb2_grpc",
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
    name = "points_crud_skill",
    manifest = ":points_crud_py_manifest",
    deps = [
        ":points_crud",
        ":points_crud_py_pb2",
    ],
)

py_test(
    name = "points_crud_test",
    size = "small",
    srcs = ["points_crud_test.py"],
    main = "points_crud_test.py",
    deps = [
        ":points_crud",
        "@ai_intrinsic_sdks//intrinsic/skills/testing:skill_test_utils",
        "@ai_intrinsic_sdks//intrinsic/solutions/testing:compare",
    ],
)
