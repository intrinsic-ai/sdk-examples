load("@rules_foreign_cc//foreign_cc:defs.bzl", "cmake")

filegroup(
    name = "all_srcs",
    srcs = glob(["**"]),
    visibility = ["//visibility:public"],
)

cmake(
    name = "opencv",
    generate_args = [
        "-GNinja",
        "-DBUILD_LIST=core,imgproc,calib3d,objdetect",
        "-D BUILD_SHARED_LIBS:BOOL=OFF",
        "-D BUILD_PACKAGE:BOOL=OFF",
        "-D BUILD_PERF_TESTS:BOOL=OFF",
        "-D BUILD_TESTS:BOOL=OFF",
        "-D BUILD_JAVA:BOOL=OFF",
        "-D OPENCV_FORCE_3RDPARTY_BUILD:BOOL=ON",
        "-D WITH_1394:BOOL=OFF",
        "-D WITH_IPP:BOOL=OFF",
        "-D WITH_JASPER:BOOL=OFF",
        "-D WITH_OPENJPEG:BOOL=OFF",
        "-D WITH_PNG:BOOL=OFF",
        "-D WITH_TBB:BOOL=OFF",
    ],
    lib_source = ":all_srcs",
    out_include_dir = "include/opencv4",
    out_static_libs = [
        "libopencv_core.a",
        "libopencv_imgproc.a",
        "libopencv_calib3d.a",
        "libopencv_objdetect.a",
        "opencv4/3rdparty/libittnotify.a",
        "opencv4/3rdparty/libquirc.a",
    ],
    visibility = ["//visibility:public"],
)
