import * as path from 'node:path';
import { defineConfig, loadConfigFromFile } from 'vite';
import { OverrideResolverPlugin } from './rollup-plugin-override-resolver';
import { CoreDirPath, ProjectRoot } from '../common';

export default defineConfig(async (configEnv) => {
  const loadResult = await loadConfigFromFile(
    configEnv,
    path.resolve(CoreDirPath, 'vite.config.ts')
  );

  if (!loadResult) throw new Error('Failed to load vite.config.ts from core.');
  const viteConfig = loadResult.config;

  viteConfig.root = CoreDirPath;
  viteConfig.envDir = ProjectRoot;

  viteConfig.plugins ||= [];
  viteConfig.plugins!.unshift(OverrideResolverPlugin);

  return viteConfig;
});
