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
    history [0] = event(0, parameters_store, SET_OF_PARAMETERS)
    history[0].i = parameters_store["initial_conditions"]["i0"]
    history[0].e = history[0].k*history[0].i
    history[0].s = 1- history[0].e - history[0].i
    history[0].r = 0
    history[0].q = 0
    history[0].d = 0
    history[0].tot = 1 - history[0].s - history[0].e - history[0].i 
    history[0].I = parameters_store[SET_OF_PARAMETERS]["N"]*history[0].i
    history[0].E = parameters_store[SET_OF_PARAMETERS]["N"]*history[0].e
    history[0].S = parameters_store[SET_OF_PARAMETERS]["N"]*history[0].s
    history[0].Q = 0
    history[0].R = 0
    history[0].D = 0
    history[0].TOT = history[0].tot *  parameters_store[SET_OF_PARAMETERS]["N"]    

    if parameters_store["simulation_parameters"]["VERBOSE"] == "TRUE":
        print ("t "+str(history[0].time)+" i "+str( history[0].I)+" e "+str( history[0].E)+" q "+str( history[0].Q)+" r "+str( history[0].R)+" s "+str( history[0].S)+" d "+str( history[0].D))
    
    
    # Creation of the history
    print ('\nCalculation with settings: '+str(SET_OF_PARAMETERS))
    for t in range (1, parameters_store["simulation_parameters"]["TIME_MAX"]):
        if (int (t)%int (parameters_store["simulation_parameters"]["TIME_MAX"]/10)==0): print ("-> time "+str(t))
        if parameters_store["simulation_parameters"]["VERBOSE"] == "TRUE": print ("TIME "+str(t))
        tmp_event = event (t, parameters_store, SET_OF_PARAMETERS)
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

    # Shifting the time by t0
    for t,e in dict(history).items():
        e.time = e.time-parameters_store["initial_conditions"]["t0"]
        
    from plotting import plot_summary
    plot_summary (history, parameters_store, SET_OF_PARAMETERS)

    
    # #Test plot
    # test_fig, test_ax = plt.subplots()
    # test_ax.plot ([t for t in history],[e.test for t,e in history.items()], 'black')
    # test_ax.set_xlabel ("Time [days]")
    # plt.show()

    if parameters_store["simulation_parameters"]["SAVE_HISTOGRAMS"] != "FALSE":
        from utils import save_histo
        print( '..storing h_nominal in '+str("files/"+str(SET_OF_PARAMETERS).replace ('parameters_','')+'_histos.dat'))
        save_histo ([e.time for t,e in history.items ()],
                    [e.TOT for t,e in history.items ()],
                    "h_nominal",
                    "files/"+str(SET_OF_PARAMETERS).replace ('parameters_','')+'_histos.dat'
        )


    if len(parameters_store["simulation_parameters"]["SCAN_PARAMETERS"])!=0 and parameters_store["simulation_parameters"]["SCAN_PARAMETERS"] != "FALSE":
        import copy
        # factors = [1e-1,0.5,1.0,2.,10.]
        # factors = [0.5,0.75,1.,1.25,2]
        factors = [0.75,0.9,1.,1.1,1.25]
        histories_for_scan = dict()
        print('\n\nStarting scan over parameters to check the effect')
        parameters_store_hard_copy = copy.deepcopy(parameters_store)
        for k in parameters_store["simulation_parameters"]["SCAN_PARAMETERS"]:
            # if k != "beta": continue
            if k == "N": continue
            print ("- Parameter: "+k)
            for f in factors:
                parameters_store_hard_copy[SET_OF_PARAMETERS][k] = float(f*parameters_store_hard_copy[SET_OF_PARAMETERS][k]) if k != 'tau' else int (f*parameters_store_hard_copy[SET_OF_PARAMETERS][k]+1)
                print ("    > "+str(parameters_store_hard_copy[SET_OF_PARAMETERS][k]))
                histories_for_scan [k+"_"+str(parameters_store_hard_copy[SET_OF_PARAMETERS][k])] = dict ()
                histories_for_scan [k+"_"+str(parameters_store_hard_copy[SET_OF_PARAMETERS][k])][0] = history[0]
                for t in range (1, parameters_store_hard_copy["simulation_parameters"]["TIME_MAX"]):
                    tmp_event = event (t, parameters_store, SET_OF_PARAMETERS)
                    event_precedent = histories_for_scan [k+"_"+str(parameters_store_hard_copy[SET_OF_PARAMETERS][k])][t-1] if t>0 else histories_for_scan [k+"_"+str(parameters_store_hard_copy[SET_OF_PARAMETERS][k])][0]
                
                    event_past = histories_for_scan [k+"_"+str(parameters_store_hard_copy[SET_OF_PARAMETERS][k])][t-parameters_store_hard_copy[SET_OF_PARAMETERS]["tau"]] if t>parameters_store_hard_copy[SET_OF_PARAMETERS]["tau"] else histories_for_scan [k+"_"+str(parameters_store_hard_copy[SET_OF_PARAMETERS][k])][0]
                
                    tmp_event.update_midpoint (parameters_store_hard_copy, event_precedent, event_past, SET_OF_PARAMETERS)
            
                    histories_for_scan [k+"_"+str(parameters_store_hard_copy[SET_OF_PARAMETERS][k])][t] = tmp_event
                    
                parameters_store_hard_copy[SET_OF_PARAMETERS] = copy.deepcopy(parameters_store[SET_OF_PARAMETERS])

        from plotting import plot_scan
        plot_scan (histories_for_scan, parameters_store, SET_OF_PARAMETERS)

        if parameters_store["simulation_parameters"]["SAVE_HISTOGRAMS"] != "FALSE":
            from utils import save_histo
            for key in histories_for_scan:
                h_name = 'h_'+key
                print( '..storing '+h_name+' in '+str("files/"+str(SET_OF_PARAMETERS).replace ('parameters_','')+'_histos.dat'))
                save_histo ([e.time for t,e in histories_for_scan[key].items ()],
                            [e.TOT for t,e in histories_for_scan[key].items ()],
                            h_name,
                            "files/"+str(SET_OF_PARAMETERS).replace ('parameters_','')+'_histos.dat'
                )



    if parameters_store["simulation_parameters"]["DISPLAY_DATA"]!="FALSE":
        from utils import read_data, save_histo
        dataset = read_data (parameters_store["simulation_parameters"]["DISPLAY_DATA"])
        from plotting import plot_data, plot_data_vs_model
        plot_data (dataset)
        plot_data_vs_model (dataset, history, parameters_store, SET_OF_PARAMETERS)
        
        if parameters_store["simulation_parameters"]["SAVE_HISTOGRAMS"] != "FALSE":
            print( '..storing h_data '+str("files/"+str(SET_OF_PARAMETERS).replace ('parameters_','')+'_histos.dat'))
            save_histo (dataset["t"],
                        dataset["tot"],
                    'h_data',
                    "files/"+str(SET_OF_PARAMETERS).replace ('parameters_','')+'_histos.dat'
            )
    
    if parameters_store["simulation_parameters"]["IMPROVED_MODEL"] != "FALSE":
        from plotting import plot_scheduling
        plot_scheduling (history, parameters_store, SET_OF_PARAMETERS)
