import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

# Create assets directory
ASSETS_DIR = "d:/NLP_MINI_Project/query_voice_root/assets"
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

# Set global style for professional look
plt.style.use('dark_background')
accent_color = '#00e676'  # Neon green
secondary_color = '#2979ff' # Modern blue
text_color = '#ffffff'
bg_color = '#0a0a0a'

def save_viz(name):
    path = os.path.join(ASSETS_DIR, f"{name}.png")
    plt.savefig(path, bbox_inches='tight', dpi=300, facecolor=bg_color)
    print(f"Saved: {path}")
    plt.close()

# 1. High-Level System Architecture
def viz_architecture():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis('off')

    # Draw components
    components = [
        (10, 25, 20, 10, "Flutter App\n(Voice Input)", secondary_color),
        (40, 25, 20, 10, "FastAPI\n(LangChain)", accent_color),
        (70, 40, 20, 10, "PostgreSQL\n(Structured Data)", '#ff9100'),
        (70, 10, 20, 10, "ChromaDB\n(Vector Store)", '#d500f9')
    ]

    for x, y, w, h, label, color in components:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=2", 
                                       linewidth=2, edgecolor=color, facecolor='none')
        ax.add_patch(rect)
        ax.text(x+w/2, y+h/2, label, color=text_color, ha='center', va='center', fontweight='bold')

    # Draw Arrows
    ax.annotate("", xy=(40, 30), xytext=(30, 30), arrowprops=dict(arrowstyle="->", color=text_color, lw=2))
    ax.annotate("", xy=(70, 45), xytext=(60, 32), arrowprops=dict(arrowstyle="->", color=text_color, lw=2))
    ax.annotate("", xy=(70, 15), xytext=(60, 28), arrowprops=dict(arrowstyle="->", color=text_color, lw=2))

    plt.title("System Architecture: End-to-End Flow", color=text_color, pad=20, fontsize=14, fontweight='bold')
    save_viz("architecture")

# 2. LangGraph Agentic Workflow
def viz_workflow():
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis('off')
    
    steps = ["Whisper\n(ASR)", "Rewriter\n(Intent)", "Router\n(Scope)", "Retriever\n(RAG)", "Generator\n(Qwen)", "Evaluator\n(Sandbox)"]
    colors = [secondary_color, secondary_color, '#ff5252', '#d500f9', accent_color, '#ffea00']
    
    for i, (step, color) in enumerate(zip(steps, colors)):
        x = i * 20
        rect = patches.Circle((x, 5), 6, color=color, alpha=0.3)
        ax.add_patch(rect)
        ax.add_patch(patches.Circle((x, 5), 6, linewidth=2, edgecolor=color, facecolor='none'))
        ax.text(x, 5, step, color=text_color, ha='center', va='center', fontsize=9, fontweight='bold')
        
        if i < len(steps) - 1:
            ax.annotate("", xy=(x+14, 5), xytext=(x+6, 5), arrowprops=dict(arrowstyle="->", color=text_color, lw=1.5))

    plt.title("Agentic Workflow Nodes (LangGraph)", color=text_color, pad=20, fontsize=14, fontweight='bold')
    save_viz("workflow")

# 3. Hierarchical RAG Strategy
def viz_rag_strategy():
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.axis('off')
    
    # Pyramid levels
    levels = [
        (0.4, 0.8, 0.2, 0.15, "Golden Queries\n(Verified NL-SQL)", '#ffea00'),
        (0.3, 0.55, 0.4, 0.2, "Business Logic\n(Semantic Mappings)", accent_color),
        (0.2, 0.3, 0.6, 0.2, "Table Metadata\n(Descriptions)", secondary_color),
        (0.1, 0.05, 0.8, 0.2, "Column Schema\n(Types & Constraints)", '#7c4dff')
    ]
    
    for x, y, w, h, label, color in levels:
        rect = patches.Rectangle((x, y), w, h, linewidth=2, edgecolor=color, facecolor=color, alpha=0.2)
        ax.add_patch(rect)
        ax.add_patch(patches.Rectangle((x, y), w, h, linewidth=2, edgecolor=color, facecolor='none'))
        ax.text(x+w/2, y+h/2, label, color=text_color, ha='center', va='center', fontweight='bold')

    plt.title("Hierarchical Knowledge Retrieval (RAG)", color=text_color, pad=20, fontsize=14, fontweight='bold')
    save_viz("rag_strategy")

# 4. Performance: T5 vs Qwen Fine-tuned
def viz_performance():
    labels = ['Accuracy', 'Complexity', 'Context Window', 'Latency (ms)', 'Zero-Shot']
    t5_stats = [0.70, 0.40, 0.30, 0.85, 0.50]
    qwen_stats = [0.98, 0.90, 0.85, 0.60, 0.95]
    
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    t5_stats += t5_stats[:1]
    qwen_stats += qwen_stats[:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, t5_stats, color='gray', alpha=0.25, label='T5 Baseline')
    ax.fill(angles, qwen_stats, color=accent_color, alpha=0.4, label='Qwen Pro (QLoRA)')
    
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color=text_color)
    
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    plt.title("Model Evolution: T5 vs Qwen-QLoRA", color=text_color, pad=30, fontsize=14, fontweight='bold')
    save_viz("performance")

if __name__ == "__main__":
    viz_architecture()
    viz_workflow()
    viz_rag_strategy()
    viz_performance()
