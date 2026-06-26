"""
Kanban Board — Visual task tracking for the GSD Workflow Engine.

The KanbanBoard manages individual task cards that auto-transition
status based on workflow phase changes. It provides:

1. Card management (add, update, query)
2. Auto-transition on phase advance/rollback
3. HTML rendering for the daemon's HTTP dashboard

Card lifecycle:
    backlog → in_progress → review → done
                 ↑                      |
                 └── blocked (on rollback) ←┘

Auto-transition rules (mapped to GSD phases):
    research/architecture/ux_design/plan → cards stay in backlog
    execute → all backlog cards move to in_progress
    ux_review/test/verify → all in_progress cards move to review
    deploy → all review cards move to done
    rollback → affected cards move back to in_progress or blocked
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict
from typing import Optional
import html
import json


# ---------------------------------------------------------------------------
# Card status constants
# ---------------------------------------------------------------------------

STATUS_BACKLOG = "backlog"
STATUS_IN_PROGRESS = "in_progress"
STATUS_REVIEW = "review"
STATUS_DONE = "done"
STATUS_BLOCKED = "blocked"

ALL_STATUSES = [STATUS_BACKLOG, STATUS_IN_PROGRESS, STATUS_REVIEW, STATUS_DONE, STATUS_BLOCKED]

# Phases that trigger each status transition
PHASE_STATUS_MAP = {
    "research": STATUS_BACKLOG,
    "architecture": STATUS_BACKLOG,
    "ux_design": STATUS_BACKLOG,
    "plan": STATUS_BACKLOG,
    "execute": STATUS_IN_PROGRESS,
    "ux_review": STATUS_REVIEW,
    "test": STATUS_REVIEW,
    "verify": STATUS_REVIEW,
    "deploy": STATUS_DONE,
    "done": STATUS_DONE,
}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class KanbanCard:
    """A single task card on the Kanban board."""
    id: str
    title: str
    status: str = STATUS_BACKLOG
    phase_created: str = ""
    phase_completed: Optional[str] = None
    assignee: str = ""  # model name (e.g., "deepseek-v4-flash")
    tags: list = field(default_factory=list)  # e.g., ["frontend", "ui"]
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    transition_history: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "KanbanCard":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def transition(self, new_status: str, phase: str, reason: str = ""):
        """Transition card to a new status, logging the change."""
        old_status = self.status
        self.status = new_status
        self.updated_at = time.time()
        self.transition_history.append({
            "timestamp": time.time(),
            "from": old_status,
            "to": new_status,
            "phase": phase,
            "reason": reason,
        })
        if new_status == STATUS_DONE and not self.phase_completed:
            self.phase_completed = phase


# ---------------------------------------------------------------------------
# Kanban Board
# ---------------------------------------------------------------------------

class KanbanBoard:
    """
    Manages all Kanban cards for a workflow.

    The board is stored as part of WorkflowState and serialized alongside
    the engine state. Cards auto-transition when the workflow phase changes.
    """

    def __init__(self):
        self.cards: dict[str, KanbanCard] = {}

    # ── Card CRUD ──────────────────────────────────────────────────

    def add_card(
        self,
        card_id: str,
        title: str,
        phase: str = "",
        assignee: str = "",
        tags: list = None,
    ) -> KanbanCard:
        """Add a new card to the board."""
        if card_id in self.cards:
            # Update existing
            card = self.cards[card_id]
            card.title = title
            if assignee:
                card.assignee = assignee
            if tags:
                card.tags = tags
            card.updated_at = time.time()
            return card

        card = KanbanCard(
            id=card_id,
            title=title,
            phase_created=phase,
            assignee=assignee,
            tags=tags or [],
        )
        # Set initial status based on current phase
        if phase in PHASE_STATUS_MAP:
            card.status = PHASE_STATUS_MAP[phase]
        self.cards[card_id] = card
        return card

    def update_card(self, card_id: str, **kwargs) -> Optional[KanbanCard]:
        """Update card fields (title, assignee, tags, status)."""
        card = self.cards.get(card_id)
        if not card:
            return None

        if "status" in kwargs:
            card.transition(kwargs["status"], kwargs.get("_phase", ""), kwargs.get("_reason", ""))
            kwargs.pop("status")
            kwargs.pop("_phase", None)
            kwargs.pop("_reason", None)

        for key in ("title", "assignee", "tags"):
            if key in kwargs:
                setattr(card, key, kwargs[key])

        card.updated_at = time.time()
        return card

    def remove_card(self, card_id: str) -> bool:
        """Remove a card from the board."""
        if card_id in self.cards:
            del self.cards[card_id]
            return True
        return False

    def get_card(self, card_id: str) -> Optional[KanbanCard]:
        return self.cards.get(card_id)

    def get_cards_by_status(self, status: str) -> list[KanbanCard]:
        return [c for c in self.cards.values() if c.status == status]

    def get_all_cards(self) -> list[KanbanCard]:
        return list(self.cards.values())

    # ── Auto-transition ────────────────────────────────────────────

    def on_phase_change(self, new_phase: str, old_phase: str = "", reason: str = "", is_rollback: bool = False):
        """
        Auto-transition all cards when the workflow phase changes.

        Called by the engine after advance() or rollback().
        """
        # On rollback: cards that were done/review go back to in_progress
        if is_rollback:
            for card in self.cards.values():
                if card.status in (STATUS_DONE, STATUS_REVIEW):
                    card.transition(STATUS_IN_PROGRESS, new_phase, f"rollback to {new_phase}")
            return

        new_status = PHASE_STATUS_MAP.get(new_phase)
        if not new_status:
            return

        # Normal advance
        if new_status == STATUS_IN_PROGRESS:
            # Execute phase: backlog → in_progress
            for card in self.cards.values():
                if card.status in (STATUS_BACKLOG, STATUS_DONE):
                    card.transition(STATUS_IN_PROGRESS, new_phase, "phase advanced to execute")

        elif new_status == STATUS_REVIEW:
            # Review phase: in_progress → review
            for card in self.cards.values():
                if card.status == STATUS_IN_PROGRESS:
                    card.transition(STATUS_REVIEW, new_phase, "phase advanced to review")

        elif new_status == STATUS_DONE:
            # Deploy/done phase: review → done
            for card in self.cards.values():
                if card.status in (STATUS_REVIEW, STATUS_IN_PROGRESS):
                    card.transition(STATUS_DONE, new_phase, "phase advanced to deploy")

    # ── Serialization ──────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {cid: c.to_dict() for cid, c in self.cards.items()}

    @classmethod
    def from_dict(cls, data: dict) -> "KanbanBoard":
        board = cls()
        for cid, cdata in data.items():
            board.cards[cid] = KanbanCard.from_dict(cdata)
        return board

    def get_stats(self) -> dict:
        """Return summary statistics."""
        total = len(self.cards)
        by_status = {}
        for s in ALL_STATUSES:
            by_status[s] = len([c for c in self.cards.values() if c.status == s])
        return {
            "total": total,
            "by_status": by_status,
            "progress_pct": round((by_status[STATUS_DONE] / total * 100) if total > 0 else 0),
        }

    # ── HTML Rendering ─────────────────────────────────────────────

    def render_html(self, workflow_state: dict = None) -> str:
        """
        Render the Kanban board as a self-contained HTML page.
        Auto-refreshes every 3 seconds to show live updates.
        """
        stats = self.get_stats()
        columns = [
            (STATUS_BACKLOG, "Backlog", "#6B7280"),
            (STATUS_IN_PROGRESS, "In Progress", "#3B82F6"),
            (STATUS_REVIEW, "Review", "#F59E0B"),
            (STATUS_DONE, "Done", "#10B981"),
            (STATUS_BLOCKED, "Blocked", "#EF4444"),
        ]

        current_phase = ""
        project_dir = ""
        if workflow_state:
            current_phase = workflow_state.get("current_phase", "")
            project_dir = workflow_state.get("project_dir", "")

        # Build columns HTML
        cols_html = ""
        for status, label, color in columns:
            cards = self.get_cards_by_status(status)
            cards_html = ""
            for card in cards:
                assignee_badge = ""
                if card.assignee:
                    assignee_badge = f'<span class="badge-assignee">{html.escape(card.assignee)}</span>'

                tags_html = ""
                if card.tags:
                    tags_html = '<div class="tags">' + "".join(
                        f'<span class="tag">{html.escape(t)}</span>' for t in card.tags
                    ) + '</div>'

                cards_html += f'''
                <div class="card" data-status="{status}">
                    <div class="card-title">{html.escape(card.title)}</div>
                    {tags_html}
                    <div class="card-footer">
                        <span class="card-id">#{html.escape(card.id)}</span>
                        {assignee_badge}
                    </div>
                </div>'''

            count = len(cards)
            cols_html += f'''
            <div class="column">
                <div class="column-header" style="border-top-color: {color}">
                    <span class="column-title">{label}</span>
                    <span class="column-count">{count}</span>
                </div>
                <div class="column-cards">{cards_html}</div>
            </div>'''

        # Phase progress bar
        phases_order = ["research", "architecture", "ux_design", "plan", "execute", "ux_review", "test", "verify", "deploy", "done"]
        phases_labels = {
            "research": "Research", "architecture": "Architecture", "ux_design": "UX Design",
            "plan": "Plan", "execute": "Execute", "ux_review": "UX Review",
            "test": "Test", "verify": "Verify", "deploy": "Deploy", "done": "Done",
        }
        current_idx = phases_order.index(current_phase) if current_phase in phases_order else -1

        phases_html = ""
        for i, p in enumerate(phases_order):
            cls = "phase-step"
            if i < current_idx:
                cls += " phase-done"
            elif i == current_idx:
                cls += " phase-active"
            phases_html += f'<div class="{cls}">{phases_labels.get(p, p)}</div>'

        progress = stats["progress_pct"]

        return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GSD Kanban — {html.escape(project_dir or "Workflow")}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #0F1117;
    color: #E4E4E7;
    min-height: 100vh;
    padding: 24px;
}}
.header {{
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 24px;
}}
.header h1 {{ font-size: 24px; font-weight: 700; }}
.header .subtitle {{ font-size: 13px; color: #71717A; margin-top: 4px; }}
.progress-ring {{
    display: flex; align-items: center; gap: 12px;
    background: #1A1B23; padding: 12px 20px; border-radius: 12px;
    border: 1px solid #27272A;
}}
.progress-ring .pct {{ font-size: 28px; font-weight: 800; color: #10B981; }}
.progress-ring .label {{ font-size: 12px; color: #71717A; }}

.phase-track {{
    display: flex; gap: 4px; margin-bottom: 28px;
    overflow-x: auto; padding-bottom: 8px;
}}
.phase-step {{
    padding: 6px 14px; border-radius: 8px; font-size: 12px; font-weight: 500;
    white-space: nowrap; background: #1A1B23; color: #52525B;
    border: 1px solid #27272A; transition: all 0.3s;
}}
.phase-done {{
    background: #10B98122; color: #10B981; border-color: #10B98144;
}}
.phase-active {{
    background: #3B82F622; color: #3B82F6; border-color: #3B82F688;
    box-shadow: 0 0 12px #3B82F633;
}}

.board {{
    display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px;
}}
.column {{
    background: #1A1B23; border-radius: 12px; border: 1px solid #27272A;
    display: flex; flex-direction: column; max-height: calc(100vh - 220px);
}}
.column-header {{
    padding: 14px 16px; border-bottom: 1px solid #27272A;
    display: flex; justify-content: space-between; align-items: center;
    border-top: 3px solid; border-radius: 12px 12px 0 0;
}}
.column-title {{ font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }}
.column-count {{
    background: #27272A; padding: 2px 10px; border-radius: 999px;
    font-size: 12px; font-weight: 600; color: #A1A1AA;
}}
.column-cards {{
    padding: 12px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px;
    flex: 1;
}}
.card {{
    background: #22232B; border: 1px solid #2D2E36; border-radius: 10px;
    padding: 12px 14px; cursor: default; transition: border-color 0.2s;
}}
.card:hover {{ border-color: #3F3F46; }}
.card-title {{ font-size: 13px; font-weight: 500; line-height: 1.4; margin-bottom: 8px; }}
.tags {{ display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 8px; }}
.tag {{
    background: #27272A; padding: 2px 8px; border-radius: 4px;
    font-size: 11px; color: #A1A1AA;
}}
.card-footer {{ display: flex; justify-content: space-between; align-items: center; }}
.card-id {{ font-size: 11px; color: #52525B; font-family: monospace; }}
.badge-assignee {{
    background: #3B82F622; padding: 2px 8px; border-radius: 4px;
    font-size: 11px; color: #60A5FA;
}}
.empty {{ text-align: center; padding: 24px; color: #3F3F46; font-size: 12px; }}

@media (max-width: 900px) {{
    .board {{ grid-template-columns: 1fr 1fr; }}
}}
@media (max-width: 600px) {{
    .board {{ grid-template-columns: 1fr; }}
}}
</style>
<meta http-equiv="refresh" content="3">
</head>
<body>
    <div class="header">
        <div>
            <h1>GSD Kanban Board</h1>
            <div class="subtitle">Project: {html.escape(project_dir or "—")} · Phase: <strong>{html.escape(current_phase or "—")}</strong></div>
        </div>
        <div class="progress-ring">
            <div class="pct">{progress}%</div>
            <div class="label">{stats["by_status"][STATUS_DONE]}/{stats["total"]} tasks<br>completed</div>
        </div>
    </div>

    <div class="phase-track">{phases_html}</div>

    <div class="board">{cols_html}</div>
</body>
</html>'''
