# This alias is required for Intrinsic's internal test infrastructure.
# You do not need a //bazel:linux_x86_64 target in your own workspace.
#
# Internally Intrinsic's CI jobs use --host_platform=//bazel:linux_x86_64
# to specify the platform to run tests on.
# This alias makes sure the Bazel action cache can be reused between
# CI builds of the SDK and CI builds of the SDK Examples.
alias(
    name = "linux_x86_64",
    actual = "@ai_intrinsic_sdks//bazel:linux_x86_64",
)
