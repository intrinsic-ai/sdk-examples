load("@ai_intrinsic_sdks//bazel:skills.bzl", "py_skill", "skill_manifest")
load("@com_github_grpc_grpc//bazel:python_rules.bzl", "py_proto_library")
load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")

proto_library(
    name = "read_joint_positions_from_opcua_equipment_proto",
    srcs = ["read_joint_positions_from_opcua_equipment.proto"],
    deps = ["@ai_intrinsic_sdks//intrinsic/icon/proto:joint_space_proto"],
)

py_proto_library(
    name = "read_joint_positions_from_opcua_equipment_py_pb2",
    deps = [":read_joint_positions_from_opcua_equipment_proto"],
)

skill_manifest(
    name = "read_joint_positions_from_opcua_equipment_py_manifest",
    src = "read_joint_positions_from_opcua_equipment.manifest.textproto",
    deps = [":read_joint_positions_from_opcua_equipment_proto"],
)

py_library(
    name = "read_joint_positions_from_opcua_equipment",
    srcs = ["read_joint_positions_from_opcua_equipment.py"],
    srcs_version = "PY3",
    deps = [
        ":read_joint_positions_from_opcua_equipment_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/hardware/gpio/v1:signal_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/hardware/opcua_equipment:opcua_equipment_service_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/hardware/opcua_equipment:opcua_equipment_service_py_pb2_grpc",
        "@ai_intrinsic_sdks//intrinsic/icon/equipment:equipment_utils_py",
        "@ai_intrinsic_sdks//intrinsic/icon/proto:joint_space_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/icon/python:icon",
        "@ai_intrinsic_sdks//intrinsic/skills/proto:equipment_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/skills/python:proto_utils",
        "@ai_intrinsic_sdks//intrinsic/skills/python:skill_interface",
        "@ai_intrinsic_sdks//intrinsic/util:decorators",
        "@com_google_absl_py//absl/logging",
        "@com_google_protobuf//:protobuf_python",
    ],
)

py_skill(
    name = "read_joint_positions_from_opcua_equipment_image",
    manifest = ":read_joint_positions_from_opcua_equipment_py_manifest",
    deps = [
        ":read_joint_positions_from_opcua_equipment",
        ":read_joint_positions_from_opcua_equipment_py_pb2",
    ],
)

py_test(
    name = "read_joint_positions_from_opcua_equipment_test",
    size = "small",
    srcs = ["read_joint_positions_from_opcua_equipment_test.py"],
    main = "read_joint_positions_from_opcua_equipment_test.py",
    deps = [
        ":read_joint_positions_from_opcua_equipment",
        "@ai_intrinsic_sdks//intrinsic/hardware/gpio/v1:signal_py_pb2",
    ],
)
