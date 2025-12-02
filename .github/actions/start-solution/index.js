// 1. Import the toolkit libraries
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
 * Polls the solution status until it is 'running' or a timeout is reached.
 * @param {string} solutionId - The ID of the solution.
 * @param {string} org - The Intrinsic organization.
 */
async function waitForSolutionStart(solutionId, org) {

    const timeoutSeconds = 300; // 5 minutes
    const checkIntervalSeconds = 10;
    let elapsedSeconds = 0;

    core.info(`Waiting for solution '${solutionId}' to be 'running'...`);

    while (elapsedSeconds < timeoutSeconds) {
        let statusOutput = ''; // To capture stdout
        let errorOutput = '';  // To capture stderr

        const options = {
            listeners: {
                stdout: (data) => { statusOutput += data.toString(); },
                stderr: (data) => { errorOutput += data.toString(); }
            },
            ignoreReturnCode: true
        };

        // Run the 'inctl solution get' command
        const exitCode = await exec.exec('inctl', ['solution', 'get', solutionId, '--org', org], options);

        // Check if the command itself failed
        if (exitCode !== 0) {
            core.warning(`'inctl solution get' failed with exit code ${exitCode}: ${errorOutput}`);
        }

        // Check the captured output
        if (statusOutput.includes('is running')) {
            core.info(`Solution '${solutionId}' is now running.`);
            return;
        }

        // Check for timeout
        elapsedSeconds += checkIntervalSeconds;
        if (elapsedSeconds >= timeoutSeconds) {
            throw new Error(`Error: Timed out after ${timeoutSeconds} seconds waiting for solution to start. Last status: ${statusOutput}`);
        }

        // Wait and try again
        core.info(`Not ready yet. Retrying in ${checkIntervalSeconds} seconds.`);
        await sleep(checkIntervalSeconds * 1000);
    }
}

async function run() {
    try {
        // Get inputs from action.yml
        const org = core.getInput('organization', { required: true });
        const solutionId = core.getInput('solution-id', { required: true });
        const vmDuration = core.getInput('vm-duration', { required: true });

        // Lease VM and capture output
        core.info('Requesting VM...');
        let vmInstanceId = '';

        const leaseOptions = {
            listeners: {
                stdout: (data) => { vmInstanceId += data.toString(); },
            }
        };

        // Run the 'inctl vm lease' command
        await exec.exec('inctl', ['vm', 'lease', '--silent', '-d', `${vmDuration}h`, '--org', org], leaseOptions);

        vmInstanceId = vmInstanceId.trim(); // Clean up whitespace
        if (!vmInstanceId) {
            throw new Error('Failed to capture VM instance ID.');
        }
        core.info(`VM lease successful! ID: ${vmInstanceId}`);

        // Save the VM ID and org for the cleanup script
        core.saveState('vmInstanceId', vmInstanceId);
        core.saveState('org', org);
        core.saveState('solutionId', solutionId);

        // Start the solution
        core.info(`Starting solution '${solutionId}'...`);

        const startOptions = {
            env: {
                ...process.env,
                INTRINSIC_SOLUTION: ""
            }
        };

        await exec.exec(
            'inctl',
            ['solution', 'start', solutionId, '--org', org, '--cluster', vmInstanceId],
            startOptions
        );

        await waitForSolutionStart(solutionId, org);
        core.info('Waiting 3 minutes for propagation...');
        await sleep(180 * 1000);

    } catch (error) {
        core.setFailed(error.message);
    }
}

run();
