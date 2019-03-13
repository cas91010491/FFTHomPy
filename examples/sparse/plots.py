import pickle
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
from fig_pars import set_labels,set_pars

os.nice(19)

material_list = pickle.load(open("data_for_plot/material_list.p", "rb"))
sol_rank_range_set = pickle.load(open("data_for_plot/sol_rank_range_set.p", "rb"))
kinds = pickle.load(open("data_for_plot/kinds.p", "rb"))
Ns = pickle.load(open("data_for_plot/Ns.p", "rb"))
kind_list = pickle.load(open("data_for_plot/kind_list.p", "rb"))
solver ='mr'


def plot_error():
    ylimit = [10 ** -11, 10 ** 0]
    xlabel ='rank of solution'
    ylabel='norm of relative error'
    iter_rank_range_set=[1,5,10,15,20,30,40,50]


    for dim in [2]:
        N = max(Ns['{}'.format(dim)])
        xlimend = max(sol_rank_range_set['{}'.format(dim)])
        if not os.path.exists('figures'):
            os.makedirs('figures')

        ##### BEGIN: figure 1 resiguum(solution rank) ###########
        for material in material_list:
            parf=set_pars(mpl)
            lines,labels=set_labels()
            src='figures/' # source folder\
            plt.figure(num=None, figsize=parf['figsize'], dpi=parf['dpi'])
            plt.ylabel('relative error')
            plt.xlabel('rank of solution')

            sol_rank_range = sol_rank_range_set['{}'.format(dim)]
            i=0
            for kind in kinds['{}'.format(dim)]:

                sols_Ga        =   pickle.load(open( "data_for_plot/dim_{}/mat_{}/sols_Ga_{}.p".format(dim,material,N) , "rb"))
                sols_GaNi      =   pickle.load(open( "data_for_plot/dim_{}/mat_{}/sols_GaNi_{}.p".format(dim, material,N), "rb"))
                sols_Ga_Spar   =   pickle.load(open( "data_for_plot/dim_{}/mat_{}/sols_Ga_Spar_{}_{}_{}.p".format(dim,material,kind,N,solver), "rb"  ) )
                sols_GaNi_Spar =   pickle.load(open( "data_for_plot/dim_{}/mat_{}/sols_GaNi_Spar_{}_{}_{}.p".format(dim,material,kind,N,solver), "rb"  ) )

                plt.hold(True)
                plt.semilogy(sol_rank_range,[abs((sols_Ga_Spar[i]  -sols_Ga[1])  /sols_Ga[1])   for i in range(len(sols_Ga_Spar))], lines['Ga_{}'.format(kind_list[kind])][i],   label=labels['Ga{}'.format(kind_list[kind])] , markevery=1)
                plt.semilogy(sol_rank_range,[abs((sols_GaNi_Spar[i]-sols_GaNi[1])/sols_GaNi[1]) for i in range(len(sols_GaNi_Spar))],lines['GaNi_{}'.format(kind_list[kind])][i], label=labels['GaNi{}'.format(kind_list[kind])], markevery=1, markersize=7,markeredgewidth=1,markerfacecolor='None')
                i=i+1


            ax = plt.gca()
            plt.xlabel(xlabel)
            ax.set_xlim([0,xlimend])
            plt.xticks(sol_rank_range)

            plt.ylabel(ylabel)

            lg=plt.legend(loc='best')
            fname=src+'Error_dim{}_mat{}_{}{}'.format(dim,material,solver,'.pdf')
            print('create figure: {}'.format(fname))
            plt.savefig(fname, dpi=parf['dpi'], pad_inches=parf['pad_inches'], bbox_inches='tight')
        print('END plot errors')
        ##### END: figure 1 resiguum(solution rank) ###########


    for dim in [3]:
        N = max(Ns['{}'.format(dim)])
        xlimend = max(sol_rank_range_set['{}'.format(dim)])
        if not os.path.exists('figures'):
            os.makedirs('figures')

        ##### BEGIN: figure 1 resiguum(solution rank) ###########
        for material in material_list:
            parf=set_pars(mpl)
            lines,labels=set_labels()
            src='figures/' # source folder\
            plt.figure(num=None, figsize=parf['figsize'], dpi=parf['dpi'])

            sol_rank_range = sol_rank_range_set['{}'.format(dim)]


            for kind in kinds['{}'.format(dim)]:

                sols_Ga        =   pickle.load(open( "data_for_plot/dim_{}/mat_{}/sols_Ga_{}.p".format(dim,material,N) , "rb"))
                sols_GaNi      =   pickle.load(open( "data_for_plot/dim_{}/mat_{}/sols_GaNi_{}.p".format(dim, material,N), "rb"))
                sols_Ga_Spar   =   pickle.load(open( "data_for_plot/dim_{}/mat_{}/sols_Ga_Spar_{}_{}_{}.p".format(dim,material,kind,N,solver), "rb"  ) )
                sols_GaNi_Spar =   pickle.load(open( "data_for_plot/dim_{}/mat_{}/sols_GaNi_Spar_{}_{}_{}.p".format(dim,material,kind,N,solver), "rb"  ) )

                plt.hold(True)
                plt.semilogy(sol_rank_range,[abs((sols_Ga_Spar[i]  -sols_Ga[1])  /sols_Ga[1])   for i in range(len(sols_Ga_Spar))], lines['Ga_{}'.format(kind_list[kind])][i],   label=labels['Ga{}'.format(kind_list[kind])] , markevery=1)
                plt.semilogy(sol_rank_range,[abs((sols_GaNi_Spar[i]-sols_GaNi[1])/sols_GaNi[1]) for i in range(len(sols_Ga_Spar))], lines['GaNi_{}'.format(kind_list[kind])][i], label=labels['GaNi{}'.format(kind_list[kind])], markevery=1, markersize=7,markeredgewidth=1,markerfacecolor='None')

            ax = plt.gca()
            plt.xlabel(xlabel)
            ax.set_xlim([0,xlimend])
            plt.xticks(sol_rank_range)

            plt.ylabel(ylabel)

            lg=plt.legend(loc='best')
            fname=src+'Error_dim{}_mat{}_{}{}'.format(dim,material,solver,'.pdf')
            print('create figure: {}'.format(fname))
            plt.savefig(fname, dpi=parf['dpi'], pad_inches=parf['pad_inches'], bbox_inches='tight')
        print('END plot errors')
        ##### END: figure 1 resiguum(solution rank) ###########

def plot_memory():
    #ylimit = [10 ** -7, 10 ** -1]
    xlabel = 'rank of solution'
    ylabel = 'memory efficiency'
    if not os.path.exists('figures'):
        os.makedirs('figures')
    for dim in [2]:
        sol_rank_range = sol_rank_range_set['{}'.format(dim)]
        N = max(Ns['{}'.format(dim)])
        xlimend = max(sol_rank_range_set['{}'.format(dim)])
        ##### BEGIN: figure 2 Memory efficiency ###########
        for material in material_list:

            parf = set_pars(mpl)
            lines, labels = set_labels()
            src = 'figures/'  # source folder\
            plt.figure(num=None, figsize=parf['figsize'], dpi=parf['dpi'])

            mem_GaNi = pickle.load(open("data_for_plot/dim_{}/mat_{}/mem_GaNi_{}.p".format(dim, material, N, ), "rb"))

            plt.semilogy(sol_rank_range, mem_GaNi, lines['full'],
                         label=labels['GaNi{}'.format(('full'))], markevery=1, markersize=7, markeredgewidth=1,
                         markerfacecolor='None')

            for N in Ns['{}'.format(dim)]:
                i = 0
                for kind in kinds['{}'.format(dim)]:
                    mem_GaNi_Spar = pickle.load(open(
                        "data_for_plot/dim_{}/mat_{}/mem_GaNi_Spar_{}_{}_{}.p".format(dim, material, kind, N, solver),
                        "rb"))
                    plt.semilogy(sol_rank_range, mem_GaNi_Spar, lines['mem_{}'.format(kind_list[kind])][i],
                                 label='{}{}'.format(labels['GaNi{}N'.format(kind_list[kind])], N), markevery=1,
                                 markersize=7, markeredgewidth=1, markerfacecolor='None')
                    plt.hold(True)
                    i = i + 1

            ax = plt.gca()
            plt.xticks(sol_rank_range)
            plt.xlabel(xlabel)
            ax.set_xlim([0, xlimend])

            plt.ylabel(ylabel)

            lg = plt.legend(loc='best')
            fname = src + 'Memory_dim{}_mat{}{}'.format(dim, material, '.pdf')
            print('create figure: {}'.format(fname))
            plt.savefig(fname, dpi=parf['dpi'], pad_inches=parf['pad_inches'], bbox_inches='tight')
        print('END plot memory')
        ##### END: figure 2 memory ###########

    for dim in [3]:
        sol_rank_range = sol_rank_range_set['{}'.format(dim)]
        N = max(Ns['{}'.format(dim)])
        xlimend = max(sol_rank_range_set['{}'.format(dim)])
        ##### BEGIN: figure 2 Memory efficiency ###########
        for material in material_list:

            plt.figure(num=None, figsize=parf['figsize'], dpi=parf['dpi'])

            mem_GaNi = pickle.load(open("data_for_plot/dim_{}/mat_{}/mem_GaNi_{}.p".format(dim, material, N), "rb"))

            plt.semilogy(sol_rank_range, mem_GaNi, lines['full'],
                         label=labels['GaNi{}'.format(('full'))],
                         markevery=1, markersize=7, markeredgewidth=1, markerfacecolor='None')

            for kind in kinds['{}'.format(dim)]:
                i = 0
                for N in [max(Ns['{}'.format(dim)]), min(Ns['{}'.format(dim)])]:
                    mem_GaNi_Spar = pickle.load(open(
                        "data_for_plot/dim_{}/mat_{}/mem_GaNi_Spar_{}_{}_{}.p".format(dim, material, kind, N, solver),
                        "rb"))
                    plt.semilogy(sol_rank_range, mem_GaNi_Spar, lines['mem_{}'.format(kind_list[kind])][i],
                                 label='{}{}'.format(labels['GaNi{}N'.format(kind_list[kind])], N), markevery=1,
                                 markersize=7, markeredgewidth=1, markerfacecolor='None')
                    plt.hold(True)
                    i = i + 1

            ax = plt.gca()
            plt.xticks(sol_rank_range)
            plt.xlabel(xlabel)
            ax.set_xlim([0, xlimend])

            plt.ylabel(ylabel)

            lg = plt.legend(loc='best')
            fname = src + 'Memory_dim{}_mat{}{}'.format(dim, material, '.pdf')
            print('create figure: {}'.format(fname))
            plt.savefig(fname, dpi=parf['dpi'], pad_inches=parf['pad_inches'], bbox_inches='tight')
        print('END plot memory')
        ##### END: figure 2 memory ###########

def plot_residuals():
    xlimit = [0, 20]
    ylimit = [10 ** -7, 10 ** -1]
    xlabel = 'iteration'
    ylabel = 'norm of residuum'
    iter_rank_range_set = [1, 5, 10, 15, 20, 30, 40, 50]
    if not os.path.exists('figures'):
        os.makedirs('figures')

    for dim in [2]:

        for N in Ns['{}'.format(dim)]:

            ##### BEGIN: figure 5.1 Residuum for GA solution ###########
            for material in material_list:
                for kind in kinds['{}'.format(dim)]:
                    # plt.figure(1).clear()
                    parf = set_pars(mpl)
                    lines, labels = set_labels()
                    src = 'figures/'  # source folder\
                    sol_rank_range = sol_rank_range_set['{}'.format(dim)]
                    plt.figure(num=None, figsize=parf['figsize'], dpi=parf['dpi'])
                    plt.hold(True)

                    res_Ga_Spar = pickle.load(open(
                        "data_for_plot/dim_{}/mat_{}/res_Ga_Spar_{}_{}_{}.p".format(dim, material, kind, N, solver),
                        "rb"))

                    for sol_rank in range(0, len(sol_rank_range)):
                        plt.semilogy(range(len(res_Ga_Spar[sol_rank])), res_Ga_Spar[sol_rank],
                                     lines['Ga'][sol_rank],
                                     label='{} {}'.format(labels['Garank'], sol_rank_range[sol_rank]), markevery=2)

                    ax = plt.gca()
                    plt.xticks(iter_rank_range_set)
                    plt.xlabel(xlabel)
                    ax.set_xlim(xlimit)

                    plt.ylabel(ylabel)
                    ax.set_ylim(ylimit)

                    lg = plt.legend(loc='upper right')
                    fname = src + 'Residuum_dim{}_mat{}_kind_{}_Ga_{}_N{}{}'.format(dim, material, kind_list[kind],
                                                                                    solver, N, '.pdf')
                    print('create figure: {}'.format(fname))
                    plt.savefig(fname, dpi=parf['dpi'], pad_inches=parf['pad_inches'], bbox_inches='tight')
            print('END Ga residuum')
            ##### END: figure 5.1 Residuum for Ga solution ###########

            ##### BEGIN: figure 5.2 Residuum for GaNi solution ###########
            for material in material_list:

                for kind in kinds['{}'.format(dim)]:

                    parf = set_pars(mpl)
                    lines, labels = set_labels()
                    src = 'figures/'  # source folder\
                    sol_rank_range = sol_rank_range_set['{}'.format(dim)]

                    plt.figure(num=None, figsize=parf['figsize'], dpi=parf['dpi'])
                    plt.hold(True)

                    res_GaNi_Spar = pickle.load(
                        open("data_for_plot/dim_{}/mat_{}/res_GaNi_Spar_{}_{}_{}.p".format(dim, material, kind, N,
                                                                                           solver), "rb"))

                    plt.xticks(iter_rank_range_set)
                    for sol_rank in range(0, len(sol_rank_range)):
                        plt.semilogy(range(len(res_GaNi_Spar[sol_rank])), res_GaNi_Spar[sol_rank],
                                     lines['GaNi'][sol_rank],
                                     label='{} {}'.format(labels['GaNirank'], sol_rank_range[sol_rank]), markevery=2,
                                     markersize=7,
                                     markeredgewidth=1, markerfacecolor='None')

                    ax = plt.gca()
                    plt.xticks(iter_rank_range_set)
                    plt.xlabel(xlabel)
                    ax.set_xlim(xlimit)

                    plt.ylabel(ylabel)
                    ax.set_ylim(ylimit)

                    lg = plt.legend(loc='upper right')

                    fname = src + 'Residuum_dim{}_mat{}_kind_{}_GaNi_{}_N{}{}'.format(dim, material, kind_list[kind],
                                                                                      solver, N, '.pdf')
                    print('create figure: {}'.format(fname))
                    plt.savefig(fname, dpi=parf['dpi'], pad_inches=parf['pad_inches'], bbox_inches='tight')
            print('END Ga residuum')
            ##### END: figure 5.2 Residuum for GaNi solution ###########

    for dim in [3]:

        for N in Ns['{}'.format(dim)]:

            ##### 0 material  ###########
            for material in [0]:
                for kind in kinds['{}'.format(dim)]:
                    parf = set_pars(mpl)
                    lines, labels = set_labels()
                    src = 'figures/'  # source folder\
                    sol_rank_range = sol_rank_range_set['{}'.format(dim)]

                    plt.figure(num=None, figsize=parf['figsize'], dpi=parf['dpi'])
                    plt.hold(True)

                    res_Ga_Spar = pickle.load(
                        open(
                            "data_for_plot/dim_{}/mat_{}/res_Ga_Spar_{}_{}_{}.p".format(dim, material, kind, N, solver),
                            "rb"))

                    for sol_rank in range(0, len(
                            sol_rank_range)):  # range(len(sol_rank_range)):#range(0, len(sol_rank_range), 2)
                        plt.semilogy(range(len(res_Ga_Spar[sol_rank])), res_Ga_Spar[sol_rank],
                                     lines['Ga'][sol_rank],
                                     label='{} {}'.format(labels['Garank'], sol_rank_range[sol_rank]), markevery=2)

                    ax = plt.gca()
                    plt.xticks(iter_rank_range_set)
                    plt.xlabel(xlabel)
                    ax.set_xlim(xlimit)

                    plt.ylabel(ylabel)
                    ax.set_ylim(ylimit)

                    lg = plt.legend(loc='upper right')
                    fname = src + 'Residuum_dim{}_mat{}_kind_{}_Ga_{}_N{}{}'.format(dim, material, kind_list[kind],
                                                                                    solver, N, '.pdf')
                    print('create figure: {}'.format(fname))
                    plt.savefig(fname, dpi=parf['dpi'], pad_inches=parf['pad_inches'], bbox_inches='tight')
            print('END Ga residuum')
            ##### END: figure 5.1 Residuum for Ga solution ###########

            ##### BEGIN: figure 5.2 Residuum for GaNi solution ###########
            for material in [0]:
                for kind in kinds['{}'.format(dim)]:

                    parf = set_pars(mpl)
                    lines, labels = set_labels()
                    src = 'figures/'  # source folder\
                    sol_rank_range = sol_rank_range_set['{}'.format(dim)]

                    plt.figure(num=None, figsize=parf['figsize'], dpi=parf['dpi'])
                    plt.hold(True)

                    res_GaNi_Spar = pickle.load(
                        open("data_for_plot/dim_{}/mat_{}/res_GaNi_Spar_{}_{}_{}.p".format(dim, material, kind, N,
                                                                                           solver),
                             "rb"))

                    for sol_rank in range(0, len(sol_rank_range)):  # range(len(sol_rank_range)):
                        plt.semilogy(range(len(res_GaNi_Spar[sol_rank])), res_GaNi_Spar[sol_rank],
                                     lines['GaNi'][sol_rank],
                                     label='{} {}'.format(labels['GaNirank'], sol_rank_range[sol_rank]), markevery=2,
                                     markersize=7,
                                     markeredgewidth=1, markerfacecolor='None')
                    ax = plt.gca()
                    plt.xticks(iter_rank_range_set)
                    plt.xlabel(xlabel)
                    ax.set_xlim(xlimit)

                    plt.ylabel(ylabel)
                    ax.set_ylim(ylimit)

                    lg = plt.legend(loc='upper right')
                    fname = src + 'Residuum_dim{}_mat{}_kind_{}_GaNi_{}_N{}{}'.format(dim, material, kind_list[kind],
                                                                                      solver, N, '.pdf')
                    print('create figure: {}'.format(fname))
                    plt.savefig(fname, dpi=parf['dpi'], pad_inches=parf['pad_inches'], bbox_inches='tight')
            print('END Ga residuum')
            ##### END: figure 5.2 Residuum for GaNi solution ###########

            ##### 2 meterial    ###########
            for material in [2]:
                for kind in kinds['{}'.format(dim)]:
                    # plt.figure(1).clear()
                    parf = set_pars(mpl)
                    lines, labels = set_labels()
                    src = 'figures/'  # source folder\
                    sol_rank_range = sol_rank_range_set['{}'.format(dim)]

                    plt.figure(num=None, figsize=parf['figsize'], dpi=parf['dpi'])
                    plt.hold(True)

                    res_Ga_Spar = pickle.load(
                        open(
                            "data_for_plot/dim_{}/mat_{}/res_Ga_Spar_{}_{}_{}.p".format(dim, material, kind, N, solver),
                            "rb"))

                    for sol_rank in range(0, len(sol_rank_range)):  # range(len(sol_rank_range)):
                        plt.semilogy(range(len(res_Ga_Spar[sol_rank])), res_Ga_Spar[sol_rank],
                                     lines['Ga'][sol_rank],
                                     label='{} {}'.format(labels['Garank'], sol_rank_range[sol_rank]), markevery=2)
                    ax = plt.gca()
                    plt.xticks(iter_rank_range_set)
                    plt.xlabel(xlabel)
                    ax.set_xlim(xlimit)

                    plt.ylabel(ylabel)
                    ax.set_ylim(ylimit)

                    lg = plt.legend(loc='lower left')
                    fname = src + 'Residuum_dim{}_mat{}_kind_{}_Ga_{}_N{}{}'.format(dim, material, kind_list[kind],
                                                                                    solver, N, '.pdf')
                    print('create figure: {}'.format(fname))
                    plt.savefig(fname, dpi=parf['dpi'], pad_inches=parf['pad_inches'], bbox_inches='tight')
            print('END Ga residuum')
            ##### END: figure 5.1 Residuum for Ga solution ###########

            #### BEGIN: figure 5.2 Residuum for GaNi solution ###########
            for material in [2]:
                for kind in kinds['{}'.format(dim)]:

                    parf = set_pars(mpl)
                    lines, labels = set_labels()
                    src = 'figures/'  # source folder\
                    sol_rank_range = sol_rank_range_set['{}'.format(dim)]

                    plt.figure(num=None, figsize=parf['figsize'], dpi=parf['dpi'])
                    plt.hold(True)

                    res_GaNi_Spar = pickle.load(
                        open("data_for_plot/dim_{}/mat_{}/res_GaNi_Spar_{}_{}_{}.p".format(dim, material, kind, N,
                                                                                           solver), "rb"))

                    for sol_rank in range(0, len(sol_rank_range)):  # range(len(sol_rank_range)):
                        plt.semilogy(range(len(res_GaNi_Spar[sol_rank])), res_GaNi_Spar[sol_rank],
                                     lines['GaNi'][sol_rank],
                                     label='{} {}'.format(labels['GaNirank'], sol_rank_range[sol_rank]), markevery=2,
                                     markersize=7,
                                     markeredgewidth=1, markerfacecolor='None')
                    ax = plt.gca()
                    plt.xticks(iter_rank_range_set)
                    plt.xlabel(xlabel)
                    ax.set_xlim(xlimit)

                    plt.ylabel(ylabel)
                    ax.set_ylim(ylimit)

                    lg = plt.legend(loc='lower left')
                    fname = src + 'Residuum_dim{}_mat{}_kind_{}_GaNi_{}_N{}{}'.format(dim, material, kind_list[kind],
                                                                                      solver, N, '.pdf')
                    print('create figure: {}'.format(fname))
                    plt.savefig(fname, dpi=parf['dpi'], pad_inches=parf['pad_inches'], bbox_inches='tight')
            print('END Ga residuum')
    ##### END: figure 5.2 Residuum for GaNi solution ###########

if __name__=='__main__':
    plot_error()
    plot_memory()
    plot_residuals()

