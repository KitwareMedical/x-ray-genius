const tailwindConfig = require('../tailwind.config.js');

module.exports = {
    port: 8383,
    reloadOnRestart: true,
    logSnippet: false,
    logFileChanges: false,
    open: false,
    ui: false,
    notify: false,
    // Paths of "files" are relative to the npm package root (the location of "package.json")
    files: [
      // Locally built outputs
      './xray_genius/core/static/core/dist/*',
      // HTML templates, watched by Tailwind
      ...tailwindConfig.content
    ],
}
