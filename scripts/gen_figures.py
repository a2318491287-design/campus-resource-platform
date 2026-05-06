"""
Generate 5 PNG diagrams used by Campus_Resource_Platform_Report.docx:
  Figure 1: Feature overview Mind-Map (1.4)
  Figure 2: DFD - Smart Resource Retrieval (2.1.4)
  Figure 3: DFD - Upload & Review System (2.2.4)
  Figure 4: DFD - Points & Reward System (2.3.4)
  Figure 5: DFD - AI-assisted Recommendation (3.1.3, v2.0)

Style mirrors the sample.pdf DFDs (yellow fills, schematic arrows).
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D
import os

OUT_DIR = '/Users/yuxianglian/Documents/系统分析与设计/SAD_Project/figures'
os.makedirs(OUT_DIR, exist_ok=True)

# Sample.pdf-style colors
ENT_FILL = '#FFEB99'        # entities: warm yellow
PROC_FILL = '#FEF6CC'       # processes: lighter yellow
STORE_FILL = '#D9D9D9'      # data stores: gray
TEXT_COLOR = '#000000'
ACCENT = '#1F497D'
EDGE = '#666666'

plt.rcParams['font.family'] = ['Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.unicode_minus'] = False


def box(ax, x, y, w, h, text, *, fill=ENT_FILL, fontsize=10, bold=False, edgecolor=EDGE):
    """Rectangle with centered text (entity / process)"""
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                          linewidth=1.2, edgecolor=edgecolor, facecolor=fill)
    ax.add_patch(rect)
    weight = 'bold' if bold else 'normal'
    ax.text(x + w/2, y + h/2, text, ha='center', va='center',
            fontsize=fontsize, fontweight=weight, color=TEXT_COLOR, wrap=True)


def proc(ax, x, y, w, h, num, label, *, fontsize=9):
    """Process: rectangle with a small number tag at top-left"""
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                          linewidth=1.2, edgecolor=EDGE, facecolor=PROC_FILL)
    ax.add_patch(rect)
    # Number tag
    ax.text(x + 0.06, y + h - 0.06, str(num), ha='left', va='top',
            fontsize=8, fontweight='bold', color='#888888')
    # Label
    ax.text(x + w/2, y + h/2 - 0.02, label, ha='center', va='center',
            fontsize=fontsize, color=TEXT_COLOR, wrap=True)


def store(ax, x, y, w, h, code, label):
    """Data store: gray box with D-code and label below"""
    rect = mpatches.Rectangle((x, y), w, h, linewidth=1.2,
                              edgecolor=EDGE, facecolor=STORE_FILL)
    ax.add_patch(rect)
    ax.text(x + 0.08, y + h/2, code, ha='left', va='center',
            fontsize=10, fontweight='bold', color=TEXT_COLOR)
    ax.text(x + w/2 + 0.08, y + h/2, label, ha='center', va='center',
            fontsize=9, color=TEXT_COLOR)


def arrow(ax, x1, y1, x2, y2, label='', *, color=ACCENT, lw=1.4, label_offset=(0, 0.05)):
    """Curved arrow with optional label"""
    arr = FancyArrowPatch((x1, y1), (x2, y2),
                          arrowstyle='-|>', mutation_scale=14,
                          color=color, linewidth=lw,
                          connectionstyle="arc3,rad=0")
    ax.add_patch(arr)
    if label:
        mx = (x1 + x2)/2 + label_offset[0]
        my = (y1 + y2)/2 + label_offset[1]
        ax.text(mx, my, label, ha='center', va='center', fontsize=8,
                color=ACCENT, style='italic',
                bbox=dict(boxstyle='round,pad=0.18', facecolor='white', edgecolor='none'))


def setup_axes(figsize=(11, 7), title=None):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.set_aspect('equal')
    ax.axis('off')
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold', pad=15, color=ACCENT)
    return fig, ax


# ==================================================================
# FIGURE 1 — MIND MAP (left-vertical layout, no overlap)
# ==================================================================
fig, ax = plt.subplots(figsize=(13, 9))
ax.set_xlim(0, 14)
ax.set_ylim(0, 12)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title("Figure 1.  Feature overview mind-map",
             fontsize=12, fontweight='bold', pad=12, color=ACCENT)

# Central node (left side)
cx, cy = 2.5, 6.0
center = FancyBboxPatch((cx-1.4, cy-0.6), 2.8, 1.2,
                       boxstyle="round,pad=0.04",
                       linewidth=2, edgecolor=ACCENT, facecolor=ACCENT)
ax.add_patch(center)
ax.text(cx, cy, "MUST Campus\nResource\nPlatform",
        ha='center', va='center', fontsize=12, fontweight='bold', color='white')

branches = [
    ("Smart Search",
     ["Keyword input", "Course code filter", "Year + type filter", "Min rating filter"],
     '#0F6E8C'),
    ("Verified Upload",
     ["File dropzone", "Metadata form", "Tags (≥ 2)", "Submit for review"],
     '#2B8AB5'),
    ("Points System",
     ["Welcome bonus 100", "Earn: upload +10 / download +2 / rating +1",
      "Spend: download -1 / redeem", "Atomic transaction"],
     '#7C9D32'),
    ("Content Review",
     ["Admin queue", "Approve / Reject", "Rejection reasons", "Audit trail"],
     '#B45309'),
    ("My Dashboard",
     ["Balance", "Transaction history", "Leaderboard rank", "Upload count"],
     '#6B466E'),
]

# Vertical layout: 5 branches stacked on the right
n_branches = len(branches)
top = 11.0; bottom = 1.0
hub_y_positions = [top - i * (top - bottom) / (n_branches - 1) for i in range(n_branches)]

hub_x = 6.5
sub_x_start = 9.0

for (name, sub_items, bcolor), hy in zip(branches, hub_y_positions):
    # Connector from center to branch hub (curved)
    ax.annotate('', xy=(hub_x - 1.1, hy), xytext=(cx + 1.4, cy),
                arrowprops=dict(arrowstyle='-', color=bcolor, lw=1.5,
                                connectionstyle=f"arc3,rad=0"))

    # Branch hub box
    hub = FancyBboxPatch((hub_x - 1.1, hy - 0.35), 2.2, 0.7,
                        boxstyle="round,pad=0.04",
                        linewidth=1.5, edgecolor=bcolor, facecolor='#FFFFFF')
    ax.add_patch(hub)
    ax.text(hub_x, hy, name, ha='center', va='center',
            fontsize=11, fontweight='bold', color=bcolor)

    # Sub-items: vertical list to the right
    n = len(sub_items)
    sub_y_offsets = [(i - (n-1)/2) * 0.45 for i in range(n)]
    for sub_offset, item in zip(sub_y_offsets, sub_items):
        sy = hy - sub_offset
        sx = sub_x_start
        # Connector from hub to sub-item
        ax.plot([hub_x + 1.1, sx], [hy, sy],
                color=bcolor, linewidth=0.8, alpha=0.6, zorder=0)
        # Sub-item label
        ax.text(sx, sy, item, ha='left', va='center',
                fontsize=9, color='#222222',
                bbox=dict(boxstyle='round,pad=0.20',
                          facecolor='#F8F5EE', edgecolor=bcolor, linewidth=0.7))

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'fig1_mindmap.png'),
            dpi=180, bbox_inches='tight', facecolor='white')
plt.close()
print("✓ fig1_mindmap.png")


# ==================================================================
# FIGURE 2 — DFD: Smart Academic Resource Retrieval
# ==================================================================
fig, ax = setup_axes((11.5, 6.5),
                     "Figure 2.  DFD — Smart Academic Resource Retrieval")

# User entity (left)
box(ax, 0.5, 3.0, 1.6, 1.0, "User", fontsize=11, bold=True)

# Process 1: Search Handler
proc(ax, 3.0, 5.5, 2.0, 1.0, "1", "Receive Search\nRequest")

# Process 2: Apply Filters & Match
proc(ax, 6.0, 5.5, 2.4, 1.0, "2", "Filter & Score\n(40/30/30 weights)")

# Process 3: Rank & Return
proc(ax, 9.0, 5.5, 2.0, 1.0, "3", "Rank &\nReturn Results")

# Process 4: Charge Download
proc(ax, 6.0, 1.5, 2.4, 1.0, "4", "Charge Download\n(atomic txn)")

# Data stores
store(ax, 3.0, 3.0, 2.5, 0.6, "D1", "Resources")
store(ax, 6.5, 3.0, 2.5, 0.6, "D2", "Tags")
store(ax, 9.5, 3.0, 2.0, 0.6, "D3", "Ratings")

# File storage
box(ax, 0.5, 1.2, 1.6, 1.0, "File\nStorage", fill=STORE_FILL, fontsize=10)

# Arrows
arrow(ax, 2.1, 3.7, 3.0, 5.7, "1. query")
arrow(ax, 5.0, 6.0, 6.0, 6.0, "2. matches")
arrow(ax, 5.5, 5.5, 4.5, 3.6, "DB read", lw=1, color='#888888')
arrow(ax, 7.5, 5.5, 7.5, 3.6, "DB read", lw=1, color='#888888')
arrow(ax, 8.4, 6.0, 9.0, 6.0, "3. scored")
arrow(ax, 10.0, 5.5, 10.5, 3.6, "DB read", lw=1, color='#888888')
arrow(ax, 10.0, 5.5, 2.1, 4.0, "4. ranked list", color=ACCENT)

# Click download flow
arrow(ax, 1.3, 3.0, 6.0, 2.0, "5. click download", color='#B45309')
arrow(ax, 7.2, 1.5, 4.5, 3.0, "deduct +1\npoint", lw=1, color='#888888')
arrow(ax, 7.0, 1.5, 1.5, 1.7, "6. file stream", color='#B45309')

# Legend
ax.text(0.5, 0.4, "● Entity (yellow)   ● Process (numbered)   ● Data store (gray, D-code)",
        fontsize=8, color='#666666', style='italic')

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'fig2_dfd_retrieval.png'),
            dpi=180, bbox_inches='tight', facecolor='white')
plt.close()
print("✓ fig2_dfd_retrieval.png")


# ==================================================================
# FIGURE 3 — DFD: Upload & Review System
# ==================================================================
fig, ax = setup_axes((11.5, 6.5),
                     "Figure 3.  DFD — Upload & Review System")

# Student entity
box(ax, 0.5, 5.5, 1.6, 1.0, "Student\n(Uploader)", fontsize=10, bold=True)

# Admin entity
box(ax, 0.5, 0.7, 1.6, 1.0, "Admin\nReviewer", fontsize=10, bold=True)

# Process 1: Upload Handler (validate)
proc(ax, 3.0, 5.5, 2.4, 1.0, "1", "Validate File\n+ Metadata")

# Process 2: Create Pending Row
proc(ax, 6.5, 5.5, 2.4, 1.0, "2", "Create Pending\nResource Row")

# Process 3: Review Queue
proc(ax, 6.5, 3.0, 2.4, 1.0, "3", "Review Queue\n(Approve / Reject)")

# Process 4: Publish + Reward
proc(ax, 9.5, 5.5, 2.2, 1.0, "4", "Publish &\nCredit +10")

# Process 5: Notify
proc(ax, 3.0, 1.0, 2.4, 1.0, "5", "Notify\nUploader")

# Data stores
store(ax, 6.5, 1.5, 2.4, 0.6, "D1", "Resources")
store(ax, 9.5, 3.0, 2.2, 0.6, "D2", "PointRecord")
store(ax, 9.5, 1.5, 2.2, 0.6, "D3", "Object\nStorage")

# Arrows
arrow(ax, 2.1, 6.0, 3.0, 6.0, "file + meta")
arrow(ax, 5.4, 6.0, 6.5, 6.0, "valid → PENDING")
arrow(ax, 8.9, 5.7, 9.5, 5.7, "approve")
arrow(ax, 7.7, 5.5, 7.7, 4.0, "queue", lw=1, color='#888888')
arrow(ax, 6.5, 3.5, 2.1, 1.5, "reject + reason", color='#B45309')
arrow(ax, 1.5, 1.7, 6.5, 3.5, "decision", color=ACCENT)
arrow(ax, 8.9, 3.5, 9.5, 3.3, "audit row", lw=1, color='#888888')
arrow(ax, 8.0, 3.0, 7.7, 2.1, "status update", lw=1, color='#888888')
arrow(ax, 10.6, 5.5, 10.6, 2.1, "stored file", lw=1, color='#888888')
arrow(ax, 4.2, 5.5, 4.2, 2.0, "→ notify", lw=1, color='#888888')
arrow(ax, 3.0, 1.5, 2.1, 5.7, "✓ published / ✗ rejected", color='#B45309')

ax.text(0.5, 0.1,
        "● Entity (yellow)   ● Process (numbered)   ● Data store (gray, D-code)   ● Admin gate prevents low-quality / copyright resources",
        fontsize=8, color='#666666', style='italic')

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'fig3_dfd_upload.png'),
            dpi=180, bbox_inches='tight', facecolor='white')
plt.close()
print("✓ fig3_dfd_upload.png")


# ==================================================================
# FIGURE 4 — DFD: Points & Reward System
# ==================================================================
fig, ax = setup_axes((11.5, 6.5),
                     "Figure 4.  DFD — Points & Reward System")

# User entity
box(ax, 0.5, 3.0, 1.6, 1.0, "User", fontsize=11, bold=True)

# Action event sources
box(ax, 0.5, 5.5, 1.6, 1.0, "Upload\nApproval", fontsize=9)
box(ax, 0.5, 0.7, 1.6, 1.0, "Rating\nReceived", fontsize=9)

# Process 1: Event Receiver
proc(ax, 3.5, 5.0, 2.2, 1.0, "1", "Event\nReceiver")

# Process 2: Points Engine (CENTRAL)
proc(ax, 6.5, 4.0, 2.6, 1.5, "2", "Points Engine\n(SELECT FOR UPDATE\natomic transaction)")

# Process 3: Apply Reward
proc(ax, 6.5, 1.0, 2.6, 1.0, "3", "Apply Reward\n(if redeem)")

# Data stores (right side)
store(ax, 10.0, 5.0, 2.0, 0.6, "D1", "Users")
store(ax, 10.0, 4.0, 2.0, 0.6, "D2", "PointRecord")
store(ax, 10.0, 3.0, 2.0, 0.6, "D3", "Redemptions")

# Process 4: Notification
proc(ax, 3.5, 1.5, 2.2, 1.0, "4", "Notify User")

# Arrows: action events flowing into Points Engine
arrow(ax, 2.1, 6.0, 3.5, 5.5, "+10 event")
arrow(ax, 1.3, 5.5, 1.3, 4.0, lw=1, color='#888888')   # user → user box stub
arrow(ax, 2.1, 3.5, 3.5, 5.0, "-1 download")
arrow(ax, 2.1, 1.2, 3.5, 5.2, "+1 rating")
arrow(ax, 5.7, 5.4, 6.5, 5.0, "event", lw=1.2)

# Engine → DB
arrow(ax, 9.1, 5.0, 10.0, 5.3, "lock + update", color='#888888', lw=1)
arrow(ax, 9.1, 4.5, 10.0, 4.3, "audit row", color='#888888', lw=1)
arrow(ax, 9.1, 4.0, 10.0, 3.3, "redeem rec.", color='#888888', lw=1)

# Engine → user notification
arrow(ax, 6.5, 4.0, 5.7, 2.0, "balance Δ", color='#B45309')
arrow(ax, 5.7, 2.0, 2.1, 3.5, "✓ confirmed", color='#B45309')

# Engine → reward apply
arrow(ax, 7.5, 4.0, 7.5, 2.0, "if REDEEM_*", lw=1, color='#888888')

# Legend
ax.text(0.5, 0.1, "● Entity (yellow)   ● Process (numbered)   ● Data store (gray, D-code)   ● Atomic txn = no race condition",
        fontsize=8, color='#666666', style='italic')

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'fig4_dfd_points.png'),
            dpi=180, bbox_inches='tight', facecolor='white')
plt.close()
print("✓ fig4_dfd_points.png")


# ==================================================================
# FIGURE 5 — DFD: AI-assisted Recommendation (v2.0)
# ==================================================================
fig, ax = setup_axes((11.5, 6.5),
                     "Figure 5.  DFD — AI-assisted Recommendation (v2.0)")

# User
box(ax, 0.5, 3.0, 1.6, 1.0, "User", fontsize=11, bold=True)

# Process 1: Read History
proc(ax, 3.0, 5.0, 2.2, 1.0, "1", "Read User\nHistory")

# Process 2: Filter Candidates
proc(ax, 6.0, 5.0, 2.2, 1.0, "2", "Filter by Major\n+ Course Tag")

# Process 3: AI Engine (highlighted)
proc(ax, 9.0, 5.0, 2.2, 1.0, "3", "AI Engine\n(hybrid model)")

# Process 4: Rank & Explain
proc(ax, 9.0, 2.5, 2.2, 1.0, "4", "Rank & Add\nExplanation")

# Process 5: Feedback Loop
proc(ax, 3.0, 2.0, 2.2, 1.0, "5", "Feedback\nUpdate")

# Data stores
store(ax, 3.0, 6.5, 2.0, 0.6, "D1", "User History")
store(ax, 6.0, 6.5, 2.0, 0.6, "D2", "Resources")
store(ax, 9.0, 6.5, 2.0, 0.6, "D3", "Ratings")

# Arrows
arrow(ax, 2.1, 3.7, 3.0, 5.2, "page open")
arrow(ax, 4.0, 6.0, 4.0, 6.5, lw=1, color='#888888')
arrow(ax, 5.2, 5.5, 6.0, 5.5, "user vector")
arrow(ax, 7.0, 6.0, 7.0, 6.5, lw=1, color='#888888')
arrow(ax, 8.2, 5.5, 9.0, 5.5, "candidates")
arrow(ax, 10.0, 6.0, 10.0, 6.5, lw=1, color='#888888')
arrow(ax, 10.0, 5.0, 10.0, 3.5, "scored list")
arrow(ax, 9.0, 3.0, 2.1, 3.4, "recommendation cards", color=ACCENT)

# Feedback loop
arrow(ax, 1.3, 3.0, 3.0, 2.5, "click / dismiss", color='#B45309')
arrow(ax, 5.2, 2.5, 4.0, 6.5, "update history", lw=1, color='#888888')

# Legend
ax.text(0.5, 0.4,
        "v2.0 extends v1.0 retrieval — adds explainable suggestions ranked by user-major + history similarity",
        fontsize=8, color='#666666', style='italic')

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'fig5_dfd_recommendation.png'),
            dpi=180, bbox_inches='tight', facecolor='white')
plt.close()
print("✓ fig5_dfd_recommendation.png")


print(f"\n✅ All figures saved to {OUT_DIR}/")
