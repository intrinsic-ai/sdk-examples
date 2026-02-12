import {
  ExecutiveServiceService,
  OpenAPI,
  SolutionServiceService,
} from './generated';

OpenAPI.BASE = '/http-gateway';

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

  const opsResp =
    await ExecutiveServiceService.executiveServiceListOperations();
  const ops = (opsResp as {operations?: unknown[]})?.operations || [];

  if (ops.length === 0) {
    log('System is clean.');
    return;
  }

  for (const opRaw of ops) {
    const op = opRaw as {name: string};
    const id = op.name.split('/').pop();
    log(`Deleting: ${id}`);
    let deleted = false;
    for (let i = 0; i < 3; i++) {
      try {
        await ExecutiveServiceService.executiveServiceDeleteOperation(op.name);
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
    let treeToRun: Record<string, unknown> | null = null;
    let mode = 'FALLBACK';

    try {
      const list =
        await SolutionServiceService.solutionServiceListBehaviorTrees();
      const trees =
        (list as {behaviorTrees?: Array<{name: string}>}).behaviorTrees || [];
      if (trees.length > 0) {
        const name = trees[0].name;
        log(`Found ${trees.length} tree(s).`);
        log(`Target: "${name}"`);
        const dl =
          await SolutionServiceService.solutionServiceGetBehaviorTree(name);
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
    const create =
      await ExecutiveServiceService.executiveServiceCreateOperation({
        behaviorTree: treeToRun as unknown as Parameters<
          typeof ExecutiveServiceService.executiveServiceCreateOperation
        >[0]['behaviorTree'],
      });
    const opName = (create as {name: string}).name;
    log(`Operation Created!`);
    log(`Created ID: ...${opName.split('/').pop()?.substring(0, 8)}`);

    log('\n4. Starting Execution.');
    await ExecutiveServiceService.executiveServiceStartOperation(opName, {});
    log(`Command Sent successfully!`);

    log('\n5. Checking status.');
    const final =
      await ExecutiveServiceService.executiveServiceGetOperation(opName);
    log(
      `State: ${(final as {metadata?: {operationState?: string}}).metadata?.operationState}`,
    );

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
