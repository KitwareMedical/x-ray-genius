import * as path from 'node:path';
import simpleGit from 'simple-git';
import { CustomizeConfig, ProjectRoot } from '../common.js';

/**
 * Updates the core submodule
 */
async function main() {
  process.chdir(ProjectRoot);
  const git = simpleGit();
  await git
    .subModule([
      'add',
      '--force',
      CustomizeConfig.coreRepo.url,
      CustomizeConfig.coreDir,
    ])
    .submoduleInit()
    .submoduleUpdate(CustomizeConfig.coreDir);

  const subgit = simpleGit(path.resolve(ProjectRoot, CustomizeConfig.coreDir));
  // subgit.clean()
  await subgit.checkout(CustomizeConfig.coreRepo.ref);
}

await main();
