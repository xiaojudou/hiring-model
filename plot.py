import contextlib
import numpy
import random
from matplotlib import pyplot

pyplot.style.use('seaborn-whitegrid')
pyplot.rcParams.update({'font.size': 15})


@contextlib.contextmanager
def gfx_setup(filename, xlabel='Ability with thing A', ylabel='Ability with thing B'):
    fig, axes = pyplot.subplots(2, 2, sharex='col', sharey='row',
                                gridspec_kw={'width_ratios': [7, 1],
                                             'height_ratios': [1, 7],
                                             'wspace': 0,
                                             'hspace': 0})
    for i, j in [(0, 0), (0, 1), (1, 1)]:
        axes[i][j].axis('off')
    ax = axes[1][0]
    fig.set_size_inches(7, 7)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_aspect('equal', 'box')
    ax.set_xticks(range(-3, 4))
    ax.set_yticks(range(-3, 4))
    ax.grid(which='major', alpha=0.2)
    ax.tick_params(colors=(0, 0, 0, 0.2), labelsize='small')
    yield fig, axes
    ax.set_xlim([-4, 4])
    ax.set_ylim([-4, 4])
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right', frameon=True, facecolor='white', bbox_to_anchor=(1, 1))
    # fig.tight_layout()
    fig.savefig(filename)


xs = [random.gauss(0, 1) for i in range(5000)]
ys = [random.gauss(0, 1) for i in range(5000)]

def scatter(axes, fn, color, label):
    axes[1][0].scatter([], [], color=color, label=label)  # just for label
    axes[1][0].scatter([x for x, y in zip(xs, ys) if fn(x, y)],
                       [y for x, y in zip(xs, ys) if fn(x, y)],
                       alpha=0.1, color=color, edgecolors='none')
    hist_bins = numpy.arange(-4, 4, 0.25)
    axes[0][0].hist([x for x, y in zip(xs, ys) if fn(x, y)],
                    bins=hist_bins, alpha=0.3, color=color, density=True)
    axes[1][1].hist([y for x, y in zip(xs, ys) if fn(x, y)],
                    bins=hist_bins, alpha=0.3, color=color, density=True, orientation='horizontal')

with gfx_setup('plot.png') as (fig, axes):
    scatter(axes, lambda x, y: True,
            color='b', label='Candidates we consider')

with gfx_setup('plot2.png') as (fig, axes):
    scatter(axes, lambda x, y: x+y > 0.5,
            color='g', label='Candidates we bring in')
    scatter(axes, lambda x, y: x+y <= 0.5,
            color='r', label='Candidates we do not bring in')

with gfx_setup('plot3.png') as (fig, axes):
    scatter(axes, lambda x, y: x+y > 1.5,
            color=(1, 0.5, 0), label='Candidates that do not want to talk to us')
    scatter(axes, lambda x, y: 0.5 < x+y <= 1.5,
            color='g', label='Candidates we bring in')
    scatter(axes, lambda x, y: x+y <= 0.5,
            color='r', label='Candidates we do not bring in')

with gfx_setup('plot_confidence.png', xlabel='Competence', ylabel='Confidence') as (fig, axes):
    scatter(axes, lambda x, y: x+y > 1.5,
            color=(1, 0.5, 0), label='Candidates that do not want to talk to us')
    scatter(axes, lambda x, y: 1 < x and x+y <= 1.5,
            color='g', label='Candidates we bring in')
    scatter(axes, lambda x, y: x <= 1 and x+y <= 1.5,
            color='r', label='Candidates we do not bring in')

with gfx_setup('plot_fancy_school.png', xlabel='Did well on coding test', ylabel='Went to fancy school') as (fig, axes):
    scatter(axes, lambda x, y: x+y > 1.5,
            color=(1, 0.5, 0), label='Candidates that do not want to talk to us')
    scatter(axes, lambda x, y: 2 < 2*x+y and x+y <= 1.5,
            color='g', label='Candidates we bring in')
    scatter(axes, lambda x, y: 2*x+y <= 2 and x+y <= 1.5,
            color='r', label='Candidates we do not bring in')

def split_by_exp_model(our_kx, our_ky, market_kx=1, market_ky=1):
    func = lambda x, y: numpy.log(numpy.exp(our_kx*x + our_ky*y) / (1 + numpy.exp(market_kx*x + market_ky*y)))
    vs_sorted = sorted(func(x, y) for x, y in zip(xs, ys))
    thresh_lo, thresh_hi = vs_sorted[len(vs_sorted)//3], vs_sorted[len(vs_sorted)*2//3]
    return (lambda x, y: func(x, y) < thresh_lo,
            lambda x, y: thresh_lo <= func(x, y) < thresh_hi,
            lambda x, y: thresh_hi <= func(x, y))

for our_kx, our_ky in [(1, 0), (1, 0.5), (0.75, 0.75), (2, 2)]:
    fn = 'exp_model_%.2f_%.2f.png' % (our_kx, our_ky)
    with gfx_setup(fn) as (fig, axes):
        bucket_1_f, bucket_2_f, bucket_3_f = split_by_exp_model(our_kx, our_ky)
        scatter(axes, bucket_1_f, color=(1, 0, 0), label='Worst 3rd')
        scatter(axes, bucket_2_f, color=(0.5, 0, 0.5), label='Mid 3rd')
        scatter(axes, bucket_3_f, color=(0, 0, 1), label='Top 3rd')
        pad_f = 0.9
        axes[1][0].arrow(0, 0, 1*pad_f, 1*pad_f, head_width=0.4, head_length=0.4, width=0.1, ec='none', fc=(0, 0.7, 0), alpha=0.7)
        axes[1][0].arrow(0, 0, our_kx*pad_f, our_ky*pad_f, head_width=0.4, head_length=0.4, width=0.1, ec='none', fc=(1, 0.5, 0), alpha=0.7)
        axes[1][0].text(1, 1, 'Market', color=(0, 0.7, 0), va='bottom')
        axes[1][0].text(our_kx, our_ky, 'We hire', color=(1, 0.5, 0), va='bottom')
        fig.suptitle('Market vector = (%.2f, %.2f)\nOur vector = (%.2f, %.2f)' % (1, 1, our_kx, our_ky))
