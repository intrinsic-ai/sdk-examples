load("@ai_intrinsic_sdks//bazel:python_oci_image.bzl", "python_oci_image")
load("@ai_intrinsic_sdks//intrinsic/assets/services/build_defs:services.bzl", "intrinsic_service")
load("@container_structure_test//:defs.bzl", "container_structure_test")
load("@rules_oci//oci:defs.bzl", "oci_load")
load("@rules_pkg//:pkg.bzl", "pkg_tar")

filegroup(
    name = "frontend_files",
    srcs = glob(["frontend/**"]),
)

py_binary(
    name = "server",
    srcs = ["server.py"],
    data = [":frontend_files"],
    main = "server.py",
    deps = [
        "@ai_intrinsic_sdks//intrinsic/executive/proto:executive_service_py_pb2_grpc",
        "@ai_intrinsic_sdks//intrinsic/resources/proto:runtime_context_py_pb2",
    ],
)

pkg_tar(
    name = "server_layer",
    srcs = [":server"],
    extension = "tar.gz",
    include_runfiles = True,
    strip_prefix = "/",
)

python_oci_image(
    name = "hmi_image",
    base = "@distroless_python3",
    binary = "server",
    data_path = "/frontend/",
    entrypoint = [
        "python3",
        "-u",
        "/services/hmi_python/server",
    ],
    extra_tars = [":server_layer"],
)

oci_load(
    name = "hmi_tarball",
    image = ":hmi_image",
    repo_tags = ["hmi:latest"],
)

filegroup(
    name = "hmi_tarball.tar",
    srcs = [":hmi_tarball"],
    output_group = "tarball",
)

container_structure_test(
    name = "hmi_tarball_test",
    configs = ["testdata/image_files.yaml"],
    driver = "tar",
    image = ":hmi_tarball.tar",
)

intrinsic_service(
    name = "hmi_service",
    images = [":hmi_tarball.tar"],
    manifest = "manifest.textproto",
)
