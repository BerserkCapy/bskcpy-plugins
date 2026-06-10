# bskcpy-plugins

> Berserk energy, capybara pace.

A personal Claude Code plugin marketplace. Wildly productive, completely unbothered.

## Install

```
/plugin marketplace add github:Capybara-sama/bskcpy-plugins
```

or via `/plugin > Discover > Manage Marketplaces`.

## Browse & Install Plugins

After adding the marketplace:

```
/plugin install <plugin-name>@bskcpy-plugins
```

## Structure

```
bskcpy-plugins/
├── .claude-plugin/
│   └── marketplace.json   # Marketplace metadata
├── plugins/               # Plugins bundled in this repo
├── external_plugins/      # Third-party plugin references
└── README.md
```

## Adding Plugins

### Bundled plugin (in this repo)

1. Create a directory under `plugins/<plugin-name>/`
2. Add `.claude-plugin/plugin.json` with plugin metadata
3. Add your commands, agents, skills, hooks as needed
4. Add the plugin entry to `.claude-plugin/marketplace.json`

### External plugin (reference only)

Add an entry to `.claude-plugin/marketplace.json` with `"source": { "source": "github", "repo": "<owner>/<repo>" }`.

## License

MIT
