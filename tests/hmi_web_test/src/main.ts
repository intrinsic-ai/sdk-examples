import {
  IntrinsicProtoExecutiveBehaviorTree,
  executiveServiceCreateOperation,
  executiveServiceDeleteOperation,
  executiveServiceGetOperation,
  executiveServiceListOperations,
  executiveServiceStartOperation,
  solutionServiceGetBehaviorTree,
  solutionServiceListBehaviorTrees,
} from './generated';
import {client} from './generated/client.gen';

client.setConfig({
  baseUrl: '/http-gateway',
});

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

function log(msg: string) {
  const el = document.getElementById('logs');
  if (el) {
    el.textContent += '\n' + msg;
    el.scrollTop = el.scrollHeight;
  }
  console.log(msg);
}

async function forceCleanup() {
  log('Attempting cleanup');

  const operationsResponse = await executiveServiceListOperations();
  const operations = operationsResponse.data?.operations ?? [];

  if (operations.length === 0) {
    log('System is clean.');
    return;
  }

  for (const op of operations) {
    const id = op.name?.split('/').pop();

    if (!id || !op.name) return;

    log(`Deleting: ${id}`);
    let deleted = false;
    for (let i = 0; i < 3; i++) {
      try {
        await executiveServiceDeleteOperation({
          path: {name: op.name},
        });
        deleted = true;
        log(`Deleted successfully.`);
        break;
      } catch (e) {
        log(`Delete failed (Attempt ${i + 1}/3). Retrying in 2s...`);
        await sleep(2000);
      }
    }

    if (!deleted) {
      log(
        'CRITICAL: Could not delete operation. Server might require a manual restart.',
      );
      throw new Error('Process Refused to Delete');
    }
  }
}

async function runTestSequence() {
  const btn = document.getElementById('runTestBtn') as HTMLButtonElement;
  btn.disabled = true;

  log('STARTING HMI TEST');

  try {
    log('\n1. Safety Cleanup.');
    try {
      await forceCleanup();
    } catch (e) {
      log(`Cleanup Warning: ${e}`);
    }

    log('\n2. Checking for Existing Behavior Trees.');
    let treeToRun: IntrinsicProtoExecutiveBehaviorTree | null = null;
    let mode = 'FALLBACK';

    try {
      const listResponse = await solutionServiceListBehaviorTrees();
      const list = listResponse.data;
      const trees = list?.behaviorTrees ?? [];

      if (trees.length > 0) {
        const name = trees[0].name;
        if (!name) return;

        log(`Found ${trees.length} tree(s).`);
        log(`Target: "${name}"`);

        const behaviorTreeResponse = await solutionServiceGetBehaviorTree({
          path: {name},
        });

        const dl = behaviorTreeResponse.data;

        if (dl) {
          treeToRun = dl;
          mode = 'REAL_TREE';
          log('Download Success!');
        }
      } else {
        log('List is empty. No trees found on server.');
      }
    } catch (e) {
      log('Download failed. Switching to Manual Fallback.');
    }

    if (!treeToRun) {
      mode = 'MANUAL_FALLBACK';
      treeToRun = {
        treeId: 'web-' + Date.now(),
        name: 'Web Fallback',
        root: {sequence: {}},
      };
    }

    log(`\n3. Creating Operation (Mode: ${mode})`);
    const createOperation = await executiveServiceCreateOperation({
      body: {behaviorTree: treeToRun},
    });

    const opName = createOperation.data?.name;
    if (!opName) return;

    log(`Operation Created!`);
    log(`Created ID: ...${opName.split('/').pop()?.substring(0, 8)}`);

    log('\n4. Starting Execution.');
    await executiveServiceStartOperation({
      path: {name: opName},
      body: {},
    });
    log(`Command Sent successfully!`);

    log('\n5. Checking status.');
    const final = await executiveServiceGetOperation({
      path: {name: opName},
    });
    log(`State: ${final.data?.metadata?.operationState}`);

    log(`TEST COMPLETED: (${mode})`);
  } catch (e) {
    log(`ERROR: ${e}`);
  } finally {
    btn.disabled = false;
  }
}

document
  .getElementById('runTestBtn')
  ?.addEventListener('click', runTestSequence);
