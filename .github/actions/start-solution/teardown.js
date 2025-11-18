const core = require('@actions/core');
const exec = require('@actions/exec');

/**
 * Sleeps for a given number of milliseconds.
 * @param {number} ms - The number of milliseconds to sleep.
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Polls the solution status until it is 'not running' or a timeout is reached.
 * @param {string} solutionId - The ID of the solution.
 * @param {string} org - The Intrinsic organization.
 */
async function waitForSolutionStop(solutionId, org) {
  const timeoutSeconds = 300; // 5 minutes
  const checkIntervalSeconds = 10;
  let elapsedSeconds = 0;

  core.info(`Waiting for solution '${solutionId}' to be 'not running'...`);

  while (elapsedSeconds < timeoutSeconds) {
    let statusOutput = '';
    let errorOutput = '';

    const options = {
      listeners: {
        stdout: (data) => { statusOutput += data.toString(); },
        stderr: (data) => { errorOutput += data.toString(); }
      },
      ignoreReturnCode: true
    };

    const exitCode = await exec.exec('inctl', ['solution', 'get', solutionId, '--org', org], options);

    if (exitCode !== 0) {
      core.warning(`'inctl solution get' failed during teardown: ${errorOutput}`);
    }

    // Check for "not running"
    if (statusOutput.includes('not running')) {
      core.info(`Solution '${solutionId}' is now stopped.`);
      return; 
    }

    elapsedSeconds += checkIntervalSeconds;
    if (elapsedSeconds >= timeoutSeconds) {
      core.warning(`Warning: Timed out after ${timeoutSeconds} seconds waiting for solution to stop. Last status: ${statusOutput}`);
      return;
    }

    core.info(`Not stopped yet. Retrying in ${checkIntervalSeconds} seconds.`);
    await sleep(checkIntervalSeconds * 1000);
  }
}

async function teardown() {
  core.info('--- Starting Teardown ---');
  try {
    // Get the variables from the index.js
    const vmInstanceId = core.getState('vmInstanceId');
    const org = core.getState('org');
    const solutionId = core.getState('solutionId');

    // Check if we have anything to clean up
    if (!vmInstanceId || !org || !solutionId) {
      core.warning('Missing state variables. Teardown may have failed or already run.');
      return;
    }

    // Stop Solution
    core.info(`Stopping solution '${solutionId}'...`);

    const stopOptions = {
      env: {
        ...process.env,
        INTRINSIC_SOLUTION: ""
      }
    };

    await exec.exec(
      'inctl',
      ['solution', 'stop', solutionId, '--org', org, '--cluster', vmInstanceId],
      stopOptions
    );
    await waitForSolutionStop(solutionId, org);

    // Return VM 
    core.info(`Returning VM '${vmInstanceId}'...`);
    await exec.exec('inctl', ['vm', 'return', vmInstanceId, '--org', org]);

    core.info('--- Teardown Finished ---');

  } catch (error) {
    core.warning(`Teardown failed: ${error.message}`);
  }
}

teardown();
