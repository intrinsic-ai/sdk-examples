load("@ai_intrinsic_sdks//bazel:skills.bzl", "cc_skill", "py_skill", "skill_manifest")
load("@com_github_grpc_grpc//bazel:python_rules.bzl", "py_proto_library")
load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")

proto_library(
    name = "use_world_proto",
    srcs = ["use_world.proto"],
    deps = ["@ai_intrinsic_sdks//intrinsic/world/proto:object_world_refs_proto"],
)

py_proto_library(
    name = "use_world_py_pb2",
    deps = [":use_world_proto"],
)

py_library(
    name = "use_world_py",
    srcs = ["use_world.py"],
    deps = [
        ":use_world_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/icon/equipment:equipment_utils_py",
        "@ai_intrinsic_sdks//intrinsic/math/python:data_types",
        "@ai_intrinsic_sdks//intrinsic/skills/python:proto_utils",
        "@ai_intrinsic_sdks//intrinsic/skills/python:skill_interface",
        "@ai_intrinsic_sdks//intrinsic/util:decorators",
        "@ai_intrinsic_sdks//intrinsic/world/python:object_world_client",
        "@ai_intrinsic_sdks//intrinsic/world/python:object_world_resources",
        "@com_google_protobuf//:protobuf_python",
    ],
)

skill_manifest(
    name = "use_world_py_manifest",
    src = "use_world_py.manifest.textproto",
    deps = [":use_world_proto"],
)

py_skill(
    name = "use_world_py_image",
    manifest = ":use_world_py_manifest",
    deps = [
        ":use_world_py",
        ":use_world_py_pb2",
    ],
)

py_test(
    name = "use_world_py_test",
    size = "small",
    srcs = ["use_world_test.py"],
    main = "use_world_test.py",
    deps = [
        ":use_world_py",
    ],
)

cc_proto_library(
    name = "use_world_cc_proto",
    deps = [":use_world_proto"],
)

skill_manifest(
    name = "use_world_cc_manifest",
    src = "use_world_cc.manifest.textproto",
    deps = [":use_world_proto"],
)

cc_library(
    name = "use_world_cc",
    srcs = ["use_world.cc"],
    hdrs = ["use_world.h"],
    deps = [
        ":use_world_cc_proto",
        "@ai_intrinsic_sdks//intrinsic/math:pose3",
        "@ai_intrinsic_sdks//intrinsic/skills/cc:equipment_pack",
        "@ai_intrinsic_sdks//intrinsic/skills/cc:skill_interface",
        "@ai_intrinsic_sdks//intrinsic/skills/cc:skill_utils",
        "@ai_intrinsic_sdks//intrinsic/world/objects:object_world_client",
        "@com_google_absl//absl/log",
        "@com_google_absl//absl/status",
        "@com_google_absl//absl/status:statusor",
        "@com_google_protobuf//:protobuf",
    ],
    alwayslink = True,
)

cc_skill(
    name = "use_world_cc_image",
    manifest = ":use_world_cc_manifest",
    deps = [
        ":use_world_cc",
        ":use_world_cc_proto",
    ],
)

# Manually run integration test:
#   bazel run //skills/use_world:use_world_integration_test -- --python
# OR
#   bazel run //skills/use_world:use_world_integration_test -- --cpp
py_binary(
    name = "use_world_integration_test",
    srcs = ["use_world_integration_test.py"],
    main = "use_world_integration_test.py",
    deps = [
        "@ai_intrinsic_sdks//intrinsic/solutions:behavior_tree",
        "@ai_intrinsic_sdks//intrinsic/solutions:deployments",
    ],
)
