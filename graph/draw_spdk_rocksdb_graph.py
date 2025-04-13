import os.path as osp
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import AutoMinorLocator
from matplotlib.ticker import MaxNLocator
import pandas
import seaborn


RAW_DATA_DIR = "../rocksdb-spdk-data/"

WORKLOAD_DICT = {
    "readseq": "1 sequential reader", \
    "seekrandom": "1 random seeker",
    "readrandom": "1 random reader",
    "fillseq" : "1 sequential writer", \
    "fillrandom" : "1 random writer", \
    "deleteseq": "1 sequential deletion",
    "appendrandom": "1 random appender",
}

ROCKSDB_DICT = {
    "original" : "kernel-IO", \
    "spdk" : "SPDK", \
}

NUMCPU_LIST = [2]
MODE_DICT = {
    "baseline": "Native",
    "kernel_rr": "KRR",
    "whole_system_rr": "VM-RR",
}

PALETTE = {
    "baseline": (0.2980392156862745, 0.4470588235294118, 0.6901960784313725),
    "kernel_rr": (0.3333333333333333, 0.6588235294117647, 0.40784313725490196),
    "whole_system_rr": "salmon",
}


def million_formatter(x, pos):
    return f'{x / 1e6}'

def draw_subgraph(workload, ax_pair, enable_label=False):
    rocksdb_df_filepath = osp.join(RAW_DATA_DIR, f"rocksdb-{workload}-opsps.csv")
    rocksdb_df = pandas.read_csv(rocksdb_df_filepath)
    rocksdb_df["rocksdb"] = "original"

    spdk_df_filepath = osp.join(RAW_DATA_DIR, f"rocksdb_kernel_bypass-{workload}-opsps.csv")
    spdk_df = pandas.read_csv(spdk_df_filepath)
    spdk_df["rocksdb"] = "spdk"

    rawdata_df = pandas.concat([rocksdb_df, spdk_df])
    assert len(NUMCPU_LIST) == 1
    rawdata_df = rawdata_df[rawdata_df["cores"] == NUMCPU_LIST[0]]

    throughput_data_df = pandas.DataFrame({"rocksdb" : [], "mode": [], "value": []})
    # get the throughput data
    for rocksdb in ROCKSDB_DICT:
        for mode in MODE_DICT:
            trialdata_df = rawdata_df[(rawdata_df["mode"] == mode) & (rawdata_df["rocksdb"] == rocksdb)]
            # get the mean value
            value = trialdata_df["value"].mean()
            row = [rocksdb, mode, value]
            throughput_data_df.loc[len(throughput_data_df)] = row
    print(throughput_data_df)

    # get the overhead data
    overhead_data_df = pandas.DataFrame({"rocksdb" : [], "mode": [], "value": []})
    for rocksdb in ROCKSDB_DICT:
        for mode in MODE_DICT:
            if mode == "baseline":
                continue
            this_mode_throughput = throughput_data_df[(throughput_data_df["mode"] == mode) & (throughput_data_df["rocksdb"] == rocksdb)]["value"]
            baseline_throughput = throughput_data_df[(throughput_data_df["mode"] == "baseline") & (throughput_data_df["rocksdb"] == rocksdb)]["value"]
            assert len(this_mode_throughput) == 1
            assert len(baseline_throughput) == 1
            this_mode_throughput = this_mode_throughput.iloc[0]
            baseline_throughput = baseline_throughput.iloc[0]
            overhead = baseline_throughput / this_mode_throughput
            row = [rocksdb, mode, overhead]
            overhead_data_df.loc[len(overhead_data_df)] = row

    print(overhead_data_df)
    ax1 = ax_pair[0]
    ax2 = ax_pair[1]

    # draw the lineplot to show the throughput
    seaborn.barplot(x="rocksdb", y="value", hue="mode", \
                    palette=PALETTE, \
                    width=0.5, \
                    data=throughput_data_df, ax=ax1)
    ax1.set_ylim(bottom=0)
    #ax1.set_xticks([str(num_cpu) for num_cpu in NUMCPU_LIST])
    xticks = [ROCKSDB_DICT[rocksdb] for rocksdb in ROCKSDB_DICT]
    ax2.set_xticklabels(xticks)
    ax1.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax1.yaxis.set_major_locator(MaxNLocator(4))
    ax1.yaxis.set_major_formatter(FuncFormatter(million_formatter))
    ax1.get_legend().remove()
    ax1.grid(True, color='gray', alpha=0.25)

    # draw the barplot to show the overhead
    seaborn.barplot(x="rocksdb", y="value", hue="mode", \
                    palette=PALETTE, \
                    width=0.5, \
                    data=overhead_data_df, ax=ax2)

    max_height = max([p.get_height() for p in ax2.patches])
    ax2.set_ylim(0, max_height * 1.7)

    for p in ax2.containers[0].patches:
        height = p.get_height()
        label = f'{height:.2f}'
        ax2.text(p.get_x() + p.get_width(), max_height * 1.06, label, ha="center", size=10, color=PALETTE["kernel_rr"])

    for p in ax2.containers[1].patches:
        height = p.get_height()
        label = f'{height:.2f}'
        ax2.text(p.get_x(), max_height * 1.38, label, ha="center", size=10, color=PALETTE["whole_system_rr"])

    workload_description = WORKLOAD_DICT[workload]
    if enable_label is True:
        ax1.set_ylabel("Throughput\n(10e6 ops/s)", fontsize=14)
        ax2.set_ylabel('Slowdown\n(times)', fontsize=14)
    else:
        ax1.set_ylabel("")
        ax1.set_xlabel("")
        ax2.set_ylabel("")
    ax2.set_xlabel(f"\n{workload_description}")

    ax2.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax2.yaxis.set_major_locator(MaxNLocator(4))

    ax2.get_legend().remove()
    ax2.grid(True, color='gray', alpha=0.25)


def draw_graph():
    num_plots = len(WORKLOAD_DICT)
    fig, ax_pair_list = plt.subplots(2, num_plots, figsize=(1.9 * num_plots, 2.6), \
                        gridspec_kw = {'height_ratios':[1.6, 1]}, \
                        sharex=True)

    workload_list = list(WORKLOAD_DICT.keys())
    for idx in range(num_plots):
        workload = workload_list[idx]
        ax1 = ax_pair_list[0][idx]
        ax2 = ax_pair_list[1][idx]
        ax_pair = [ax1, ax2]
        if idx == 0:
            draw_subgraph(workload, ax_pair, enable_label=True)
        else:
            draw_subgraph(workload, ax_pair)

    handles, labels = ax_pair_list[0][-1].get_legend_handles_labels()
    new_labels = []
    for label in labels:
        new_labels.append(MODE_DICT[label])
    fig.legend(handles, new_labels, loc='upper center', ncol=len(labels), bbox_to_anchor=(0.5, 1.08), frameon=True)

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.1)
    filename = "spdk-study.pdf"
    plt.savefig(filename, bbox_inches='tight')
    print("Graph is generated as {}".format(filename))

draw_graph()
