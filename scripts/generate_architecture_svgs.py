#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from textwrap import wrap
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images"


PALETTE = {
    "ink": "#162033",
    "muted": "#526070",
    "line": "#334155",
    "bg": "#f6f8fb",
    "panel": "#ffffff",
    "slate": "#e8edf3",
    "blue": "#e4f1ff",
    "teal": "#e1f5ef",
    "amber": "#fff2cf",
    "violet": "#eee8ff",
    "rose": "#ffe7ec",
    "green": "#e9f7df",
    "orange": "#ffe9d2",
}


@dataclass
class Svg:
    name: str
    width: int
    height: int
    title: str
    desc: str
    body: list[str] = field(default_factory=list)

    def add(self, markup: str) -> None:
        self.body.append(markup)

    def text(
        self,
        x: int,
        y: int,
        text: str,
        cls: str = "body",
        max_chars: int | None = None,
        line_height: int = 18,
        anchor: str | None = None,
    ) -> None:
        lines = wrap(text, width=max_chars, break_long_words=False) if max_chars else [text]
        anchor_attr = f' text-anchor="{anchor}"' if anchor else ""
        if len(lines) == 1:
            self.add(f'<text class="{cls}" x="{x}" y="{y}"{anchor_attr}>{escape(lines[0])}</text>')
            return
        tspans = []
        for i, line in enumerate(lines):
            dy = 0 if i == 0 else line_height
            tspans.append(f'<tspan x="{x}" dy="{dy}">{escape(line)}</tspan>')
        self.add(f'<text class="{cls}" x="{x}" y="{y}"{anchor_attr}>{"".join(tspans)}</text>')

    def header(self, subtitle: str | None = None) -> None:
        self.text(48, 58, self.title, "title")
        if subtitle:
            self.text(48, 88, subtitle, "subtitle", max_chars=132, line_height=19)

    def band(self, x: int, y: int, w: int, label: str, fill: str = "#172033") -> None:
        self.add(f'<rect class="band" x="{x}" y="{y}" width="{w}" height="36" fill="{fill}"/>')
        self.text(x + 18, y + 24, label, "bandText")

    def card(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        title: str,
        lines: list[str],
        fill: str = "panel",
        stroke: str = "#64748b",
        title_cls: str = "cardTitle",
    ) -> None:
        self.add(
            f'<rect class="card" x="{x}" y="{y}" width="{w}" height="{h}" '
            f'fill="{PALETTE.get(fill, fill)}" stroke="{stroke}"/>'
        )
        title_max = max(12, int((w - 36) / 9.2))
        title_lines = wrap(title, width=title_max, break_long_words=False) or [title]
        self.text(x + 18, y + 31, title, title_cls, max_chars=title_max, line_height=19)
        cy = y + 58 + (len(title_lines) - 1) * 22
        for line in lines:
            self.text(x + 18, cy, line, "small", max_chars=max(16, int((w - 36) / 7.2)), line_height=16)
            cy += 32 if len(line) > max(16, int((w - 36) / 7.2)) else 20

    def note(self, x: int, y: int, w: int, h: int, text: str, fill: str = "slate", stroke: str = "#94a3b8") -> None:
        self.add(
            f'<rect class="note" x="{x}" y="{y}" width="{w}" height="{h}" '
            f'fill="{PALETTE.get(fill, fill)}" stroke="{stroke}"/>'
        )
        self.text(x + 18, y + 29, text, "smallStrong", max_chars=max(24, int((w - 36) / 7.0)), line_height=18)

    def arrow(self, d: str, cls: str = "arrow", label: str | None = None, lx: int = 0, ly: int = 0) -> None:
        self.add(f'<path class="{cls}" d="{d}"/>')
        if label:
            self.add(f'<rect class="chip" x="{lx - 8}" y="{ly - 17}" width="{len(label) * 7 + 16}" height="23"/>')
            self.text(lx, ly, label, "label")

    def table_row(self, x: int, y: int, widths: list[int], cells: list[str], fill: str = "panel") -> None:
        cx = x
        for i, (w, cell) in enumerate(zip(widths, cells)):
            self.add(f'<rect class="cell" x="{cx}" y="{y}" width="{w}" height="82" fill="{PALETTE.get(fill, fill)}"/>')
            cls = "cellHead" if i == 0 else "cellText"
            self.text(cx + 14, y + 27, cell, cls, max_chars=max(18, int((w - 28) / (8.6 if i == 0 else 7.1))), line_height=16)
            cx += w

    def render(self) -> str:
        style = f"""
  <defs>
    <marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">
      <path d="M2,2 L10,6 L2,10 Z" fill="{PALETTE['line']}"/>
    </marker>
    <style>
      .bg {{ fill: {PALETTE['bg']}; }}
      .title {{ font: 700 34px Inter, Arial, sans-serif; fill: {PALETTE['ink']}; }}
      .subtitle {{ font: 400 16px Inter, Arial, sans-serif; fill: {PALETTE['muted']}; }}
      .band {{ rx: 8; }}
      .bandText {{ font: 700 14px Inter, Arial, sans-serif; fill: #ffffff; letter-spacing: 0; }}
      .card {{ stroke-width: 2; rx: 8; }}
      .note {{ stroke-width: 1.6; rx: 8; }}
      .cardTitle {{ font: 700 18px Inter, Arial, sans-serif; fill: {PALETTE['ink']}; }}
      .body {{ font: 500 15px Inter, Arial, sans-serif; fill: {PALETTE['ink']}; }}
      .small {{ font: 400 13px Inter, Arial, sans-serif; fill: #3a4758; }}
      .smallStrong {{ font: 700 13px Inter, Arial, sans-serif; fill: #253244; }}
      .label {{ font: 700 11px Inter, Arial, sans-serif; fill: #263447; }}
      .chip {{ fill: #ffffff; stroke: #cbd5e1; stroke-width: 1; rx: 7; }}
      .arrow {{ stroke: {PALETTE['line']}; stroke-width: 2.2; fill: none; marker-end: url(#arrow); }}
      .dash {{ stroke: #64748b; stroke-width: 2; stroke-dasharray: 7 7; fill: none; marker-end: url(#arrow); }}
      .soft {{ stroke: #94a3b8; stroke-width: 1.7; fill: none; marker-end: url(#arrow); }}
      .cell {{ stroke: #cbd5e1; stroke-width: 1.4; }}
      .cellHead {{ font: 700 14px Inter, Arial, sans-serif; fill: {PALETTE['ink']}; }}
      .cellText {{ font: 400 12px Inter, Arial, sans-serif; fill: #39485a; }}
    </style>
  </defs>"""
        content = "\n  ".join(self.body)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}" role="img" aria-labelledby="title desc">\n'
            f'  <title id="title">{escape(self.title)}</title>\n'
            f'  <desc id="desc">{escape(self.desc)}</desc>\n'
            f'{style}\n'
            f'  <rect class="bg" width="{self.width}" height="{self.height}"/>\n'
            f'  {content}\n'
            f'</svg>\n'
        )

    def write(self) -> None:
        (OUT / self.name).write_text(self.render())


def simple_flow(name: str, title: str, desc: str, subtitle: str, cards: list[tuple[str, list[str], str]], footer: str) -> Svg:
    svg = Svg(name, 1360, 640, title, desc)
    svg.header(subtitle)
    x0, y, w, h, gap = 48, 160, 180, 132, 32
    for i, (ct, lines, fill) in enumerate(cards):
        x = x0 + i * (w + gap)
        svg.card(x, y, w, h, ct, lines, fill)
        if i:
            px = x0 + (i - 1) * (w + gap) + w
            svg.arrow(f"M{px} {y + h // 2} L{x} {y + h // 2}")
    svg.note(48, 360, 1264, 76, footer)
    return svg


def stack_overview() -> Svg:
    s = Svg(
        "ao-stack-overview.svg",
        1600,
        1080,
        "AO agent orchestration stack",
        "Current AO architecture with Mission intake, Blueprint authorization, Atlas workgraph compilation, Foundry scheduling, Forge planning, Covenant gates, AO2 execution, read-only observers, and assurance gates.",
    )
    s.header("Mission records intent; Blueprint and Atlas shape work; Foundry, Forge, Covenant, and AO2 run governed work; Command and control-plane only read back evidence.")
    s.band(48, 124, 1504, "Repository authority map")
    positions = {
        "AO Mission": (64, 190, "teal", ["User entry, route decision", "Gateway and recovery readbacks", "No execution or approval"]),
        "AO Blueprint": (414, 190, "amber", ["Requirements interview", "Blueprint pack", "Build authorization"]),
        "AO Atlas": (764, 190, "blue", ["Stack-instance compiler", "Workgraphs and context packs", "Foundry import material"]),
        "AO Foundry": (1114, 190, "orange", ["Portfolio scheduler", "Readiness and PR lifecycle", "One ready node at a time"]),
        "AO Forge": (414, 445, "violet", ["One governed GoalRun", "Factory plan and packets", "Retained evidence"]),
        "AO Covenant": (764, 445, "amber", ["Policy and trust kernel", "Approval tickets", "Claim vocabulary"]),
        "AO2": (1114, 445, "blue", ["Bounded local execution", "Adapters and artifacts", "Evaluator closure"]),
        "ao2-control-plane": (414, 700, "green", ["Read-only observer", "Signed ingest", "Dashboards and APIs"]),
        "AO Command": (764, 700, "teal", ["Read-only operator view", "Status and next actions", "Validation without mutation"]),
        "Assurance gates": (1114, 700, "rose", ["Arena scores", "Crucible probes", "Sentinel holds, Promoter dry-runs"]),
    }
    for title, (x, y, fill, lines) in positions.items():
        s.card(x, y, 280, 150, title, lines, fill)
    s.arrow("M344 265 L406 265")
    s.arrow("M694 265 L756 265")
    s.arrow("M1044 265 L1106 265")
    s.arrow("M1254 340 C1254 398 574 390 554 437")
    s.arrow("M694 520 L756 520")
    s.arrow("M1044 520 L1106 520")
    s.arrow("M1254 595 C1254 656 574 646 554 692", cls="dash")
    s.arrow("M694 775 L756 775", cls="dash")
    s.arrow("M1044 775 L1106 775", cls="dash")
    s.note(64, 930, 1392, 82, "Invariant: Atlas does not schedule, execute, approve, publish, call providers, or mutate sibling repositories. Command and control-plane report evidence only; they do not approve or execute work.")
    return s


def mission_pipeline() -> Svg:
    s = Svg(
        "ao-mission-pipeline.svg",
        1500,
        780,
        "AO Mission pipeline",
        "AO Mission accepts operator and gateway intent, emits route-decision and governance readback, then routes through Blueprint, Atlas, Foundry, Forge, AO2, assurance gates, and read-only Command status.",
    )
    s.header("Intent and readback stay separate from execution authority.")
    s.band(48, 120, 1404, "Mission-led route and governance path")
    cards = [
        ("User and gateways", ["CLI, Telegram, A2A", "Intent/readback only"], "teal"),
        ("AO Mission", ["Mission record", "Route decision", "Governance snapshot"], "teal"),
        ("Blueprint", ["Requirements", "Build authorization"], "amber"),
        ("Atlas", ["Workgraph metadata", "Context packs"], "blue"),
        ("Foundry", ["PR lifecycle", "Smoke and readiness ledger"], "orange"),
        ("Forge / AO2", ["Bounded runs", "Policy packet", "Evidence export"], "violet"),
    ]
    x, y = 64, 178
    for i, (title, lines, fill) in enumerate(cards):
        cx = x + i * 232
        s.card(cx, y, 190, 140, title, lines, fill)
        if i:
            s.arrow(f"M{cx - 42} 248 L{cx - 8} 248")
    s.band(48, 398, 1404, "Readback, gates, and denied authority")
    s.card(92, 476, 300, 132, "Assurance gates", ["Covenant policy", "Arena, Crucible, Sentinel", "Promoter dry-run activation"], "rose")
    s.card(600, 476, 300, 132, "AO Command", ["Read-only status", "Next action display", "No scheduling or mutation"], "teal")
    s.card(1010, 476, 300, 132, "Denied authority remains denied", ["No direct main", "No credentials or deploy", "No hidden mutation"], "slate")
    s.arrow("M1319 318 V360 H1360 V456 H242 V468", cls="dash")
    s.arrow("M392 542 L592 542", cls="dash")
    s.arrow("M900 542 L1002 542", cls="dash")
    return s


def gateway_map() -> Svg:
    s = Svg(
        "ao-mission-gateway-authority-map.svg",
        1280,
        760,
        "AO Mission gateway authority map",
        "Gateway, scheduler, archive, and readiness surfaces feed Mission readback and downstream provenance without granting execution, approval, provider, credential, release, or repository mutation authority.",
    )
    s.header("Gateway convenience is not work authority.")
    s.band(48, 116, 1184, "Gateway and recovery inputs")
    inputs = [
        ("Telegram", ["Allowlisted operator intent", "Freshness readback"], "teal"),
        ("A2A", ["Agent Card fixture", "Status and artifact refs"], "blue"),
        ("codex-cron", ["Wakeup substrate", "No mission brain"], "slate"),
        ("Archive", ["Digest-bound provenance", "Validation readback"], "green"),
    ]
    for i, item in enumerate(inputs):
        s.card(64 + i * 300, 176, 236, 120, item[0], item[1], item[2])
        s.arrow(f"M{182 + i * 300} 296 C{182 + i * 300} 328 640 318 640 354", cls="soft")
    s.card(520, 354, 240, 146, "AO Mission", ["Mission record", "Route decision", "Gateway readiness rollup", "Timeline compaction"], "teal")
    chain = [
        ("Blueprint", ["Authorization"], "amber"),
        ("Atlas", ["Workgraph compiler"], "blue"),
        ("Foundry", ["Implementation gates"], "orange"),
        ("Forge / AO2", ["Bounded execution"], "violet"),
    ]
    for i, item in enumerate(chain):
        s.card(64 + i * 300, 570, 236, 118, item[0], item[1], item[2])
        if i == 0:
            s.arrow("M640 500 C640 548 182 535 182 570", label="route", lx=485, ly=535)
        else:
            s.arrow(f"M{64 + (i - 1) * 300 + 236} 629 L{64 + i * 300} 629")
    s.card(980, 354, 236, 146, "Covenant / Sentinel / Command", ["Denial contracts", "Public-risk guard", "Compact readback"], "rose")
    s.arrow("M760 427 L980 427", cls="dash", label="authority checks", lx=805, ly=412)
    s.note(64, 704, 1152, 38, "Denied at gateway: execution, approval, provider calls, release, credentials, direct mutation, direct-main mutation, and authority widening.")
    return s


def live_mutation_boundary() -> Svg:
    s = Svg(
        "live-mutation-boundary.svg",
        1440,
        980,
        "Authority-request dry-run boundary",
        "Shows the current public-safe unrestricted self-modification authority-request dry-run class, while keeping unrestricted self-modification, sandbox bypass, real sandbox escape, provider calls, credentials, release, direct-main mutation, concurrent mutation, and broad public claims denied.",
    )
    s.header("Current highest proven class is a no-execution authority-request dry-run; it is not unrestricted self-modification authority.")
    s.band(48, 120, 1344, "Request packet and denial evidence")
    top = [
        ("Authority-request packet", ["Exact-scope reversible request", "No execution permission"], "blue"),
        ("Covenant denial ticket", ["Denies unrestricted self-modification", "Binds denied surfaces"], "amber"),
        ("Sentinel hold", ["Public-risk and kill-switch trace", "No unsafe activation"], "rose"),
        ("Command / Promoter readback", ["No-execution status", "Dry-run promotion evidence"], "teal"),
    ]
    for i, item in enumerate(top):
        x = 74 + i * 335
        s.card(x, 188, 270, 142, item[0], item[1], item[2])
        if i:
            s.arrow(f"M{x - 65} 259 L{x} 259")
    s.band(48, 398, 1344, "Governed stack path")
    path = [
        ("Mission", ["Records objective and route", "Readback only"], "teal"),
        ("Blueprint / Atlas", ["Authorization and workgraph", "No execution grant"], "blue"),
        ("Foundry / Forge", ["Approval request and guard", "Bounded packet only"], "orange"),
        ("AO2", ["Dry-run evidence bundle", "No unrestricted mutation"], "violet"),
    ]
    for i, item in enumerate(path):
        x = 74 + i * 335
        s.card(x, 466, 270, 142, item[0], item[1], item[2])
        if i:
            s.arrow(f"M{x - 65} 537 L{x} 537")
    s.band(48, 676, 1344, "Claim boundary")
    s.card(74, 744, 270, 142, "Proven", ["Public-safe authority-request dry-run", "Four exact-scope reversible attempts"], "green")
    s.card(409, 744, 270, 142, "Still denied", ["Unrestricted self-modification", "Sandbox containment bypass", "Real sandbox escape"], "rose")
    s.card(744, 744, 270, 142, "Still denied", ["Provider calls and credentials", "Release, deploy, publish, upload, tags", "Dependency updates"], "rose")
    s.card(1079, 744, 270, 142, "Still denied", ["Direct-main and concurrent mutation", "Hidden instruction mutation", "Broad public claims"], "rose")
    s.note(74, 910, 1275, 42, "Readback can explain the dry-run decision. It cannot approve, execute, publish, mutate repositories, widen authority, or convert denied surfaces into allowed ones.")
    return s


def authority_boundaries() -> Svg:
    s = Svg(
        "authority-boundaries.svg",
        1480,
        1120,
        "Authority boundaries keep the factory auditable",
        "Repository ownership table showing what each AO repository owns and must not own.",
    )
    s.header("No repository writes its own permission slip.")
    widths = [205, 555, 625]
    x, y = 48, 130
    s.add(f'<rect class="cell" x="{x}" y="{y}" width="{sum(widths)}" height="42" fill="#172033"/>')
    s.text(x + 14, y + 27, "Repository", "bandText")
    s.text(x + widths[0] + 14, y + 27, "Owns", "bandText")
    s.text(x + widths[0] + widths[1] + 14, y + 27, "Must not own", "bandText")
    rows = [
        ("AO Mission", "Mission records, gateway intents, route decisions, governance snapshots, archive/recovery/compaction readbacks", "Execution, approval, provider calls, repository mutation, authority widening"),
        ("AO Blueprint", "Requirements interview, blueprint pack, sufficiency audit, build authorization", "Scheduling, execution, policy approval, provider calls, self-approving self-change"),
        ("AO Atlas", "Stack instances, workgraphs, context packs, Foundry handoff, run-link readback", "Scheduling, execution, approval, publication, providers, sibling repository mutation"),
        ("AO Foundry", "Portfolio queue, active-stack readiness, release trains, one-slice PR lifecycle", "Individual governed execution or side-effect approval"),
        ("AO Forge", "One governed factory run, GoalRun state, plans, gates, retained evidence", "Provider execution, final policy authority, observer dashboard storage"),
        ("AO Covenant", "Policy, trust, approval tickets, side-effect gates, claim vocabulary", "Whole-factory scheduling, all evidence storage, operator dashboard UX"),
        ("AO2", "Governed local execution, adapters, exact-digest approvals, evaluator closure", "Cross-repository scheduling, release promotion policy, observer storage"),
        ("Control plane", "Signed ingest, content-addressed storage, read APIs, dashboards", "Approving AO2 runs, executing providers, deciding release readiness"),
        ("AO Command", "Read-only status, stack summaries, evidence validation, next-action display", "Policy replacement, provider execution, release mutation, repository mutation"),
        ("Assurance", "Arena scores, Crucible probes, Sentinel holds, Promoter dry-run activation", "Overriding Covenant policy, bypassing AO2, publishing without promotion gates"),
    ]
    cy = y + 42
    for i, row in enumerate(rows):
        s.table_row(x, cy, widths, list(row), fill="panel" if i % 2 == 0 else "slate")
        cy += 82
    s.note(48, 1018, 1385, 52, "Rule: readback surfaces report evidence; they do not approve, execute, mutate, call providers, publish, or widen denied authority.")
    return s


def evidence_flow() -> Svg:
    s = Svg(
        "evidence-flow.svg",
        1440,
        840,
        "Evidence-first orchestration workflow",
        "Shows execution and evidence lanes from intent through Blueprint, Atlas, Foundry, Forge, Covenant, AO2, control-plane readback, Command status, and assurance gates.",
    )
    s.header("Every meaningful decision leaves a durable, schema-backed record.")
    s.band(48, 118, 1344, "Execution lane: scope must be authorized and gated before side effects")
    exec_cards = [
        ("Intent", ["Operator goal"], "teal"),
        ("Blueprint", ["Authorization"], "amber"),
        ("Atlas", ["Workgraph pack"], "blue"),
        ("Foundry", ["Schedule next"], "orange"),
        ("Forge", ["GoalRun plan"], "violet"),
        ("Covenant", ["Policy decision"], "amber"),
        ("AO2", ["Governed run"], "blue"),
    ]
    for i, item in enumerate(exec_cards):
        x = 64 + i * 194
        s.card(x, 184, 164, 108, item[0], item[1], item[2])
        if i:
            s.arrow(f"M{x - 30} 238 L{x} 238")
    s.band(48, 354, 1344, "Evidence lane: decisions are exported, retained, and read back")
    ev = [
        ("Pack", ["Events and digests"], "green"),
        ("Control-plane", ["Read-only ingest"], "green"),
        ("Command", ["Operator status"], "teal"),
        ("Arena", ["Benchmark score"], "slate"),
        ("Crucible", ["Hardening evidence"], "slate"),
        ("Sentinel", ["Regression verdict"], "rose"),
        ("Promoter", ["Gated activation plan"], "orange"),
    ]
    for i, item in enumerate(ev):
        x = 64 + i * 194
        s.card(x, 420, 164, 108, item[0], item[1], item[2])
        if i:
            s.arrow(f"M{x - 30} 474 L{x} 474", cls="dash")
    s.arrow("M1310 292 V326 H32 V474 H64", cls="dash", label="evidence export", lx=1010, ly=318)
    s.note(64, 612, 1312, 92, "Publication boundary: full autonomous RSI claims remain denied unless separate Covenant-approved mutation authority, rollback evidence, live self-change evidence, observer readback, public-safety review, and promotion evidence exist.")
    return s


def repo_specific() -> list[Svg]:
    diagrams: list[Svg] = []
    diagrams.append(simple_flow(
        "ao-arena-scoreboard.svg",
        "AO Arena deterministic scoreboard",
        "AO Arena converts fixture benchmark evidence into deterministic scorecards and promotion-gate input.",
        "Fixture evidence becomes promotion-grade scores.",
        [
            ("Benchmark suite", ["Canonical tasks", "Stable fixtures"], "blue"),
            ("Competitors", ["Baseline and challenger"], "slate"),
            ("Fixture attempts", ["Evidence bundles only"], "green"),
            ("Scorecards", ["100-point deterministic math"], "amber"),
            ("Comparison report", ["Winner, evidence, safety"], "violet"),
            ("Promotion gate", ["Score >= 85", "Improvement >= 5"], "orange"),
        ],
        "Arena does not promote candidates by itself; it supplies benchmark evidence to the gated promotion chain.",
    ))
    diagrams.append(simple_flow(
        "ao-crucible-hardening.svg",
        "AO Crucible adversarial hardening",
        "AO Crucible probes candidates with controlled adversarial fixtures before promotion.",
        "Trust candidates only after controlled failure probes.",
        [
            ("Subject", ["AO orchestration candidate"], "slate"),
            ("Probe catalog", ["Injection", "Spoofing", "Stale proof"], "rose"),
            ("Fixture run", ["Controlled scenarios"], "blue"),
            ("Assessment", ["Resilience score", "Risk notes"], "amber"),
            ("Hardening gate", ["Pass or remediation brief"], "green"),
        ],
        "Crucible supplies hardening evidence that Promoter must consume; it does not activate candidates.",
    ))
    diagrams.append(simple_flow(
        "ao-sentinel-regression-monitor.svg",
        "AO Sentinel safety and regression monitor",
        "AO Sentinel evaluates public-safety and regression signals and emits clear, incident, or hold verdicts.",
        "Watch safety and regressions before promotion.",
        [
            ("Target", ["Candidate or active stack"], "slate"),
            ("Baseline", ["Trusted regression budgets"], "green"),
            ("Safety scan", ["Public artifact checks"], "rose"),
            ("Regression diff", ["Current vs baseline"], "blue"),
            ("Verdict", ["Clear, incident, or hold"], "amber"),
            ("Promoter hold", ["Blocks unsafe activation"], "rose"),
        ],
        "Sentinel is a non-mutating guardrail. Holds require repair evidence before promotion can continue.",
    ))
    diagrams.append(simple_flow(
        "ao-promoter-gated-promotion.svg",
        "AO Promoter gated promotion",
        "AO Promoter turns passing evidence into a dry-run activation and rollback plan only after all gates are satisfied.",
        "Activation only after every gate has evidence.",
        [
            ("Arena gate", ["Benchmark win"], "blue"),
            ("Crucible gate", ["Hardening passed"], "rose"),
            ("Sentinel verdict", ["Clear, no hold"], "green"),
            ("Policy and run proof", ["Covenant", "Forge", "AO2"], "amber"),
            ("Promotion packet", ["Candidate", "Evidence refs"], "violet"),
            ("Apply dry-run", ["No default live mutation"], "orange"),
        ],
        "Promoter does not override Covenant policy, bypass AO2, or publish without rollback and readback evidence.",
    ))
    diagrams.append(simple_flow(
        "ao-forge-factory-loop.svg",
        "AO Forge factory loop",
        "AO Forge owns one governed GoalRun and coordinates plans, gates, AO2 delegation, evidence, and operator packets.",
        "Trusted factory brain for one governed run.",
        [
            ("GoalRun", ["Durable objective", "Phase and next action"], "violet"),
            ("Factory plan", ["Exact step and constraints"], "blue"),
            ("Covenant gate", ["Policy and approvals"], "amber"),
            ("AO2 run", ["Bounded execution"], "teal"),
            ("Evidence", ["Artifacts and closure"], "green"),
            ("Operator packet", ["Readback and blockers"], "slate"),
        ],
        "Forge decides the next governed factory step, but provider execution and final policy authority remain outside Forge.",
    ))
    diagrams.append(simple_flow(
        "ao2-governed-runtime.svg",
        "AO2 governed runtime",
        "AO2 executes bounded local workflows through replaceable adapters while preserving approvals, artifacts, replay, evaluator closure, and evidence export.",
        "Adapters are clients; AO2 owns run state and evidence closure.",
        [
            ("Workflow", ["Compile run context"], "blue"),
            ("Policy gate", ["Exact-digest approval"], "amber"),
            ("Adapter", ["Scripted, Codex, Claude"], "teal"),
            ("Artifacts", ["Digests and lineage"], "green"),
            ("Reviewer", ["Concerns and evidence"], "violet"),
            ("Evaluator", ["Accepts or rejects"], "rose"),
        ],
        "AO2 does not schedule cross-repository work or decide release promotion policy.",
    ))
    diagrams.append(simple_flow(
        "ao2-control-plane-observer.svg",
        "ao2-control-plane observer architecture",
        "ao2-control-plane stores and exposes signed AO2 evidence after the fact through read-only observer surfaces.",
        "Read-only evidence observer.",
        [
            ("AO2 CLI", ["Signed evidence bundles"], "blue"),
            ("Ingest API", ["Token and signature checks"], "teal"),
            ("Storage", ["Content-addressed files"], "green"),
            ("Read APIs", ["Authenticated views"], "slate"),
            ("Dashboards", ["Operator readback"], "violet"),
            ("Runbooks", ["Backup, restore, rotation"], "amber"),
        ],
        "Observer invariant: the server never approves AO2 runs, executes providers, or decides release readiness.",
    ))
    diagrams.append(simple_flow(
        "ao-covenant-policy-kernel.svg",
        "AO Covenant policy kernel",
        "AO Covenant checks side effects, approval tickets, contracts, release bundles, claims, and closure obligations before trust is granted.",
        "Contract-bound trust kernel.",
        [
            ("Brief", ["Human intent"], "teal"),
            ("Contract", ["Schema and digest"], "blue"),
            ("Policy", ["Allow, deny, require approval"], "amber"),
            ("Approval", ["Exact action digest"], "orange"),
            ("Closure", ["Obligation matrix"], "violet"),
            ("Evidence", ["Pack and bundle"], "green"),
        ],
        "Rule: side effects are declared and policy-checked before execution; closure must map to durable evidence.",
    ))
    diagrams.append(simple_flow(
        "ao-command-readonly.svg",
        "AO Command read-only command center",
        "AO Command reads, validates, and summarizes stack evidence without scheduling, approving, executing, publishing, or mutating repositories.",
        "Read-only operator status across the active stack.",
        [
            ("Command", ["operator_mode=read_only", "Status and next actions"], "teal"),
            ("Blueprint / Atlas", ["Authorization", "Compile/readback evidence"], "blue"),
            ("Foundry / Forge", ["Active-stack ledger", "GoalRun evidence"], "orange"),
            ("Covenant / AO2", ["Policy decisions", "Execution summaries"], "amber"),
            ("Control plane", ["Observer readback"], "green"),
            ("Assurance", ["Arena, Crucible", "Sentinel, Promoter"], "rose"),
        ],
        "AO Command validates and displays evidence. It does not schedule, execute, approve claims, call providers, publish releases, apply activation plans, or mutate repositories.",
    ))
    return diagrams


def foundry_portfolio() -> Svg:
    s = Svg(
        "ao-foundry-portfolio-loop.svg",
        1280,
        800,
        "AO Foundry active-stack portfolio loop",
        "AO Foundry coordinates the current 13-repository active stack with registry validation, readiness gates, PR lifecycle evidence, Forge delegation, and stop conditions.",
    )
    s.header("Foundry schedules and coordinates; it does not execute or approve policy.")
    s.band(48, 118, 1184, "Portfolio control loop")
    nodes = [
        ("Blueprint", ["Build authorization"], "amber"),
        ("Atlas", ["Workgraph and context packs"], "blue"),
        ("Foundry", ["Registry, intake/start gates", "PR lifecycle"], "orange"),
        ("Repo registry", ["13 active repositories"], "green"),
        ("Readiness", ["Evidence and CI runs"], "slate"),
        ("Forge", ["One governed factory run"], "violet"),
        ("Release handoff", ["Manual promotion gate"], "rose"),
        ("Stop condition", ["No blocking readiness tasks", "No open PRs"], "teal"),
    ]
    coords = [(72, 186), (376, 186), (680, 186), (984, 186), (984, 432), (680, 432), (376, 432), (72, 432)]
    for (title, lines, fill), (x, y) in zip(nodes, coords):
        s.card(x, y, 224, 126, title, lines, fill)
    for a, b in zip(coords, coords[1:]):
        ax, ay = a
        bx, by = b
        if ay == by:
            if bx > ax:
                s.arrow(f"M{ax + 224} {ay + 63} L{bx} {by + 63}")
            else:
                s.arrow(f"M{ax} {ay + 63} L{bx + 224} {by + 63}")
        elif bx == ax:
            s.arrow(f"M{ax + 112} {ay + 126} L{bx + 112} {by}")
        else:
            s.arrow(f"M{ax + 112} {ay + 126} C{ax + 112} {ay + 178} {bx + 112} {by - 52} {bx + 112} {by}")
    s.arrow("M72 495 C20 495 20 249 72 249", cls="dash", label="next slice", lx=28, ly=376)
    s.note(72, 668, 1136, 66, "Foundry does not execute providers, approve policy, publish releases, call providers, or treat raw ideas as ready implementation work.")
    return s


def main() -> int:
    OUT.mkdir(exist_ok=True)
    diagrams = [
        stack_overview(),
        mission_pipeline(),
        gateway_map(),
        live_mutation_boundary(),
        authority_boundaries(),
        evidence_flow(),
        foundry_portfolio(),
    ]
    diagrams.extend(repo_specific())
    for diagram in diagrams:
        diagram.write()
        print(f"wrote images/{diagram.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
