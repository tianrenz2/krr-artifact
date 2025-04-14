import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Read data from file
file_path = "../../test_data/redis-dpdk/5m/redis_dpdk-SET-avg.csv"  # Input file path
df = pd.read_csv(file_path)

# Convert throughput to k req/sec
df["throughput"] = df["throughput"] / 1000

# Define colors for modes
colors = {
    "krr": (0.3333333333333333, 0.6588235294117647, 0.40784313725490196),
    "native": (0.2980392156862745, 0.4470588235294118, 0.6901960784313725)
}

MODE_DICT = {
    "native": "Native",
    "krr": "KRR",
}

# Uniform x-axis positions for threads, with wider spacing between points
threads = df['threads'].unique()
x_positions = np.arange(len(threads)) * 1.5  # Scale positions to widen the gaps
bar_width = 0.6  # Wider bars

# Plotting
fig, axes = plt.subplots(1, 2, figsize=(15, 6), sharey=False)

# Throughput bar graph
for i, mode in enumerate(df['mode'].unique()):
    subset = df[df['mode'] == mode]
    offset = (i - 0.5) * bar_width
    bars = axes[0].bar(
        x_positions + offset, 
        subset['throughput'], 
        width=bar_width, 
        label=mode, 
        color=colors[mode], 
        alpha=0.9
    )
    for bar, val in zip(bars, subset['throughput']):
        y_position = bar.get_height() - 10  # Adjust the text to be closer to the top of the bar
        text_color = 'white'  # Set text color to white
        axes[0].text(
            bar.get_x() + bar.get_width() / 2, 
            y_position, 
            f"{val:.2f}", 
            ha='center', 
            va='top',  # Align text to the top
            fontsize=14, 
            rotation=90,  # Vertical text
            color=text_color,  # Text color white
            fontweight='bold'  # Bold text
        )

# axes[0].set_title("Throughput", fontsize=14, fontweight='bold')
axes[0].set_xlabel("Client Threads", fontsize=16)
axes[0].tick_params(axis='x', labelsize=16)
axes[0].tick_params(axis='y', labelsize=16)
axes[0].set_ylabel("Throughput\n(Thousands Req/Sec)", fontsize=16)
axes[0].legend(title="Mode")
axes[0].set_xticks(x_positions)
axes[0].set_xticklabels(threads)

axes[0].get_legend().remove()

# p99 Latency bar graph
for i, mode in enumerate(df['mode'].unique()):
    subset = df[df['mode'] == mode]
    offset = (i - 0.5) * bar_width
    bars = axes[1].bar(
        x_positions + offset, 
        subset['p99_latency'], 
        width=bar_width, 
        label=mode, 
        color=colors[mode], 
        alpha=0.9
    )
    for bar, val in zip(bars, subset['p99_latency']):
        y_position = bar.get_height() - 0.02  # Adjust the text to be closer to the top of the bar
        text_color = 'white'  # Set text color to white
        axes[1].text(
            bar.get_x() + bar.get_width() / 2, 
            y_position, 
            f"{val:.3f}", 
            ha='center', 
            va='top',  # Align text to the top
            fontsize=14, 
            rotation=90,  # Vertical text
            color=text_color,  # Text color white
            fontweight='bold'  # Bold text
        )

axes[1].set_xlabel("Client Threads", fontsize=16)
axes[1].set_ylabel("P99 Latency (ms)", fontsize=16)
axes[1].tick_params(axis='x', labelsize=16)
axes[1].tick_params(axis='y', labelsize=16)
axes[1].legend(title="Mode")
axes[1].set_xticks(x_positions)
axes[1].set_xticklabels(threads)

axes[1].get_legend().remove()

handles, labels = axes[0].get_legend_handles_labels()

# Save the figure as a PDF
output_pdf = "redis_dpdk_performance.pdf"  # Output file path
# plt.tight_layout()

new_labels = []
for label in colors.keys():
    new_labels.append(MODE_DICT[label])
plt.legend(
    handles, new_labels,
    loc='upper center', ncol=len(labels),
    bbox_to_anchor=(0.5, 1), bbox_transform=fig.transFigure,
    fontsize=16, frameon=True
)

plt.tight_layout()
plt.subplots_adjust(wspace=0.15)

plt.savefig(output_pdf, format="pdf")
plt.show()

print(f"Graphs have been saved as {output_pdf}")
