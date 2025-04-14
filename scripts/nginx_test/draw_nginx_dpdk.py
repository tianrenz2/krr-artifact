import os
import os.path as osp
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import AutoMinorLocator
import pandas
import seaborn


RAW_DATA_DIR = "../../test_data/nginx-dpdk/v3"
NUMCPU_LIST = [1, 2, 4, 8, 16, 32]
MODE_DICT = {
    "native": "Native",
    "krr": "KRR",
}

TEST_DICT = {
    "1k" : "a",
    "4k" : "b",
    "16k" : "c",
    "64k" : "d",
}

PALETTE = {
    "native": (0.2980392156862745, 0.4470588235294118, 0.6901960784313725),
    "krr": (0.3333333333333333, 0.6588235294117647, 0.40784313725490196),
    "whole_system_rr": "salmon",
}

HEIGHT = 5
WIDTH = 4

def draw_subgraph(test, save_dirpath):
    time_df_filepath = osp.join(RAW_DATA_DIR, "nginx-test-{}.csv".format(test))
    graphdata_df = pandas.read_csv(time_df_filepath)

    rawdata_df = graphdata_df

    timetaken_data_df = pandas.DataFrame({"cores": [], "mode": [], "req/sec": []})
    timetaken_divide_data_df = pandas.DataFrame({"cores": [], "mode": [], "req/sec": []})
    for mode in MODE_DICT:
        for num_cpu in NUMCPU_LIST:
            trialdata_df = rawdata_df[(rawdata_df["mode"] == mode) & (rawdata_df["cores"] == num_cpu)]
            # get the mean value
            value = trialdata_df["req/sec"].mean()
            row = [num_cpu, mode, value]
            row_divide = [num_cpu, mode, value / 1000]
            timetaken_data_df.loc[len(timetaken_data_df)] = row
            timetaken_divide_data_df.loc[len(timetaken_divide_data_df)] = row_divide

    slowdown_data_df = pandas.DataFrame({"cores": [], "mode": [], "value": []})
    for mode in MODE_DICT:
        if mode == "native":
            continue
        for num_cpu in NUMCPU_LIST:
            trialdata_df = rawdata_df[(graphdata_df["mode"] == mode) & (graphdata_df["cores"] == num_cpu)]
            this_mode_time = timetaken_data_df[(timetaken_data_df["mode"] == mode) & (timetaken_data_df["cores"] == num_cpu)]["req/sec"]
            baseline_time = timetaken_data_df[(timetaken_data_df["mode"] == "native") & (timetaken_data_df["cores"] == num_cpu)]["req/sec"]
            assert len(this_mode_time) == 1
            assert len(baseline_time) == 1
            this_mode_time = this_mode_time.iloc[0]
            baseline_time = baseline_time.iloc[0]
            #overhead = (this_mode_time - baseline_time) / baseline_time
            overhead = baseline_time / this_mode_time
            row = [num_cpu, mode, overhead]
            slowdown_data_df.loc[len(slowdown_data_df)] = row

    timetaken_data_df['cores'] = timetaken_data_df['cores'].astype(str)
    slowdown_data_df['cores'] = slowdown_data_df['cores'].astype(str)
    timetaken_divide_data_df['cores'] = timetaken_divide_data_df['cores'].astype(str)

    _, ax_pair = plt.subplots(2, 1, figsize=(WIDTH, HEIGHT), \
                        gridspec_kw = {'height_ratios':[1, 1]}, \
                        sharex=True)

    ax1 = ax_pair[0]
    ax2 = ax_pair[1]
    ax1.clear()
    ax2.clear()

    seaborn.barplot(x="cores", y="req/sec", hue="mode", \
            palette=PALETTE, \
            data=timetaken_divide_data_df, ax=ax1)
    ax1.set_ylim(bottom=0)
    ax1.set_xticks([str(num_cpu) for num_cpu in NUMCPU_LIST])
    ax1.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax1.yaxis.set_major_locator(MaxNLocator(4))
    #ax1.yaxis.set_major_formatter(FuncFormatter(million_formatter))
    ax1.grid(True, color='gray', alpha=0.25)
    ax1.set_ylabel("RPS\n(10e3 req/sec)", fontsize=16)

    # draw the barplot to show the overhead
    g = seaborn.barplot(x="cores", y="value", hue="mode", \
                    palette=PALETTE, \
                    width=0.5, \
                    data=slowdown_data_df, ax=ax2)
    ax2.set_ylabel('Slowdown\n(times)', fontsize=16)
    ax2.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax2.yaxis.set_major_locator(MaxNLocator(5))

    max_height = max([p.get_height() for p in ax2.patches])
    ax2.set_ylim(0, max_height * 1.25)

    for p in ax2.containers[0].patches:
        height = p.get_height()
        label = f'{height:.2f}'
        ax2.text(p.get_x() + p.get_width() / 2, p.get_height() * 1.1, label, ha="center", size=10, color=PALETTE["krr"])

    # for p in ax2.containers[1].patches:
    #     height = p.get_height()
    #     label = f'{height:.2f}'
    #     ax2.text(p.get_x(), max_height * 1.38, label, ha="center", size=10, color=PALETTE["whole_system_rr"])

    ax2.get_legend().remove()
    ax2.grid(True, color='gray', alpha=0.25)

    ax1.set_xlabel("")
    ax2.set_xlabel("Num. of Cores", fontsize=16)

    handles, labels = ax1.get_legend_handles_labels()
    new_labels = []
    for label in labels:
        new_labels.append(MODE_DICT[label])
    ax1.legend(handles, new_labels, loc='lower left')

    save_filepath = osp.join(save_dirpath, f"nginx-dpdk-{test}.pdf")
    print("Save to {}".format(save_filepath))
    plt.tight_layout(pad = 0.0)
    plt.subplots_adjust(hspace=0.1)
    plt.savefig(save_filepath)


def draw_graph():
    result_dirpath = "./nginx-graph"
    os.makedirs(result_dirpath, exist_ok=True)

    for test in TEST_DICT:
        draw_subgraph(test, result_dirpath)

draw_graph()
