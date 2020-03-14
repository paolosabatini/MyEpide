#/usr/bin/env python3
latex_decode = {
    "beta" : "\{beta}",
    "gamma" : "\gamma",
    "k" : "k",
    "mu" : "\mu",
    "d1" : "d_{1}",
    "d2" : "d_{2}",
    "delta" : "\delta",
    "tau" : "\tau",
}


import matplotlib.pyplot as plt
import numpy as np

def plot_summary (history, parameters_store, SET_OF_PARAMETERS):

    #Summary plot
    fig, ax = plt.subplots()
    ax.plot ([t for t in history],[e.S for t,e in history.items()], 'k--', label='Susceptible')
    ax.plot ([t for t in history],[e.E for t,e in history.items()], 'y', label='Exposed')
    ax.plot ([t for t in history],[e.I for t,e in history.items()], 'r', label='Infected')
    ax.plot ([t for t in history], [e.Q for t,e in history.items()], 'b', label='Quarantined' )
    ax.plot ([t for t in history], [e.R for t,e in history.items()], 'g--', label='Recovered')
    ax.set_xlabel ("Time [days]")
    plt.ylim ( (1, 1.5*parameters_store[SET_OF_PARAMETERS]["N"]) )
    #plt.yscale('log')
    legend = ax.legend(loc='upper right', frameon=False)
    font_size = 10
    plt.text(plt.xlim()[0]+(0.05)*(plt.xlim()[1]-plt.xlim()[0]), plt.ylim()[0]+(0.95)*(plt.ylim()[1]-plt.ylim()[0]), r'$\beta='+str(parameters_store[SET_OF_PARAMETERS]["beta"])+'$', fontsize=font_size)
    plt.text(plt.xlim()[0]+(0.05)*(plt.xlim()[1]-plt.xlim()[0]), plt.ylim()[0]+(0.90)*(plt.ylim()[1]-plt.ylim()[0]), r'$k='+str(parameters_store[SET_OF_PARAMETERS]["k"])+'$', fontsize=font_size)
    plt.text(plt.xlim()[0]+(0.05)*(plt.xlim()[1]-plt.xlim()[0]), plt.ylim()[0]+(0.85)*(plt.ylim()[1]-plt.ylim()[0]), r'$\gamma='+str(parameters_store[SET_OF_PARAMETERS]["gamma"])+'$', fontsize=font_size)
    plt.text(plt.xlim()[0]+(0.05)*(plt.xlim()[1]-plt.xlim()[0]), plt.ylim()[0]+(0.80)*(plt.ylim()[1]-plt.ylim()[0]), r'$\mu='+str(parameters_store[SET_OF_PARAMETERS]["mu"])+'$', fontsize=font_size)
    plt.text(plt.xlim()[0]+(0.25)*(plt.xlim()[1]-plt.xlim()[0]), plt.ylim()[0]+(0.95)*(plt.ylim()[1]-plt.ylim()[0]), r'$d_{1}='+str(parameters_store[SET_OF_PARAMETERS]["d1"])+'$', fontsize=font_size)
    plt.text(plt.xlim()[0]+(0.25)*(plt.xlim()[1]-plt.xlim()[0]), plt.ylim()[0]+(0.90)*(plt.ylim()[1]-plt.ylim()[0]), r'$d_{2}='+str(parameters_store[SET_OF_PARAMETERS]["d2"])+'$', fontsize=font_size)
    plt.text(plt.xlim()[0]+(0.25)*(plt.xlim()[1]-plt.xlim()[0]), plt.ylim()[0]+(0.85)*(plt.ylim()[1]-plt.ylim()[0]), r'$\delta='+str(parameters_store[SET_OF_PARAMETERS]["delta"])+'$', fontsize=font_size)
    plt.text(plt.xlim()[0]+(0.25)*(plt.xlim()[1]-plt.xlim()[0]), plt.ylim()[0]+(0.80)*(plt.ylim()[1]-plt.ylim()[0]), r'$\tau='+str(parameters_store[SET_OF_PARAMETERS]["tau"])+'$', fontsize=font_size)
    print ("..saving plots/Summary_"+SET_OF_PARAMETERS+".pdf")
    fig.savefig("plots/Summary_"+SET_OF_PARAMETERS+".pdf", bbox_inches='tight')

    
def plot_scan (histories_for_scan, parameters_store, SET_OF_PARAMETERS):
    styles = [(0,(1,10)), 'dotted', '-', 'dashed', (0,(5,10))]
    
    
    quantities = ['S', 'E', 'I', 'Q', 'R']
    #Scan plots
    plots_collection = dict ()
    for parameter in parameters_store[SET_OF_PARAMETERS]:
        print (parameter)
        #if parameter != 'beta': continue
        for q in quantities:
            plots_collection[parameter+"_fig"], plots_collection[parameter+"_ax"] = plt.subplots()
            counter = 0
            for p in [x for x in histories_for_scan if parameter in x]:
                print (p)
                plots_collection[parameter+"_ax"].plot ([t for t,e in histories_for_scan[p].items()],
                                                        [getattr(e,q) for t,e in histories_for_scan[p].items()],
                                                        color='k', ls=styles[counter],
                                                        label=str(p.split('_')[1]))
                

                counter = counter+1
            plt.ylim ( (1, 1.5*parameters_store[SET_OF_PARAMETERS]["N"]) )
            plt.text(plt.xlim()[0]+(0.05)*(plt.xlim()[1]-plt.xlim()[0]), plt.ylim()[0]+(0.95)*(plt.ylim()[1]-plt.ylim()[0]), 'Scan over '+r'$'+latex_decode[parameter]+'$', fontsize=10)
            plots_collection[parameter+"_ax"].set_xlabel ("Time [days]")
            
                
            plots_collection[parameter+"_leg"] = plots_collection[parameter+"_ax"].legend(loc='upper right',
                                                                                          frameon=False)
            print ("..saving plots/Scan_"+q+"_vs_"+parameter+"_"+SET_OF_PARAMETERS+".pdf")
            plots_collection[parameter+"_fig"].savefig("plots/Scan_"+q+"_vs_"+parameter+"_"+SET_OF_PARAMETERS+".pdf",
                                                       bbox_inches='tight')
