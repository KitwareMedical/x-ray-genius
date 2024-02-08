import * as path from "node:path";
import { execFileSync } from "node:child_process";
import { CoreDirPath, CoreDirPrefix, ProjectRoot } from "../common.js";

/**
 * Runs npm install path/to/app/
 */
function main() {
  process.chdir(ProjectRoot);
  try {
    process.stdout.write(
      execFileSync("npm", ["install", CoreDirPrefix], { shell: true })
    );
  } catch (err) {
    process.stderr.write(String(err));
    process.exit(1);
  }
}

main();
