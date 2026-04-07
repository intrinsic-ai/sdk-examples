#include <iostream>
#include <string>
#include <vector>

#include "absl/log/check.h"
#include "absl/log/log.h"
#include "absl/random/random.h"
#include "absl/status/status.h"
#include "absl/strings/string_view.h"
#include "absl/time/clock.h"
#include "absl/time/time.h"
#include "intrinsic/icon/release/file_helpers.h"
#include "intrinsic/icon/release/portable/init_intrinsic.h"
#include "intrinsic/resources/proto/runtime_context.pb.h"
#include "intrinsic/util/proto/any.h"
#include "intrinsic/util/status/status_macros.h"
#include "services/configurable_service/configurable_service.pb.h"

absl::Status MainImpl() {
  LOG(INFO) << "------------------------------------";
  LOG(INFO) << "-- Configurable C++ service starting";
  LOG(INFO) << "------------------------------------";

  constexpr absl::string_view kContextFilePath =
      "/etc/intrinsic/runtime_config.pb";

  // Read the RuntimeContext from the binary proto file
  INTR_ASSIGN_OR_RETURN(
      const auto context,
      intrinsic::GetBinaryProto<intrinsic_proto::config::RuntimeContext>(
          kContextFilePath),
      _ << "Reading runtime context from " << kContextFilePath);

  // Parse/Unpack the service-specific configuration
  auto config =
      std::make_unique<configurable_service::ConfigurableServiceConfig>();
  INTR_RETURN_IF_ERROR(intrinsic::UnpackAny(context.config(), *config));

  // Validation
  if (config->seconds_to_sleep() < 1) {
    return absl::InvalidArgumentError(
        absl::StrCat("seconds_to_sleep must be at least 1, got ",
                     config->seconds_to_sleep()));
  }

  // Setup randomness for food selection
  absl::BitGen bitgen;
  const int food_count = config->food_size();

  // Loop forever
  while (true) {
    std::string chosen_food = "nothing";
    if (food_count > 0) {
      int index = absl::Uniform(bitgen, 0, food_count);
      chosen_food = config->food(index);
    }

    LOG(INFO) << "My name is " << config->name() << ", and I like to eat "
              << chosen_food;

    absl::SleepFor(absl::Seconds(config->seconds_to_sleep()));
  }

  return absl::OkStatus();
}

int main(int argc, char** argv) {
  // Initialize logging and internal frameworks
  InitIntrinsic(argv[0], argc, argv);

  // Execute logic and check for terminal errors
  QCHECK_OK(MainImpl());

  return 0;
}
