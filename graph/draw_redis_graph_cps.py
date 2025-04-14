import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Read data from file
file_path_get = "../redis-data/redis_dpdk-GET.csv"  # Input file path
file_path_set = "../redis-data/redis_dpdk-SET.csv"  # Input file path

df_get = pd.read_csv(file_path_get)
df_set = pd.read_csv(file_path_set)

# Convert throughput to k req/sec
df_get["throughput"] = df_get["throughput"] / 1000
df_set["throughput"] = df_set["throughput"] / 1000

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
threads = df_get['threads'].unique()
x_positions = np.arange(len(threads)) * 1.5  # Scale positions to widen the gaps
bar_width = 0.6  # Wider bars

# Plotting
fig, axes = plt.subplots(1, 2, figsize=(15, 6), sharey=False)

# Throughput bar graph
for i, mode in enumerate(df_get['mode'].unique()):
    subset = df_get[df_get['mode'] == mode]
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
        y_position = bar.get_height() - 5  # Adjust the text to be closer to the top of the bar
        text_color = 'white'  # Set text color to white
        axes[0].text(
            bar.get_x() + bar.get_width() / 2, 
            y_position, 
            f"{val:.2f}", 
            ha='center', 
            va='top',  # Align text to the top
            fontsize=13, 
            rotation=90,  # Vertical text
            color=text_color,  # Text color white
            fontweight='bold'  # Bold text
        )

# axes[0].set_title("Throughput", fontsize=14, fontweight='bold')
axes[0].set_xlabel("Client Threads", fontsize=26)
axes[0].tick_params(axis='x', labelsize=22)
axes[0].tick_params(axis='y', labelsize=22)
axes[0].set_ylabel("RPS\n(10e3 req/sec)", fontsize=24)
axes[0].legend(title="Mode")
axes[0].set_xticks(x_positions)
axes[0].set_xticklabels(threads)

axes[0].get_legend().remove()

for i, mode in enumerate(df_set['mode'].unique()):
    subset = df_set[df_set['mode'] == mode]
    offset = (i - 0.5) * bar_width
    bars = axes[1].bar(
        x_positions + offset, 
        subset['throughput'], 
        width=bar_width, 
        label=mode, 
        color=colors[mode], 
        alpha=0.9
    )
    for bar, val in zip(bars, subset['throughput']):
        y_position = bar.get_height() - 5  # Adjust the text to be closer to the top of the bar
        text_color = 'white'  # Set text color to white
        axes[1].text(
            bar.get_x() + bar.get_width() / 2, 
            y_position, 
            f"{val:.2f}", 
            ha='center', 
            va='top',  # Align text to the top
            fontsize=13, 
            rotation=90,  # Vertical text
            color=text_color,  # Text color white
            fontweight='bold'  # Bold text
        )

axes[1].set_xlabel("Client Threads", fontsize=26)
axes[1].tick_params(axis='x', labelsize=22)
axes[1].tick_params(axis='y', labelsize=22)
axes[1].legend(title="Mode")
axes[1].set_xticks(x_positions)
axes[1].set_xticklabels(threads)

axes[1].get_legend().remove()


axes[0].text(0.5, 1.02, 'GET', transform=axes[0].transAxes, 
         horizontalalignment='center', fontsize=26)
axes[1].text(0.5, 1.02, 'SET', transform=axes[1].transAxes, 
         horizontalalignment='center', fontsize=26)


# Save the figure as a PDF
output_pdf = "redis_dpdk_performance.pdf"  # Output file path
# plt.tight_layout()

handles, labels = axes[0].get_legend_handles_labels()


new_labels = []
for label in labels:
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
