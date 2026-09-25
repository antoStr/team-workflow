// team-workflow for OpenCode (written by install_opencode.py; edits here are overwritten).
// - the project memory, the settings and the OpenCode notes go into the system prompt, once per
//   session (what the SessionStart hook does in Claude Code);
// - /team-workflow:settings, agents, profile, models, addons, audit, doctor, ci-init and
//   update-plugin are answered by tw.py without the model: no tokens;
// - when a turn ends with files changed after docs/memory/STATE.md, it asks for the memory
//   update once (what the Stop hook does in Claude Code).
const SCRIPTS = "__SCRIPTS__";
const NO_MODEL = {
  "update-plugin": "update", settings: "settings", models: "models", addons: "addons",
  agents: "agents", profile: "profile", audit: "audit", doctor: "doctor", "ci-init": "ci-init",
};

function words(text) {
  return (text.match(/"[^"]*"|'[^']*'|\S+/g) || []).map((w) => w.replace(/^["']|["']$/g, ""));
}

export const TeamWorkflow = async ({ client, directory }) => {
  const context = new Map(); // sessionID -> text for the system prompt
  const child = new Map(); // sessionID -> true for subagent sessions

  async function python(script, args = [], stdin = "") {
    const proc = Bun.spawn(["python3", `${SCRIPTS}/${script}`, ...args], {
      cwd: directory, stdin: new Blob([stdin]), stdout: "pipe", stderr: "pipe",
      env: { ...process.env, TEAM_WORKFLOW_APP: "opencode" },
    });
    const [out, err] = await Promise.all([new Response(proc.stdout).text(), new Response(proc.stderr).text()]);
    await proc.exited;
    return (out + err).trim();
  }

  async function isChild(sessionID) {
    if (!child.has(sessionID)) {
      try {
        const res = await client.session.get({ path: { id: sessionID } });
        child.set(sessionID, Boolean(res.data?.parentID));
      } catch {
        child.set(sessionID, false);
      }
    }
    return child.get(sessionID);
  }

  async function toast(message) {
    try {
      await client.tui.showToast({ body: { message, variant: "info", duration: 8000 } });
    } catch {}
  }

  return {
    "experimental.chat.system.transform": async (input, output) => {
      const id = input.sessionID;
      if (!id || (await isChild(id))) return; // subagents get their own role prompt only
      if (!context.has(id)) {
        let text = "";
        try {
          const data = JSON.parse(await python("session_start.py", [], JSON.stringify({ cwd: directory, session_id: id })));
          text = data.hookSpecificOutput?.additionalContext || "";
          if (data.systemMessage) await toast(data.systemMessage);
        } catch {}
        context.set(id, text);
      }
      if (context.get(id)) output.system.push(context.get(id));
    },

    "command.execute.before": async (input) => {
      const m = /^team-workflow:([\w-]+)$/.exec(input.command || "");
      if (!m || !NO_MODEL[m[1]]) return;
      const out = await python("tw.py", [NO_MODEL[m[1]], ...words(input.arguments || "")]);
      await client.session.prompt({
        path: { id: input.sessionID },
        body: { noReply: true, parts: [{ type: "text", text: out || "(no output)" }] },
      });
      throw new Error("team-workflow: answered without the model");
    },

    event: async ({ event }) => {
      if (event.type !== "session.idle") return;
      const id = event.properties?.sessionID;
      if (!id || (await isChild(id))) return;
      try {
        const out = await python("stop_check.py", [], JSON.stringify({ cwd: directory, session_id: id }));
        const data = out ? JSON.parse(out) : {};
        if (data.decision === "block" && data.reason) {
          await client.session.prompt({ path: { id }, body: { parts: [{ type: "text", text: data.reason }] } });
        }
      } catch {}
    },
  };
};
