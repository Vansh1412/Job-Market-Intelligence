"""
Script to generate the Phase 7 Final Architecture Diagram
Saves to reports/figures/final_architecture.png
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_diagram():
    fig, ax = plt.subplots(figsize=(16, 14), dpi=300)
    fig.patch.set_facecolor('#0B0F19')
    ax.set_facecolor('#0B0F19')

    # Hide axes
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 105)
    ax.axis('off')

    # Title
    ax.text(50, 101.5, "JOBINTEL: END-TO-END PRODUCTION ARCHITECTURE", 
            ha='center', va='center', color='#FFFFFF', fontsize=21, fontweight='bold', family='sans-serif')
    ax.text(50, 98.8, "Unified Cross-Market Predictive Analytics & Skill Archetype System | Frozen Model SSOT", 
            ha='center', va='center', color='#94A3B8', fontsize=11, family='sans-serif')

    # Color definitions
    USA_COLOR = '#10B981'
    IND_COLOR = '#F97316'
    COMM_COLOR = '#38BDF8'
    TEXT_MUTED = '#94A3B8'

    def draw_box(x, y, w, h, title, subtitle, details, border_color, fill_color):
        rect = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.6,rounding_size=1.2",
            facecolor=fill_color,
            edgecolor=border_color,
            linewidth=1.8,
            alpha=0.98
        )
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 1.5, title, ha='center', va='center', color=border_color, fontsize=11, fontweight='bold')
        if subtitle:
            ax.text(x + w/2, y + h - 2.9, subtitle, ha='center', va='center', color='#E2E8F0', fontsize=9, fontweight='semibold')
        if details:
            for i, line in enumerate(details):
                ax.text(x + 1.8, y + h - 4.4 - (i * 1.3), line, ha='left', va='center', color=TEXT_MUTED, fontsize=8)

    def draw_arrow(x1, y1, x2, y2, color):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(facecolor=color, edgecolor=color, width=1.6, headwidth=7, headlength=7, alpha=0.9))

    # ================= LAYER 1: DATA =================
    ax.text(6, 89.5, "1. DATA LAYER", ha='left', va='center', color='#64748B', fontsize=10, fontweight='bold')
    # USA Data
    draw_box(16, 84, 31, 9.5, "USA TECH CORPUS (N=34,036)", "Dataset A + NextGig Integration", 
             ["• Tier-1 ATS Job Postings (Cleaned & De-duplicated)", "• Annual Base Salary (USD, Median $180,413)", "• 82 Binary Tech Skill Presence Tokens"],
             USA_COLOR, '#06281E')
    # India Data
    draw_box(53, 84, 31, 9.5, "INDIA TECH CORPUS (N=5,859)", "Naukri Multi-City Tech Corpus", 
             ["• 5 Major Metros (Bengaluru, Hyd, Pune, etc.)", "• Annual Base Salary Midpoint (INR, Median ₹10.0 LPA)", "• 284 Clean Tech Skill Indicators + Experience"],
             IND_COLOR, '#38160B')

    # Arrows 1 -> 2
    draw_arrow(31.5, 84, 31.5, 79.5, USA_COLOR)
    draw_arrow(68.5, 84, 68.5, 79.5, IND_COLOR)

    # ================= LAYER 2: PREPROCESSING =================
    ax.text(6, 75, "2. PREPROCESSING", ha='left', va='center', color='#64748B', fontsize=10, fontweight='bold')
    # USA Preprocessing
    draw_box(16, 70, 31, 9, "USA FEATURE PIPELINE (123 FEATS)", "Frozen ColumnTransformer & Scaler", 
             ["• Categorical One-Hot Encoding (Role, Seniority, City)", "• Binary Skill Matrix (82 cols)", "• StandardScaler for Centered PCA (12 dims)"],
             USA_COLOR, '#06281E')
    # India Preprocessing
    draw_box(53, 70, 31, 9, "INDIA FEATURE PIPELINE (290 FEATS)", "Frozen DictVectorizer & Log1p Pipeline", 
             ["• Log1p Target Transformation ln(1 + INR Salary)", "• 284 Technical Skill Indicators + Experience Span", "• Centered Covariance PCA (15 dims)"],
             IND_COLOR, '#38160B')

    # Arrows 2 -> 3
    draw_arrow(31.5, 70, 31.5, 65.5, USA_COLOR)
    draw_arrow(68.5, 70, 68.5, 65.5, IND_COLOR)

    # ================= LAYER 3: FROZEN MODELS =================
    ax.text(6, 61, "3. FROZEN MODELS", ha='left', va='center', color='#64748B', fontsize=10, fontweight='bold')
    # USA Models
    draw_box(16, 56, 31, 9, "USA FROZEN MODELS (SSOT)", "XGBoost Regressor + KMeans (k=7)", 
             ["• Salary: XGBoost (MAE $36,380.64 | R² 0.4233)", "• Archetypes: 7 Clusters (AI/ML, Backend, Cloud, etc.)", "• SHA-256: 55c1b7fcf7c... / 4d6d2508..."],
             USA_COLOR, '#06281E')
    # India Models
    draw_box(53, 56, 31, 9, "INDIA FROZEN MODELS (SSOT)", "HistGradientBoosting + KMeans (k=6)", 
             ["• Salary: HistGB (MAE ₹3.71 LPA | R² 0.5798)", "• Archetypes: 6 Clusters (Big Data, Java, AI, etc.)", "• SHA-256: 7a3490d7a36... / 4465a3d7..."],
             IND_COLOR, '#38160B')

    # Arrows 3 -> 4
    draw_arrow(31.5, 56, 42, 51.5, USA_COLOR)
    draw_arrow(68.5, 56, 58, 51.5, IND_COLOR)

    # ================= LAYER 4: MODEL REGISTRY =================
    ax.text(6, 47, "4. MODEL REGISTRY", ha='left', va='center', color='#64748B', fontsize=10, fontweight='bold')
    draw_box(28, 42.5, 44, 8.5, "CENTRALIZED MODEL REGISTRY (SINGLETON)", "Bitwise Cryptographic Verification Hub", 
             ["• 10/10 Frozen Artifact SHA-256 Checksum Validation", "• In-Memory Singleton Cache (Zero Request-Time Reload)", "• Zero Retraining / Zero Fit Enforcement Gate"],
             COMM_COLOR, '#07243A')

    # Arrow 4 -> 5
    draw_arrow(50, 42.5, 50, 39, COMM_COLOR)

    # ================= LAYER 5: FASTAPI BACKEND =================
    ax.text(6, 34, "5. REST API", ha='left', va='center', color='#64748B', fontsize=10, fontweight='bold')
    draw_box(16, 29, 68, 9.5, "FASTAPI HIGH-PERFORMANCE REST GATEWAY", "Pydantic V2 Validated Endpoints | Structured Logging & Error Handling", 
             ["• Health & Readiness: /api/health (Liveness) & /api/ready (Model Verification Probe)", 
              "• USA Endpoints: /api/usa/predict, /api/usa/archetype, /api/usa/market-summary, /api/usa/options",
              "• India Endpoints: /api/india/predict, /api/india/archetype, /api/india/market-summary, /api/india/options",
              "• Cross-Market & Meta: /api/cross-market/summary, /api/meta (Zero FX Conversion Policy)"],
             COMM_COLOR, '#0F172A')

    # Arrow 5 -> 6
    draw_arrow(50, 29, 50, 25.5, COMM_COLOR)

    # ================= LAYER 6: REACT FRONTEND =================
    ax.text(6, 20.5, "6. FRONTEND SPA", ha='left', va='center', color='#64748B', fontsize=10, fontweight='bold')
    draw_box(16, 15.5, 68, 9.5, "JOBINTEL REACT 19 + TYPESCRIPT USER INTERFACE", "Glassmorphic Dark UI | Atomic Context State | Strict Scientific Guardrails", 
             ["• Interactive Salary Calculator: Guided Multi-Step Wizard with Live Recalculation", 
              "• Skill Archetype Explorer: PCA Cluster Projections, Observed MAE, and Relative Error", 
              "• Cross-Market Lens: Structural Market Comparison (USD vs INR Isolated Currencies)", 
              "• Academic Integrity: Empirical Caveats for High Compensation (≥20 LPA) & Small Sample Archetypes"],
             '#A855F7', '#1E1035')

    # Arrow 6 -> 7
    draw_arrow(50, 15.5, 50, 11.8, '#A855F7')

    # ================= LAYER 7: USER JOURNEYS =================
    ax.text(6, 7.5, "7. END USER", ha='left', va='center', color='#64748B', fontsize=10, fontweight='bold')
    draw_box(22, 3.5, 56, 7.8, "JOBINTEL USERS: CANDIDATES, RECRUITERS & RESEARCHERS", "Empirical Decision Support with Transparent Lineage", 
             ["• Defensible Compensation Estimates grounded in validated holdout evaluation", 
              "• Market Valuation Skill Discovery across 82 (USA) and 284 (India) tech tokens", 
              "• Granular Peer Benchmark Context without arbitrary currency conversions"],
             '#EC4899', '#2E081F')

    os.makedirs("reports/figures", exist_ok=True)
    out_path = "reports/figures/final_architecture.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"SUCCESS: Regenerated {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == "__main__":
    generate_diagram()
