#!/usr/bin/env python3

import logging
import random
import sys
import time

from intrinsic.resources.proto import runtime_context_pb2

from services.configurable_service import configurable_service_pb2


def main():
  logging.info('--------------------------------')
  logging.info('-- Configurable service starting')
  logging.info('--------------------------------')

  with open('/etc/intrinsic/runtime_config.pb', 'rb') as fin:
    context = runtime_context_pb2.RuntimeContext.FromString(fin.read())

  # Parse the configuration
  config = configurable_service_pb2.ConfigurableServiceConfig()
  context.config.Unpack(config)

  if config.seconds_to_sleep < 1:
    raise ValueError(
        f'seconds_to_sleep must be at least 1, got {config.seconds_to_sleep}'
    )

  # Loop forever
  while True:
    logging.info(
        f'My name is {config.name}, and I like to eat'
        f' {random.choice(config.food)}'
    )
    time.sleep(config.seconds_to_sleep)


if __name__ == '__main__':
  logging.basicConfig(stream=sys.stderr, level=logging.INFO)
  main()
