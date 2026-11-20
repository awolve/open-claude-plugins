---
name: awolve-spec:mockup
description: Write a visual mockup or wireframe for a Signum feature, as a static HTML page under mockups/ that reviewers can comment on with boxes and arrows, and link mockups into a clickable flow. Use when the user asks for a mockup, wireframe, screen sketch or UI draft for a feature, wants to link screens into a flow, or wants to work through comments left on a mockup.
---

# Mockups in Signum

A mockup is a document of a feature, like `requirements.md`: it has versions, a status (`specifying` → `ready` → `approved`) and comments. Reviewers draw a box or an arrow on the page and comment on that spot. Links between mockups in the same feature can be clicked, so a reviewer can walk a flow screen by screen.

Two example pages that link to each other: `example/login.html` and `example/dashboard.html` beside this file.

## Where it lives

- Path: `<feature folder>/mockups/<name>.html`. Lower case letters, digits, `.`, `_`, `-`. No subfolders.
- Register it once:

  ```bash
  python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py create-doc <project-id> <feature-name> mockups/<name>.html
  ```

  If the file already exists, its HTML becomes version 1. If not, an empty page is created for you to fill.
- The sync header sits at the top inside an HTML comment (`<!-- --- spec_doc_id: … --- -->`). Leave it alone; the plugin keeps it out of what is pushed.
- After that, every Write or Edit on the file pushes a new version, as for markdown specs.

## Shape of the page

Signum shows the page with JavaScript off, in an isolated frame. Build only what static HTML and CSS can show.

- One self-contained file. All CSS in one `<style>` block in `<head>`.
- No `<script>`, no `on*` attributes, no `javascript:` links. They never run, so anything built with them will not show.
- No forms that need to submit. Draw fields and buttons; they will not do anything.
- Images and fonts only as `data:` or `https:` URLs. Nothing relative except links to other mockups. Web images or fonts may be blocked for some viewers; the page must still read without them.
- At most 2 MB.

## Size

- Set the width you design for: `<meta name="signum:design-width" content="1280">`. Default is 1280. Use the real target, e.g. `390` for a phone screen.
- Lay the page out for exactly that width (`body { width: 1280px; margin: 0; }` or a fixed-width wrapper). Signum scales it down on smaller screens, so every viewer sees the same layout and marks land on the same spot.
- The page can be as tall as it needs. Do not give the page its own scrolling area (`height: 100vh; overflow: auto`): comment marks would drift.

## Links between mockups

- Link to another mockup by its bare filename: `<a href="dashboard.html">`. `./dashboard.html` also works.
- Only mockups in the same feature open. Anything else (an external URL, a folder, `..`, another feature) shows as a broken link and does nothing.
- Use `<a>` for every clickable thing in a flow, and style it as a button where a button is meant. A `<button>` cannot navigate.
- A link to a screen not drawn yet is fine. It shows as broken until that mockup exists, which is how gaps in the flow show up.
- `#fragment` and `?query` are ignored; the target opens at its top.

## Wireframe or mockup

- **Wireframe:** greys, plain boxes, system font, `[PLACEHOLDER]` text. Use this when layout and flow are the question.
- **Mockup:** the product's real look, using its brand or design system when one is known (at Awolve: the client's brand, or the Awolve brand for internal tools). Use this when the look is the question.
- Never present invented data as real. Use clearly fake names and numbers, or placeholders.

## Review loop

1. Read the comments:

   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py comments <feature-folder>/mockups/<name>.html
   ```

   An area comment prints as `#3 box (596,118)–(684,170) on v1: Logo is too small`. Coordinates are design pixels from the top-left of the page at the design width. An arrow prints `arrow (x1,y1)→(x2,y2)` and points at its end point. `on v1` is the version the comment was made on; the page may have moved since.
2. Find the element at that spot in the HTML, change it, and save. The hook pushes a new version.
3. Answer on the mockup with a comment that names the number, e.g. `#3: logo is now 48 px high`:

   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py comment <feature-folder>/mockups/<name>.html "#3: logo is now 48 px high"
   ```

4. Do not resolve another person's comment unless asked. They check the new version and resolve it.
