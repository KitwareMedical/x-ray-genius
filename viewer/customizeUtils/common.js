import * as url from 'node:url';
import * as path from 'node:path';
import { normalizePath } from 'vite';
import CustomizeConfig from '../custom-app.config.js';

function getDirname() {
  return url.fileURLToPath(new URL('.', import.meta.url));
}

export { CustomizeConfig };
export const ProjectRoot = normalizePath(path.resolve(getDirname(), '..'));
export const OverrideDirPath = normalizePath(
  path.resolve(ProjectRoot, CustomizeConfig.overrideDir)
);
export const CoreDirPath = normalizePath(
  path.resolve(ProjectRoot, CustomizeConfig.coreDir)
);
export const OverrideDirPrefix = OverrideDirPath + '/';
export const CoreDirPrefix = CoreDirPath + '/';
