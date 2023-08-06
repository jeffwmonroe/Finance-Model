from itertools import compress
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib import ticker
import numpy as np
import base64
from io import BytesIO


def plot_lines(ax, date_axis, data):
    for col in data.columns:
        ax.plot(date_axis, data[col], label=col)

    ax.legend()


def combo_legend(ax):
    handler, labeler = ax.get_legend_handles_labels()
    hd = []
    labli = list(set(labeler))
    for lab in labli:
        comb = [h for h, l in zip(handler, labeler) if l == lab]
        hd.append(tuple(comb))
    return hd, labli


def plot_bars(ax, date_axis, data):
    print('-' * 50)
    width = 0.8
    pos_bottom = np.zeros(len(date_axis))
    neg_bottom = np.zeros(len(date_axis))
    prop = ax._get_lines.prop_cycler
    for col in data.columns:
        color = next(prop)['color']
        values = data[col]
        prows = data[col] > 0
        pvalues = values.copy()
        pvalues[~prows] = 0
        ax.bar(date_axis, pvalues, width, label=col, bottom=pos_bottom, color=color)
        pos_bottom += pvalues

        nvalues = values.copy()
        nvalues[prows] = 0
        ax.bar(date_axis, nvalues, width, label=col, bottom=neg_bottom, color=color)
        neg_bottom += nvalues
    hd, lab = combo_legend(ax)
    ax.legend(hd, lab)


def finance_plot(data, title, binary=False, yearly=True):
    figsize = (10, 10)
    if binary:
        fig = Figure(figsize=figsize)
        ax = fig.subplots()
    else:
        fig, ax = plt.subplots(figsize=figsize, layout='constrained')

    if yearly:
        ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
        date_axis = [pd.to_datetime(dt).strftime('%b-%Y') for dt in data.index]
    else:
        ax.xaxis.set_major_locator(ticker.MultipleLocator(6))
        date_axis = [pd.to_datetime(dt).strftime('%m-%y') for dt in data.index]
    plot_bars(ax, date_axis, data)
    # plot_lines(ax, date_axis, data)

    # ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 7)))
    # ax.xaxis.set_minor_locator(mdates.MonthLocator())
    # ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b'))
    # Rotates and right-aligns the x labels so they don't crowd each other.
    for label in ax.get_xticklabels(which='major'):
        label.set(rotation=30, horizontalalignment='right')
    ax.set_xlabel("time")
    ax.set_ylabel("height")
    ax.set_title(title)
    # ax.legend()

    if binary:
        # Save it to a temporary buffer.
        buf = BytesIO()
        fig.savefig(buf, format="png")
        # Embed the result in the html output.
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return data
    else:
        plt.show()
        return None
