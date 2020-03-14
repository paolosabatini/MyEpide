#/usr/bin/env python3

import json

if __name__ == "__main__":
    print ("*************************************")
    print ("** Simulation of epidemy spreading **")
    print ("*************************************")
    parameter_file = "parameters.json"
    print ("\nParameter file: "+parameter_file)
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
    print ('\nCalculation with settings: '+str(SET_OF_PARAMETERS))
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

    from plotting import plot_summary
    plot_summary (history, parameters_store, SET_OF_PARAMETERS)

    # #Test plot
    # test_fig, test_ax = plt.subplots()
    # test_ax.plot ([t for t in history],[e.test for t,e in history.items()], 'black')
    # test_ax.set_xlabel ("Time [days]")
    # plt.show()


    if parameters_store["simulation_parameters"]["SCAN_PARAMETERS"] == "TRUE":
        factors = [0.1,0.5,1,2,10]
        histories_for_scan = dict()
        print('\n\nStarting scan over parameters to check the effect')
        parameters_store_hard_copy = parameters_store
        for k,v in parameters_store_hard_copy[SET_OF_PARAMETERS].items():
            # if k != "beta": continue
            if k == "N": continue
            print ("- Parameter: "+k)
            for f in factors:
                
                parameters_store_hard_copy[SET_OF_PARAMETERS][k] = f*v
                print ("    > "+str(parameters_store_hard_copy[SET_OF_PARAMETERS][k]))
                histories_for_scan [k+"_"+str(parameters_store_hard_copy[SET_OF_PARAMETERS][k])] = dict ()
                histories_for_scan [k+"_"+str(parameters_store_hard_copy[SET_OF_PARAMETERS][k])][0] = history[0]
                for t in range (1, parameters_store_hard_copy["simulation_parameters"]["TIME_MAX"]):
                    tmp_event = event (t)
                    event_precedent = histories_for_scan [k+"_"+str(parameters_store_hard_copy[SET_OF_PARAMETERS][k])][t-1] if t>0 else histories_for_scan [k+"_"+str(parameters_store_hard_copy[SET_OF_PARAMETERS][k])][0]
                
                    event_past = histories_for_scan [k+"_"+str(parameters_store_hard_copy[SET_OF_PARAMETERS][k])][t-parameters_store_hard_copy[SET_OF_PARAMETERS]["tau"]] if t>parameters_store_hard_copy[SET_OF_PARAMETERS]["tau"] else histories_for_scan [k+"_"+str(parameters_store_hard_copy[SET_OF_PARAMETERS][k])][0]
                
                    tmp_event.update_midpoint (parameters_store_hard_copy, event_precedent, event_past, SET_OF_PARAMETERS)
            
                    histories_for_scan [k+"_"+str(parameters_store_hard_copy[SET_OF_PARAMETERS][k])][t] = tmp_event
                    
                parameters_store_hard_copy[SET_OF_PARAMETERS][k] = parameters_store[SET_OF_PARAMETERS][k]

        from plotting import plot_scan
        plot_scan (histories_for_scan, parameters_store, SET_OF_PARAMETERS)
