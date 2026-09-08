import assert from "node:assert/strict"

const THRESHOLD = 10

function canonicalize(value) {
  if (value === undefined) return "undefined"
  if (value === null || typeof value !== "object") return JSON.stringify(value)
  if (Array.isArray(value)) return `[${value.map(canonicalize).join(",")}]`
  return `{${Object.entries(value)
    .filter(([, v]) => v !== undefined)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([k, v]) => `${JSON.stringify(k)}:${canonicalize(v)}`)
    .join(",")}}`
}

function signature(call) {
  return `${call.name}:${canonicalize(call.input)}`
}

function run(policy, turns, { cancelAt } = {}) {
  const state = {
    session: "busy",
    lastSignature: undefined,
    count: 0,
    reassessmentIssued: false,
    providerTurns: 0,
    assistantMessages: 0,
    toolExecutions: 0,
    toolParts: [],
    events: [],
    text: [],
    terminal: undefined,
  }
  for (let index = 0; index < turns.length; index++) {
    if (cancelAt === index) {
      state.events.push({ type: "cancel" })
      state.session = "idle"
      state.terminal = "cancelled"
      break
    }
    const turn = turns[index]
    if (turn.kind === "reassessment") {
      if (policy !== "target" || !state.reassessmentIssued) throw new Error("unexpected reassessment turn")
      state.providerTurns++
      state.assistantMessages++
      state.events.push({ type: "reassessment-requested", tools: [] })
      if (turn.attemptTool) {
        state.events.push({ type: "reassessment-tool-suppressed", tool: turn.attemptTool.name })
        state.events.push({ type: "error", ref: "reassessment-tool-request" })
        state.session = "idle"
        state.terminal = "error"
        break
      }
      state.text.push(turn.text)
      state.events.push({ type: "reassessment-completed", category: turn.category })
      state.session = "idle"
      state.terminal = turn.category === "unhelpful" ? "error" : "normal"
      break
    }
    state.providerTurns++
    state.assistantMessages++
    if (turn.kind === "text") {
      state.text.push(turn.text)
      state.session = "idle"
      state.terminal = "normal"
      break
    }
    if (turn.kind !== "tool") throw new Error(`unsupported turn ${turn.kind}`)
    const part = { tool: turn.name, input: turn.input, output: turn.output, status: "completed" }
    state.toolParts.push(part)
    state.toolExecutions++
    const current = signature(turn)
    state.count = current === state.lastSignature ? state.count + 1 : 1
    state.lastSignature = current
    if (state.count !== THRESHOLD) continue
    state.events.push({ type: "continuation-threshold", ref: "repeated-identical-tool-call", count: THRESHOLD, tool: turn.name })
    if (policy === "baseline") {
      state.events.push({ type: "error", ref: "repeated-identical-tool-call" })
      state.session = "idle"
      state.terminal = "error"
      break
    }
    state.reassessmentIssued = true
    // The policy removes automatic tools before the only subsequent provider request.
    continue
  }
  return state
}

function calls(count, input = { pattern: "**/*.txt" }, output = "same") {
  return Array.from({ length: count }, () => ({ kind: "tool", name: "glob", input, output }))
}

const fixtures = {
  normal: [...calls(1), { kind: "text", text: "done" }],
  alternating: [
    { kind: "tool", name: "glob", input: { pattern: "x" }, output: "x" },
    { kind: "tool", name: "glob", input: { pattern: "y" }, output: "y" },
    { kind: "tool", name: "glob", input: { pattern: "x" }, output: "x" },
    { kind: "tool", name: "glob", input: { pattern: "y" }, output: "y" },
    { kind: "text", text: "done" },
  ],
  changing: [...calls(12).map((turn, n) => ({ ...turn, input: { pattern: `p${n}` }, output: `p${n}` })), { kind: "text", text: "done" }],
  nine: [...calls(9), { kind: "text", text: "done" }],
  baselineTenEleven: [...calls(11), { kind: "text", text: "unconsumed" }],
  targetUseful: [...calls(10), { kind: "reassessment", category: "useful", text: "Automatic checks were bounded after 10 identical results. Deployment remains pending; please provide a deployment event or confirm whether to continue polling." }, { kind: "tool", name: "glob", input: { pattern: "**/*.txt" }, output: "unconsumed" }],
  targetUnhelpful: [...calls(10), { kind: "reassessment", category: "unhelpful", text: "I appear to be stuck." }],
  targetAdversarial: [...calls(10), { kind: "reassessment", attemptTool: { name: "glob", input: { pattern: "**/*.txt" } } }],
  polling: [...calls(10).map((turn, n) => ({ ...turn, name: "check_deployment", input: {}, output: `pending ${n + 1}` })), { kind: "reassessment", category: "useful", text: "Deployment is still pending after bounded automatic polling. Please confirm whether to wait or inspect deployment logs." }],
  changingOutput: [...calls(10).map((turn, n) => ({ ...turn, name: "status", input: {}, output: `pending ${10 + n * 10}%` })), { kind: "reassessment", category: "useful", text: "Status changed but automatic identical calls reached the fixed boundary; please continue manually." }],
  cancellation: [...calls(5), { kind: "text", text: "not reached" }],
}

const results = {
  metadata: {
    threshold: THRESHOLD,
    harness: "disposable counterfactual model of SessionPrompt assistant-message turns, completed tool parts, SessionStatus, events, and tool suppression; it is not an upstream integration test",
  },
  baseline: {},
  target: {},
}
for (const name of ["normal", "alternating", "changing", "nine", "baselineTenEleven", "polling", "changingOutput"]) results.baseline[name] = run("baseline", fixtures[name])
for (const name of ["normal", "alternating", "changing", "nine", "targetUseful", "targetUnhelpful", "targetAdversarial", "polling", "changingOutput"]) results.target[name] = run("target", fixtures[name])
results.baseline.cancellation = run("baseline", fixtures.cancellation, { cancelAt: 3 })
results.target.cancellation = run("target", fixtures.cancellation, { cancelAt: 3 })

for (const policy of ["baseline", "target"]) {
  for (const name of ["normal", "alternating", "changing", "nine"]) {
    assert.equal(results[policy][name].terminal, "normal", `${policy}/${name}`)
    assert.equal(results[policy][name].session, "idle", `${policy}/${name} idle`)
  }
}
assert.equal(results.baseline.nine.toolExecutions, 9)
assert.equal(results.target.nine.toolExecutions, 9)
assert.equal(results.baseline.baselineTenEleven.toolExecutions, 10)
assert.equal(results.baseline.baselineTenEleven.providerTurns, 10)
assert.equal(results.baseline.baselineTenEleven.terminal, "error")
assert.equal(results.target.targetUseful.toolExecutions, 10)
assert.equal(results.target.targetUseful.providerTurns, 11)
assert.equal(results.target.targetUseful.terminal, "normal")
assert.equal(results.target.targetAdversarial.toolExecutions, 10)
assert.equal(results.target.targetAdversarial.terminal, "error")
assert.equal(results.target.targetAdversarial.events.some((x) => x.type === "reassessment-tool-suppressed"), true)
assert.equal(results.baseline.polling.terminal, "error")
assert.equal(results.target.polling.terminal, "normal")
assert.equal(results.baseline.changingOutput.toolExecutions, 10)
assert.equal(results.target.changingOutput.toolExecutions, 10)
assert.equal(results.baseline.cancellation.terminal, "cancelled")
assert.equal(results.target.cancellation.terminal, "cancelled")

console.log(JSON.stringify(results, null, 2))
