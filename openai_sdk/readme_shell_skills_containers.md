# Shell, Skills, And Containers Guide

This guide explains how three related concepts fit together in the OCI GenAI OpenAI-compatible examples:

1. `shell` tool: lets a model request command-line work.
2. Containers: hosted stateful workspaces where OCI can run shell commands and store files.
3. Skills: reusable workflow bundles that tell the model how to perform repeatable tasks.

Use this guide before moving through:

- `genai_client/shell_tool.py`
- `genai_client/shell_tools/`
- `genai_client/containers/readme_containers.md`
- `skills/readme_skills.md`

## Mental Model

A normal Responses API call sends text to a model and receives text back.

A tool-enabled Responses API call gives the model extra capabilities. The model can decide to use a tool when the task needs it.

For Shell Tool workflows, the flow is:

1. Your Python script creates an OpenAI-compatible client through `OpenAIClientProvider`.
2. Your request includes `tools=[{"type": "shell", ...}]`.
3. The model decides whether shell commands are useful.
4. The shell commands run in either:
   - a hosted OCI container, or
   - your own local runtime.
5. The model reads command results and returns a final answer or creates files.

Containers and Skills are supporting pieces:

- Containers provide the execution workspace.
- Container Files provide inputs and generated artifacts.
- Skills provide reusable instructions, scripts, templates, schemas, examples, and references.

## Shell Tool

The Shell Tool is for terminal-native tasks:

- inspect files
- run scripts
- validate builds
- run tests
- generate reports
- transform data
- install user-space dependencies when network policy allows it
- call approved APIs when network policy and auth allow it

### Hosted Shell

Hosted shell means OCI runs the commands inside a managed container.

Use hosted shell when:

- you want OCI to provide the runtime
- the workflow can run inside the hosted workspace
- files can be uploaded into a container
- generated artifacts should be retrieved from container files

Two hosted environment modes are common:

1. `container_auto`
   - OCI provisions or reuses a container for the request context.
   - Best first hosted shell shape.

2. `container_reference`
   - Your app creates or chooses a container first.
   - The shell request points at that exact `container_id`.
   - Use this when you need persistence, uploaded files, network policy, memory settings, or attached Skills.

### Local Shell

Local shell means OCI does not run commands.

Instead:

1. The model returns `shell_call` items.
2. Your app inspects and approves the requested commands.
3. Your app runs those commands locally.
4. Your app sends `shell_call_output` back with the same `call_id`.
5. The model continues until it returns a final answer.

Use local shell when the workflow needs:

- a local repository checkout
- private tools
- internal network access
- a developer-controlled runtime
- custom approval, audit, or sandbox rules

## Containers

A container is a stateful hosted execution workspace. Shell Tool and Code Interpreter can use containers to run commands, read files, generate outputs, and preserve state while the container is alive.

Important container create fields:

1. `name`
   - Human-readable container name.
2. `expires_after`
   - Expiration policy, commonly based on `last_active_at`.
3. `file_ids`
   - Existing Files API file IDs copied into the container at creation time.
4. `memory_limit`
   - Runtime memory limit, such as `1g` or `4g`.
5. `network_policy`
   - `disabled` for no outbound network.
   - `allowlist` for approved domains only.
6. `skills`
   - Skills attached when the container is created.

Container file flow:

1. Create or reuse a container.
2. Upload input files with `client.containers.files.create(...)`.
3. Use Shell Tool with `container_reference`.
4. Let the model read inputs and generate artifacts under `/mnt/data`.
5. List files with `client.containers.files.list(...)`.
6. Retrieve content with `client.containers.files.content.retrieve(...)`.

## Skills

A Skill is a reusable folder or bundle with exactly one `SKILL.md` manifest. It can also include:

- `scripts`
- `templates`
- `schemas`
- `examples`
- `references`
- `agents`
- other supporting resources

Skills guide behavior, but they do not replace access control. Shell execution, network access, secrets, and approvals still need to be controlled by the application or platform.

### Local Skills

Local Skills are local folders referenced by name, description, and path.

Shape:

```python
{
    "name": "dev-handoff-kit",
    "description": "Create developer handoff notes.",
    "path": "openai_sdk/skills/samples/dev-handoff-kit",
}
```

Use local Skills with local shell when you want the model to know about reusable workflows in your local repo.

### Inline Skills

Inline Skills are zip bundles encoded as base64 and attached directly to a request or container.

Use inline Skills when:

- cloud Skill upload is unavailable
- the Skill is temporary
- the Skill is generated by your app
- you want a self-contained request shape

### Hosted Skills

Hosted Skills are uploaded to the Skills API and referenced later by `skill_id`.

Hosted Skill upload is useful for shared team Skills, versioning, default versions, and reuse across hosted containers. In this workshop, hosted upload is kept separate because cloud access can vary by tenancy and release timing.

### Curated Skills

Curated Skills are provider-managed Skills. They are referenced like hosted Skills:

```python
{"type": "skill_reference", "skill_id": "openai-spreadsheets"}
```

Availability can vary by provider, model, region, and release.

## How They Bind Together

The common combinations are:

1. Hosted shell with no explicit container
   - Use `container_auto`.
   - Good for quick command execution.

2. Hosted shell with an explicit container
   - Create container first.
   - Use `container_reference`.
   - Good for file workflows and generated artifacts.

3. Hosted shell with container files
   - Upload inputs to the container.
   - Ask Shell Tool to process them.
   - Retrieve generated files.

4. Hosted shell with Skills
   - Attach Skills when the container is created, or attach inline Skills in the shell environment.
   - The model can read `SKILL.md` and supporting files when relevant.

5. Local shell with local Skills
   - Attach local Skill paths.
   - The model requests shell commands.
   - Your app validates and runs them locally.

## Beginner Learning Path

1. Read the basic Responses API flow.
   - Run `uv run openai_sdk/genai_client/base_client.py`.

2. Learn simple built-in tools.
   - Run `uv run openai_sdk/genai_client/web_search.py`.
   - Skim `mcp_client.py` and `code_interpreter.py`.

3. Preview Shell Tool request shapes.
   - Run `uv run openai_sdk/genai_client/shell_tool.py`.
   - Keep `RUN_LIVE_API=False` in the focused files.
   - Then run one focused file at a time:
     - `uv run openai_sdk/genai_client/shell_tools/hosted_container_auto.py`
     - `uv run openai_sdk/genai_client/shell_tools/hosted_container_reference.py`
     - `uv run openai_sdk/genai_client/shell_tools/hosted_network_allowlist.py`
     - `uv run openai_sdk/genai_client/shell_tools/hosted_artifact_generation.py`
     - `uv run openai_sdk/genai_client/shell_tools/local_shell_loop.py`

4. Learn basic container lifecycle.
   - Read `genai_client/containers/readme_containers.md`.
   - Run `base_example.py` only when you are ready to create and delete real containers.

5. Learn container files.
   - Preview `container_files_shell_workflow.py`.
   - Understand upload, shell processing, list, and retrieve.

6. Learn local Skills.
   - Run `uv run openai_sdk/skills/local_skill_usage.py`.
   - Inspect `skills/samples/team-comms-brief`.
   - Inspect `skills/samples/dev-handoff-kit`.

7. Learn inline and curated Skills.
   - Run `uv run openai_sdk/skills/inline_skill_usage.py`.
   - Run `uv run openai_sdk/skills/curated_skill_usage.py`.

8. Connect containers, Shell Tool, and Skills.
   - Preview `container_shell_skills.py`.
   - Notice that Skills attach at container creation time.

9. Try live calls only after access is confirmed.
   - Set `RUN_LIVE_API=True` one script at a time.
   - Keep cleanup flags disabled until you understand what the script creates.
   - Delete test containers intentionally after inspection.

## Safety Checklist

- Keep preview mode on while learning.
- Keep network policy disabled unless the workflow needs approved domains.
- Never commit real API tokens, passwords, or customer data.
- Do not store secrets inside Skill bundles.
- Review generated shell commands before local execution.
- Treat generated files as untrusted until reviewed.
- Prefer small Skills with clear purpose and a short `SKILL.md`.
