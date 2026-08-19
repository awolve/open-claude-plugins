---
description: Show available awolve-spec commands and what they do
---

# /awolve-spec:help

Show a quick reference of all available awolve-spec commands.

## Instructions

Print the following command reference. Do NOT run any scripts — just display this information.

### Setup & Sync
| Command | Description |
|---------|-------------|
| `/awolve-spec:login` | Authenticate with the spec service (Azure CLI or API key) |
| `/awolve-spec:status` | Show sync status and authentication info |
| `/awolve-spec:pull` | Pull latest spec files from the service |

### Spec Writing
| Command | Description |
|---------|-------------|
| `/awolve-spec:req` | Write requirements.md — what to build and why |
| `/awolve-spec:design` | Write design.md — how to build it |
| `/awolve-spec:plan` | Write plan.md — implementation approach and task breakdown |
| `/awolve-spec:infra` | Enrich design.md with infrastructure specifications |
| `/awolve-spec:retro` | Document work after the fact from what was built |

### Features & Documents
| Command | Description |
|---------|-------------|
| `/awolve-spec:list-features` | List all features in a project |
| `/awolve-spec:create-feature` | Create a new feature |
| `/awolve-spec:rename-feature` | Rename a feature |
| `/awolve-spec:delete-feature` | Delete a feature and all its documents |
| `/awolve-spec:create-doc` | Add a document to an existing feature |
| `/awolve-spec:rename-doc` | Rename a document |
| `/awolve-spec:delete-doc` | Delete a document |
| `/awolve-spec:set-status` | Change the status of a feature or document |
| `/awolve-spec:set-description` | Set or clear a feature's short description |
| `/awolve-spec:set-title` | Update a feature's display title without renaming the slug |
| `/awolve-spec:attach` | Upload a binary file as an attachment to a feature |

### Backlog & Bugs
| Command | Description |
|---------|-------------|
| `/awolve-spec:backlog` | List backlog items for a project (filterable by assignee and tag) |
| `/awolve-spec:backlog-add` | Add a new idea or feature request to the backlog |
| `/awolve-spec:bugs` | List open bugs (filterable by assignee and tag) |
| `/awolve-spec:bug` | Report a new bug |
| `/awolve-spec:view-bug` | Show full details of a single bug |
| `/awolve-spec:update-bug` | Edit a bug's title, description, severity, assignee, or tags |
| `/awolve-spec:set-bug-status` | Change a bug's status |
| `/awolve-spec:bug-comments` | List comments on a bug |
| `/awolve-spec:bug-comment` | Add a comment to a bug |
| `/awolve-spec:edit-bug-comment` | Edit a bug comment (author or internal user) |
| `/awolve-spec:delete-bug-comment` | Delete a bug comment (author or internal user) |
| `/awolve-spec:edit-comment` | Edit a spec-doc comment (author only) |
| `/awolve-spec:delete-comment` | Delete a spec-doc comment (author only) |

### Tags
| Command | Description |
|---------|-------------|
| `/awolve-spec:tags` | List a project's tags and how many items wear each one |
| `/awolve-spec:tag-create` | Create a tag (nudges you toward an existing one when close) |
| `/awolve-spec:tag-update` | Rename, recolour, or re-describe a tag |
| `/awolve-spec:tag-delete` | Delete a tag, optionally detaching it from every item |

Tags are per-project labels shared by backlog items and bugs. Applying one needs only the right to edit the item; creating and renaming them needs the developer or admin role.

### Skill
| Skill | Description |
|-------|-------------|
| `/awolve-spec:spec` | General spec skill — triggers on spec-related questions |

Offer to run any command the user is interested in.
