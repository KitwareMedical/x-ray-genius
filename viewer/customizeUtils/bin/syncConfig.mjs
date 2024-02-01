import * as fs from 'node:fs';
import * as path from 'node:path';
import { CoreDirPath, ProjectRoot } from '../common.js';
import { normalizePath } from 'vite';

const RelCorePath = normalizePath(path.relative(ProjectRoot, CoreDirPath));

/**
 * Syncs tsconfig.json, setting the "paths" key to resolve "@/*".
 */
function syncTsConfig() {
  const tsconfigFile = path.resolve(ProjectRoot, 'tsconfig.json');
  let tsconfig = {};
  try {
    const contents = fs.readFileSync(tsconfigFile, { encoding: 'utf-8' });
    tsconfig = JSON.parse(contents || '{}');
  } catch (err) {
    throw new Error('Failed to parse tsconfig.json');
  }

  tsconfig.compilerOptions ||= {};
  tsconfig.compilerOptions.paths ||= {};

  tsconfig.compilerOptions.paths['@/*'] = [`./${RelCorePath}/*`];

  try {
    const contents = fs.writeFileSync(
      tsconfigFile,
      JSON.stringify(tsconfig, null, 2)
    );
    tsconfig = JSON.parse(contents || '{}');
  } catch (err) {
    throw new Error('Failed to parse tsconfig.json');
  }
}

function syncEslintConfig() {
  const eslintFile = path.resolve(ProjectRoot, '.eslintrc.cjs');
  const contents = `const config = require('./${RelCorePath}/.eslintrc.cjs');`;
  fs.writeFileSync(eslintFile, contents);
}

function syncPackageConfig() {
  const rootPkgJsonFile = `${ProjectRoot}/package.json`;
  const corePkgJsonFile = `${CoreDirPath}/package.json`;
  const rootPkgJson = JSON.parse(
    fs.readFileSync(rootPkgJsonFile, { encoding: 'utf-8' })
  );
  const corePkgJson = JSON.parse(
    fs.readFileSync(corePkgJsonFile, { encoding: 'utf-8' })
  );

  // The root package.json overrides core package.json,
  // but the core package-lock.json is used.
  const merge = (fromDeps, toDeps) => {
    Object.entries(fromDeps).forEach(([dep, version]) => {
      if (!(dep in toDeps)) {
        toDeps[dep] = version;
      }
    });
  };

  merge(corePkgJson.dependencies, rootPkgJson.dependencies);
  merge(corePkgJson.devDependencies, rootPkgJson.devDependencies);

  fs.writeFileSync(rootPkgJsonFile, JSON.stringify(rootPkgJson, null, 2));

  // copy over the package-lock.json
  // NOTE this does not handle merging, nor accuracy
  // of the lockfile name/version/etc.
  const rootPkgLockFile = `${ProjectRoot}/package-lock.json`;
  const corePkgLockFile = `${CoreDirPath}/package-lock.json`;

  fs.writeFileSync(
    rootPkgLockFile,
    fs.readFileSync(corePkgLockFile, { encoding: 'utf-8' })
  );
}

function main() {
  syncTsConfig();
  syncEslintConfig();
  syncPackageConfig();
}

main();
