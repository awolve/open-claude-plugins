---
description: Show available awolve-signum commands and what they do
---

# /awolve-signum:help

Show a quick reference of all available awolve-signum commands.

## Instructions

Print the following command reference. Do NOT run any scripts — just display this information.

### Setup & Sync
| Command | Description |
|---------|-------------|
| `/awolve-signum:login` | Authenticate with Signum (Azure CLI or API key) |
| `/awolve-signum:status` | Show sync status and authentication info |
| `/awolve-signum:pull` | Pull latest spec files from the service |
| `/awolve-signum:conflicts` | List spec-sync conflicts staged out-of-tree (per-machine cache) |
| `/awolve-signum:cleanup-synced-tree` | Purge legacy in-tree sync/build artifacts from the synced specs tree |
| `/awolve-signum:update-plugins` | Refresh the marketplace and reload the session |
| `/awolve-signum:help` | Show this reference |

### Spec Writing
| Command | Description |
|---------|-------------|
| `/awolve-signum:req` | Write requirements.md — what to build and why |
| `/awolve-signum:design` | Write design.md — how to build it |
| `/awolve-signum:plan` | Write plan.md — implementation approach and task breakdown |
| `/awolve-signum:infra` | Enrich design.md with infrastructure specifications |
| `/awolve-signum:retro` | Document work after the fact from what was built |

### Features & Documents
| Command | Description |
|---------|-------------|
| `/awolve-signum:list-features` | List all features in a project |
| `/awolve-signum:create-feature` | Create a new feature |
| `/awolve-signum:rename-feature` | Rename a feature |
| `/awolve-signum:delete-feature` | Delete a feature and all its documents |
| `/awolve-signum:create-doc` | Add a document to an existing feature |
| `/awolve-signum:rename-doc` | Rename a document |
| `/awolve-signum:delete-doc` | Delete a document |
| `/awolve-signum:set-status` | Change the status of a feature or document |
| `/awolve-signum:set-description` | Set or clear a feature's short description |
| `/awolve-signum:set-title` | Update a feature's display title without renaming the slug |

### Backlog & Bugs
| Command | Description |
|---------|-------------|
| `/awolve-signum:backlog` | List backlog items for a project (filterable by assignee and tag) |
| `/awolve-signum:backlog-add` | Add a new idea or feature request to the backlog |
| `/awolve-signum:view-backlog` | Show full details of a single backlog item |
| `/awolve-signum:backlog-update` | Update an item's title, description, priority, status, assignee, epic flag, or deployment info |
| `/awolve-signum:backlog-set-parent` | Set or clear the parent (epic) of a backlog item |
| `/awolve-signum:backlog-depend` | Make an item wait for another (sets it Blocked) |
| `/awolve-signum:backlog-undepend` | Remove a dependency (restores the previous status) |
| `/awolve-signum:backlog-delete` | Soft-delete a backlog item (cascades to children) |
| `/awolve-signum:restore-backlog` | Restore a soft-deleted backlog item (internal users only) |
| `/awolve-signum:backlog-comments` | List comments on a backlog item |
| `/awolve-signum:backlog-comment` | Add a comment to a backlog item |
| `/awolve-signum:edit-backlog-comment` | Edit a backlog comment (author only) |
| `/awolve-signum:delete-backlog-comment` | Delete a backlog comment (author only) |
| `/awolve-signum:bugs` | List open bugs (filterable by assignee and tag) |
| `/awolve-signum:my-daily` | What was assigned to you recently, across all your projects (the daily mail's list) |
| `/awolve-signum:my-weekly` | Everything open assigned to you, across all your projects (the weekly mail's list) |
| `/awolve-signum:bug` | Report a new bug |
| `/awolve-signum:view-bug` | Show full details of a single bug (`--images` saves its screenshots) |
| `/awolve-signum:update-bug` | Edit a bug's title, description, severity, assignee, tags, or deployment info |
| `/awolve-signum:set-bug-status` | Change a bug's status |
| `/awolve-signum:delete-bug` | Soft-delete a bug (internal users only) |
| `/awolve-signum:bug-comments` | List comments on a bug |
| `/awolve-signum:bug-comment` | Add a comment to a bug |
| `/awolve-signum:edit-bug-comment` | Edit a bug comment (author only) |
| `/awolve-signum:delete-bug-comment` | Delete a bug comment (author only) |
| `/awolve-signum:edit-comment` | Edit a spec-doc comment (author only) |
| `/awolve-signum:delete-comment` | Delete a spec-doc comment (author only) |


### Feedback users (in-app feedback widgets)
| Command | Description |
|---------|-------------|
| `/awolve-signum:feedback-users` | List a project's feedback users — write-only credentials an app's backend holds so its users can file bugs and ideas |
| `/awolve-signum:feedback-user-create` | Create a feedback user on a project |
| `/awolve-signum:feedback-user-update` | Rename it, or set its origin allowlist and rate limits |
| `/awolve-signum:feedback-user-delete` | Delete it and revoke every key; its reports stay |
| `/awolve-signum:feedback-key-create` | Mint a key (shown once) for the app's backend secret store |
| `/awolve-signum:feedback-key-revoke` | Revoke one key — the kill switch |
### Attachments
| Command | Description |
|---------|-------------|
| `/awolve-signum:attach` | Upload a binary file to a feature, bug, or backlog item |
| `/awolve-signum:list-attachments` | List attachments on a feature, bug, or backlog item |
| `/awolve-signum:download-attachment` | Download an attachment by id |
| `/awolve-signum:delete-attachment` | Delete an attachment by id |

### Activity
| Command | Description |
|---------|-------------|
| `/awolve-signum:log` | Recent audit activity — what happened since your last visit |

### Tags
| Command | Description |
|---------|-------------|
| `/awolve-signum:tags` | List a project's tags and how many items wear each one |
| `/awolve-signum:tag-create` | Create a tag (nudges you toward an existing one when close) |
| `/awolve-signum:tag-update` | Rename, recolour, or re-describe a tag |
| `/awolve-signum:tag-delete` | Delete a tag, optionally detaching it from every item |

Tags are per-project labels shared by backlog items and bugs. Applying one needs only the right to edit the item; creating and renaming them needs the developer or admin role.

### Skill
| Skill | Description |
|-------|-------------|
| `/awolve-signum:spec` | General spec skill — triggers on spec-related questions |

Offer to run any command the user is interested in.
