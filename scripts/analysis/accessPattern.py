"""
plot access pattern of sampled objects 
this can be used to visualize how objects get accessed 

"""

import os, sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "../"))
from utils.common import *
FIG_TYPE = "pdf"

def _get_num_of_lines(datapath):
    """ get number of lines in a file """
    ifile = open(datapath)
    num_of_lines = 0
    for _ in ifile:
        num_of_lines += 1
    ifile.close()

    return num_of_lines


def _load_access_pattern_data(datapath, n_obj):
    """ load access pattern plot data from C++ computation """

    n_total_obj = _get_num_of_lines(datapath) - 2
    # skip the first 20% popular objects 
    # n_total_obj = int(n_total_obj * 0.8)
    sample_ratio = max(1, n_total_obj // n_obj)
    print("access pattern: sample ratio {}//{} = {}".format(
        n_total_obj, n_obj, sample_ratio))

    if n_total_obj / sample_ratio > 10000:
        print(
            "access pattern: too many objects to plot, try to use --n_obj to reduce the number of objects, a reasonable number is 500"
        )

    ifile = open(datapath)
    data_line = ifile.readline()
    desc_line = data_line + ifile.readline()
    assert "# access pattern " in desc_line, "the input file might not be accessPattern data file" + "data " + datapath
    access_time_list = []

    # for _ in range(int(n_total_obj * 0.2)):
    #     ifile.readline() 
               
    n_line = 0
    for line in ifile:
        n_line += 1
        if len(line.strip()) == 0:
            continue
        elif n_line % sample_ratio == 0:
            access_time_list.append([float(i) for i in line.split(",")[:-1]])

    ifile.close()

    access_time_list.sort(key=lambda x: x[0])

    return access_time_list


def plot_access_pattern(datapath, n_obj=2000, figname_prefix=""):
    """
    plot access patterns 

    """

    if len(figname_prefix) == 0:
        figname_prefix = datapath.split("/")[-1]

    access_time_list = _load_access_pattern_data(datapath, n_obj)

    is_real_time = "Rtime" in datapath
    if is_real_time:
        xlabel = "Time (hour)"
        figname = "fig/{}_access_rt.{}".format(figname_prefix, FIG_TYPE)
        for idx, ts_list in enumerate(access_time_list):
            # access_rtime_list stores N objects, each object has one access pattern list
            plt.scatter([ts / 3600 for ts in ts_list],
                        [idx for _ in range(len(ts_list))], s=8)

    else:
        assert "Vtime" in datapath, "the input file might not be accessPattern data file"
        xlabel = "Time (# million requests)"
        figname = "fig/{}_access_vt.{}".format(figname_prefix, FIG_TYPE)
        for idx, ts_list in enumerate(access_time_list):
            # access_rtime_list stores N objects, each object has one access pattern list
            plt.scatter([ts / 1e6 for ts in ts_list],
                        [idx for _ in range(len(ts_list))], s=8)

    plt.xlabel(xlabel)
    plt.ylabel("Sampled object")
    plt.savefig(figname, bbox_inches="tight")
    plt.clf()


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("datapath", type=str, help="data path")
    ap.add_argument("--n_obj",
                    type=int,
                    default=400,
                    help="the number of objects to plot")
    ap.add_argument("--figname_prefix",
                    type=str,
                    default="",
                    help="the prefix of figname")
    p = ap.parse_args()

    plot_access_pattern(p.datapath, p.n_obj, p.figname_prefix)