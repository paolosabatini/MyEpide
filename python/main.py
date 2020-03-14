#/usr/bin/env python3

import json

if __name__ == "__main__":
    print ("** Easy simulation of epidemy spreading **")
    parameter_file = "parameters.json"
    print ("\n Parameter file: "+parameter_file)
    with open(parameter_file, 'r') as f:
        parameters_store = json.load(f)


    SET_OF_PARAMETERS = parameters_store["simulation_parameters"]["SET_OF_PARAMETERS"]
    history = dict ()

    from model import event
    
    # Initial conditions definition
    history [0] = event (0)
    history[0].i = parameters_store["initial_conditions"]["i0"]
    history[0].e = parameters_store[SET_OF_PARAMETERS]["k"]*history[0].i
    history[0].s = 1- history[0].e - history[0].i
    history[0].I = parameters_store[SET_OF_PARAMETERS]["N"]*history[0].i
    history[0].E = parameters_store[SET_OF_PARAMETERS]["N"]*history[0].e
    history[0].S = parameters_store[SET_OF_PARAMETERS]["N"]*history[0].s
    history[0].r = 0
    history[0].q = 0

    if parameters_store["simulation_parameters"]["VERBOSE"] == "TRUE":
        print ("t "+str(0)+" i "+str( history[0].I)+" e "+str( history[0].E)+" q "+str( history[0].Q)+" r "+str( history[0].R)+" s "+str( history[0].S))
    
    
    # Creation of the history
    for t in range (1, parameters_store["simulation_parameters"]["TIME_MAX"]):
        if (int (t)%int (parameters_store["simulation_parameters"]["TIME_MAX"]/10)==0): print ("-> time "+str(t))
        if parameters_store["simulation_parameters"]["VERBOSE"] == "TRUE": print ("TIME "+str(t))
        tmp_event = event (t)
        event_precedent = history[t-1] if t>0 else history[0]
        
        event_past = history[t-parameters_store[SET_OF_PARAMETERS]["tau"]] if t>parameters_store[SET_OF_PARAMETERS]["tau"] else history[0]

        # Euler extrapolation
        # tmp_event.update_s_euler (parameters_store, event_precedent, SET_OF_PARAMETERS)
        # tmp_event.update_e_euler (parameters_store, event_precedent, event_past, SET_OF_PARAMETERS)
        # tmp_event.update_i_euler (parameters_store, event_precedent, event_past, SET_OF_PARAMETERS)
        # tmp_event.update_q_euler (parameters_store, event_precedent, SET_OF_PARAMETERS)
        # tmp_event.update_r_euler (parameters_store, event_precedent, SET_OF_PARAMETERS)
        # tmp_event.update_test_euler (parameters_store, event_precedent, SET_OF_PARAMETERS)

        tmp_event.update_midpoint (parameters_store, event_precedent, event_past, SET_OF_PARAMETERS)
        
        history[t] = tmp_event

    
    import matplotlib.pyplot as plt
    import numpy as np

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

    fig.savefig("plots/Summary_"+SET_OF_PARAMETERS+".pdf", bbox_inches='tight')


    # #Test plot
    # test_fig, test_ax = plt.subplots()
    # test_ax.plot ([t for t in history],[e.test for t,e in history.items()], 'black')
    # test_ax.set_xlabel ("Time [days]")
    # plt.show()
