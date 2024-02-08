# Custom VolView Template

This custom app template uses file overrides to customize a webapp built using Vite.

## Getting Started

1. Edit `custom-app.config.js` to configure this custom template. If you are customizing VolView, you can leave it as-is.
2. Run `npm install && npm run setup-project` to checkout VolView and configure the project configuration.

Once everything has been installed, you can look inside `app/` for a sample file override, which updates some configuration keys.

All vite commands are supported:
- `npm run dev`: run the dev server
- `npm run build`: build the app
- `npm run preview`: preview a production-build of the app

## Override Behavior

File overriding is the primary customization behavior of this template. Files inside the override directory must match the relative file path in the core repository in order to be overridden.

Imports can be classified into 3 types: override-to-override, override-to-core, and core-to-core.
- override-to-override: an override file imports from another override file. No change in behavior.
- override-to-core: override files can import core files, even if there is an override file for that core file. This allows override files to extend core files merely by importing.
- core-to-core: core files importing other core files works as-is, unless an override file is present in the override directory.

## Troubleshooting and Technical Details

The target customization app is checked out and added as a git submodule. The "coreDir" key in `custom-app.config.js` determines where this submodule resides.

If the submodule ever gets out of sync (e.g. with a dirty tree), remove all changes in the submodule. The submodule is intended to be read-only, as the override directory is where you should make changes.