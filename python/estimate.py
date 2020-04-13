#/usr/bin/env python

import json

fitname = "fit/plots/aggressive/results.root"
plot_dir = "fit/plots/"+fitname.split("/")[2]+"/"
DEBUG=True
n_pseudo_exp = 1000
RELATIVE_VARIATION = 0.1

decode_nps_to_parameters = {
    "ModelNormFactor" : "i0",
    "alpha_beta" : "beta",
    "alpha_d2" : "d2",
    "alpha_delta" : "delta",
    "alpha_gamma" : "gamma",
    "alpha_k" : "k",
    "alpha_mu" : "mu",
    "alpha_tau" : "tau",
}


if __name__ == "__main__":
    print ("*************************************")
    print ("** Estimations from the post-fit   **")
    print ("*************************************")
    parameter_file = "parameters.json"
    print ("\nParameter file: "+parameter_file)
    with open(parameter_file, 'r') as f:
        parameters_store = json.load(f)

    
    SET_OF_PARAMETERS = parameters_store["simulation_parameters"]["SET_OF_PARAMETERS"]
    history = dict ()
    histos = dict ()
    canvases = dict ()
    
    #
    # NPs and correlation matrix
    #
    from ROOT import TFile 
    f=TFile (fitname, "READ")
    histos ["corr_matrix"] = f.Get("correlation_matrix")
    histos ["nps"] = f.Get("nps")

    mean_pars = [histos["nps"].GetBinContent (i) for i in range (1,histos["nps"].GetXaxis().GetNbins()+1)]
    var_pars = [histos["nps"].GetBinError (i) for i in range (1,histos["nps"].GetXaxis().GetNbins()+1)]
    
    print ("\nFitted NPs")
    for i,x in enumerate(mean_pars):
        print ("\t *"+str(histos["nps"].GetXaxis().GetBinLabel(i+1))+" = "+str(x)+" +- "+str(var_pars[i]) )
    
    
    from ROOT import TRandom3
    rand = TRandom3();

    
    #
    # Generate a changing copy of the parameters -> to smear them
    #    
    import copy
    current_parameter = copy.deepcopy(parameters_store)


    #
    # Declare the histories container
    #
    histories = dict()
    from model import event

    #
    # Loop over the pseudo-exp starting
    #
    print ("\nStarting looping over randomly generated NPs")    
    for i in range(0,n_pseudo_exp+1 if not DEBUG else 3):

        

        if DEBUG:
            print ("\t *****************")
            print ("\t * Extraction "+str(i)+"  *")
            print ("\t *****************")
        else:
            print ("\t Pseudo-exp "+str(i))



        #
        # Smearing the parameters (no correlations at the moment)
        #
        bad_sf = True
        while bad_sf:



            extr_pars = [rand.Gaus (mean_pars[m],var_pars[m]) for m in range (0,len(mean_pars))]
            # extr_pars = copy.deepcopy(mean_pars)
            
            transf_pars = copy.deepcopy(extr_pars)
        
            if DEBUG:
                print ("\t Parameters original")
                for k,x in enumerate(mean_pars):
                    print ("\t * extr "+str(histos["nps"].GetXaxis().GetBinLabel(k+1))+
                           " = "+str(extr_pars[k]) )

                print ("\t Parameters transformed")
            
            for k,xi in enumerate(list (extr_pars)):
                transf_pars [k] = 0
                for j,xj in enumerate(list (extr_pars)):
                    transf_pars [k] = transf_pars [k]  + histos["corr_matrix"].GetBinContent (j+1, histos["corr_matrix"].GetXaxis().GetNbins()-k)*extr_pars [j]

            if DEBUG:
                for k,x in enumerate(mean_pars):
                    print ("\t * transf "+str(histos["nps"].GetXaxis().GetBinLabel(k+1))+
                           " = "+str(transf_pars[k]) )

            if transf_pars[0] >0: bad_sf=False

        
        #
        # Update the parameters
        #
        
        for b in range (1,histos["nps"].GetXaxis().GetNbins()+1):

            name = histos["nps"].GetXaxis().GetBinLabel (b);
            if "corrbin" in name: continue

            if 'Model' not in name:
            # Using uncorrelated
                #new_par = (1+RELATIVE_VARIATION*extr_pars[b-1])*float(parameters_store[SET_OF_PARAMETERS][decode_nps_to_parameters [name]])
            # Using correlated
                new_par = (1+RELATIVE_VARIATION*transf_pars[b-1])*float(parameters_store[SET_OF_PARAMETERS][decode_nps_to_parameters [name]])
            else :
                new_par = (extr_pars[b-1])*float(parameters_store["initial_conditions"][decode_nps_to_parameters [name]])
            directory = SET_OF_PARAMETERS if not "Model" in name else "initial_conditions"
            current_parameter [directory][decode_nps_to_parameters [name]] = new_par if "tau" not in name else int (new_par) if new_par-int(new_par)<0.5 else int (new_par+1)
                        

        #    
        # Initial conditions
        #

            
        histories [i] = dict ()
        histories[i][0] = event(0, current_parameter, SET_OF_PARAMETERS)
        histories[i][0].i = current_parameter["initial_conditions"]["i0"]
        histories[i][0].e = histories[i][0].k*histories[i][0].i
        histories[i][0].s = 1- histories[i][0].e - histories[i][0].i
        histories[i][0].r = 0
        histories[i][0].q = 0
        histories[i][0].d = 0
        histories[i][0].tot = 1 - histories[i][0].s - histories[i][0].e - histories[i][0].i 
        histories[i][0].I = current_parameter[SET_OF_PARAMETERS]["N"]*histories[i][0].i
        histories[i][0].E = current_parameter[SET_OF_PARAMETERS]["N"]*histories[i][0].e
        histories[i][0].S = current_parameter[SET_OF_PARAMETERS]["N"]*histories[i][0].s
        histories[i][0].Q = 0
        histories[i][0].R = 0
        histories[i][0].D = 0
        histories[i][0].TOT = histories[i][0].tot *  current_parameter[SET_OF_PARAMETERS]["N"]    

        
        if DEBUG:

            print ("t "+str(histories[i][0].time)+" i "+str( histories[i][0].I)+" e "+str( histories[i][0].E)+" q "+str( histories[i][0].Q)+" r "+str( histories[i][0].R)+" s "+str( histories[i][0].S)+" d "+str( histories[i][0].D))
            print current_parameter["initial_conditions"]
            print i
        for t in range (1, current_parameter["simulation_parameters"]["TIME_MAX"]):
            tmp_event = event (t, current_parameter, SET_OF_PARAMETERS)
            event_precedent = histories [i][t-1] if t>0 else histories [i][0]
            event_past = histories [i][t-current_parameter[SET_OF_PARAMETERS]["tau"]] if t>current_parameter[SET_OF_PARAMETERS]["tau"] else histories [i][0]

            tmp_event.update_midpoint (current_parameter, event_precedent, event_past, SET_OF_PARAMETERS)
            histories [i][t] = tmp_event
        current_parameter[SET_OF_PARAMETERS] = copy.deepcopy(parameters_store[SET_OF_PARAMETERS])
        current_parameter["initial_conditions"] = copy.deepcopy(parameters_store["initial_conditions"])

        # Shifting the time by t0
        for t,e in dict(history).items():
            histories[i][t] = e.time-parameters_store["initial_conditions"]["t0"]

        if DEBUG:
            print [e.Q for j,e in histories[i].iteritems()]

            print "Max quarantined "+str( max ([e.Q for j,e in histories[i].iteritems()] ))
            print "Max deaths "+str( max ([e.D for j,e in histories[i].iteritems()] ))
            




    from ROOT import TH1F, TCanvas
    import math
    ######################
    # Estimation part!!! #
    ######################

    
    nbins =  int (0.5*math.sqrt(n_pseudo_exp)) if n_pseudo_exp>10 else 3

    from ROOT import TLatex
    latex=TLatex()
    latex.SetTextSize(0.03);
    latex.SetTextFont(42);
 
    # qpeak 30000, deaths 8000, total 60000
    #
    # Peak of quarantined
    #
    qpeak = 35000
    histos["q_peak"] = TH1F ("q_peak","",nbins, 0., 1e5)
    for i,h in histories.iteritems():
        histos["q_peak"].Fill( max ([e.Q for i,e in h.iteritems()]))
    canvases ["q_peak"]=TCanvas ("q_peak","Peak of quarantines",400,400)
    histos["q_peak"].SetStats(0)
    histos["q_peak"].SetTitle ("; Maximum of quarantined people; A.U.")
    histos["q_peak"].SetLineColor(1)
    histos["q_peak"].SetLineWidth(2)
    histos["q_peak"].GetYaxis().SetRangeUser(0,1.5*histos["q_peak"].GetMaximum())
    histos["q_peak"].Draw()
    canvases ["q_peak"] . SetBottomMargin (0.15);
    canvases ["q_peak"] . SetTopMargin (0.05);
    canvases ["q_peak"] . SetRightMargin (0.05);
    canvases ["q_peak"] . SetLeftMargin (0.12);
    latex.DrawLatexNDC(0.2,0.85,"Max. quarantined people = "+str(int(histos["q_peak"].GetMean()))+" #pm "+str( int(histos["q_peak"].GetRMS()) ))
    
    canvases ["q_peak"].SaveAs (plot_dir+"QuarantinePeak.pdf")

    #
    # time of peak of quarantined
    #
    histos["tq_peak"] = TH1F ("tq_peak","",20,30,50)
    for i,h in histories.iteritems():
        max_q = max ([e.Q for i,e in h.iteritems()] )
        for i,e in h.iteritems():
            if e.Q == max_q:
                histos["tq_peak"].Fill( e.time)
                break
    canvases ["tq_peak"]=TCanvas ("tq_peak","Peak of quarantines",400,400)
    histos["tq_peak"].SetStats(0)
    histos["tq_peak"].SetTitle ("; Time at the quarantined peak [days]; A.U.")
    histos["tq_peak"].SetLineColor(1)
    histos["tq_peak"].SetLineWidth(2)
    histos["tq_peak"].GetYaxis().SetRangeUser(0,1.5*histos["tq_peak"].GetMaximum())
    histos["tq_peak"].Draw()
    canvases ["tq_peak"] . SetBottomMargin (0.15);
    canvases ["tq_peak"] . SetTopMargin (0.05);
    canvases ["tq_peak"] . SetRightMargin (0.05);
    canvases ["tq_peak"] . SetLeftMargin (0.12);
    latex.DrawLatexNDC(0.2,0.85,"Time at the quarantined peak = "+str(int(histos["tq_peak"].GetMean()))+" #pm "+str( int(histos["tq_peak"].GetRMS()) )+" days")
    canvases ["tq_peak"].SaveAs (plot_dir+"TimeQuarantinePeak.pdf")
    #
    # Total deaths
    #
    deaths = 10000
    histos["deaths"] = TH1F ("deaths","",nbins, 0, 50000)
    for i,h in histories.iteritems():
        histos["deaths"].Fill( max ([e.D for i,e in h.iteritems()]))
    canvases ["deaths"]=TCanvas ("deaths","Total deaths",400,400)
    histos["deaths"].SetStats(0)
    histos["deaths"].SetTitle ("; Total deaths; A.U.")
    histos["deaths"].SetLineColor(1)
    histos["deaths"].SetLineWidth(2)
    histos["deaths"].GetYaxis().SetRangeUser(0,1.5*histos["deaths"].GetMaximum())
    histos["deaths"].Draw()
    canvases ["deaths"] . SetBottomMargin (0.15);
    canvases ["deaths"] . SetTopMargin (0.05);
    canvases ["deaths"] . SetRightMargin (0.05);
    canvases ["deaths"] . SetLeftMargin (0.12);
    latex.DrawLatexNDC(0.2,0.85,"Total deaths = "+str(int(histos["deaths"].GetMean()))+" #pm "+str( int(histos["deaths"].GetRMS()) )+"")
    canvases ["deaths"].SaveAs (plot_dir+"Deaths.pdf")

    
    #
    # Total cases
    #
    tot = 50000
    histos["total_cases"] = TH1F ("tot","",nbins, 0., 500000)
    for i,h in histories.iteritems():
        histos["total_cases"].Fill( max([e.TOT for i,e in h.iteritems()]))
    canvases ["total_cases"]=TCanvas ("total_cases","Total cases",400,400)
    histos["total_cases"].SetStats(0)
    histos["total_cases"].SetTitle ("; Total cases; A.U.")
    histos["total_cases"].SetLineColor(1)
    histos["total_cases"].SetLineWidth(2)
    histos["total_cases"].GetYaxis().SetRangeUser(0,1.5*histos["total_cases"].GetMaximum())
    histos["total_cases"].Draw()
    canvases ["total_cases"] . SetBottomMargin (0.15);
    canvases ["total_cases"] . SetTopMargin (0.05);
    canvases ["total_cases"] . SetRightMargin (0.05);
    canvases ["total_cases"] . SetLeftMargin (0.12);
    latex.DrawLatexNDC(0.2,0.85,"Total cases = "+str(int(histos["total_cases"].GetMean()))+" #pm "+str( int(histos["total_cases"].GetRMS()) )+"")
    canvases ["total_cases"].SaveAs (plot_dir+"TotalCases.pdf")


    #
    # time of saturation
    #
    histos["ttot_saturation"] = TH1F ("ttot_saturation","",50,30,80)
    for i,h in histories.iteritems():
        max_tot = max ([e.TOT for i,e in h.iteritems()] )
        for i,e in h.iteritems():
            if e.TOT > 0.95*max_tot:
                histos["ttot_saturation"].Fill( e.time)
                break
    canvases ["ttot_saturation"]=TCanvas ("ttot_saturation","Peak of quarantines",400,400)
    histos["ttot_saturation"].SetStats(0)
    histos["ttot_saturation"].SetTitle ("; Time at the quarantined peak [days]; A.U.")
    histos["ttot_saturation"].SetLineColor(1)
    histos["ttot_saturation"].SetLineWidth(2)
    histos["ttot_saturation"].GetYaxis().SetRangeUser(0,1.5*histos["ttot_saturation"].GetMaximum())
    histos["ttot_saturation"].Draw()
    canvases ["ttot_saturation"] . SetBottomMargin (0.15);
    canvases ["ttot_saturation"] . SetTopMargin (0.05);
    canvases ["ttot_saturation"] . SetRightMargin (0.05);
    canvases ["ttot_saturation"] . SetLeftMargin (0.12);
    latex.DrawLatexNDC(0.2,0.85,"Time at the total cases saturation = "+str(int(histos["ttot_saturation"].GetMean()))+" #pm "+str( int(histos["ttot_saturation"].GetRMS()) )+" days")
    canvases ["ttot_saturation"].SaveAs (plot_dir+"TimeTotalCasesSaturation.pdf")

    

