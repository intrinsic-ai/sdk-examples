load("@ai_intrinsic_sdks//bazel:skills.bzl", "py_skill", "skill_manifest")
load("@com_github_grpc_grpc//bazel:python_rules.bzl", "py_proto_library")
load("@com_google_protobuf//bazel:proto_library.bzl", "proto_library")

proto_library(
    name = "write_joint_positions_to_opcua_equipment_proto",
    srcs = ["write_joint_positions_to_opcua_equipment.proto"],
)

py_proto_library(
    name = "write_joint_positions_to_opcua_equipment_py_pb2",
    deps = [":write_joint_positions_to_opcua_equipment_proto"],
)

skill_manifest(
    name = "write_joint_positions_to_opcua_equipment_py_manifest",
    src = "write_joint_positions_to_opcua_equipment.manifest.textproto",
    deps = [":write_joint_positions_to_opcua_equipment_proto"],
)

py_library(
    name = "write_joint_positions_to_opcua_equipment",
    srcs = ["write_joint_positions_to_opcua_equipment.py"],
    deps = [
        ":write_joint_positions_to_opcua_equipment_py_pb2",
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
    name = "write_joint_positions_to_opcua_equipment_image",
    manifest = ":write_joint_positions_to_opcua_equipment_py_manifest",
    deps = [
        ":write_joint_positions_to_opcua_equipment",
        ":write_joint_positions_to_opcua_equipment_py_pb2",
    ],
)

py_test(
    name = "write_joint_positions_to_opcua_equipment_test",
    size = "small",
    srcs = ["write_joint_positions_to_opcua_equipment_test.py"],
    main = "write_joint_positions_to_opcua_equipment_test.py",
    deps = [
        ":write_joint_positions_to_opcua_equipment",
        "@ai_intrinsic_sdks//intrinsic/hardware/gpio/v1:signal_py_pb2",
        "@ai_intrinsic_sdks//intrinsic/icon/python:icon",
    ],
)
