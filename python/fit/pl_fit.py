#/usr/bin/env python

FIT_SETUP = 'baseline'

from ROOT import TH1F, TCanvas

###########################
## Profile likelihood!!! ##
###########################

def read_histo (name, filename, bin_min, bin_max):
    histo_file_lines = open (filename,"r").readlines()
    block_init = next(i for i,x in enumerate(histo_file_lines) if name in x)
    
    block_end = [i for i in range(0,len(histo_file_lines)) if 'END' in histo_file_lines[i] and i > block_init][0]
    block = [x.replace('\n','') for x in histo_file_lines[block_init:block_end] if '#' not in x and x != '\n']
    time = [int (x.split('\t')[0]) for x in block]
    content = [float (x.split('\t')[1]) for x in block]
    h = TH1F (name,name, abs(bin_max-bin_min+1), bin_min-0.5,bin_max+0.5)
    from math import sqrt
    for t,c in zip (time,content):
        index = h.GetXaxis().FindBin (t)
        h.SetBinContent (index, c)
        h.SetBinError (index, sqrt(c) if c >0 else 0)
    return h



if __name__ == "__main__":

    ###
    ### Initialisation of config and histograms
    ###
    parameter_file = "config.json"
    print ("\n ********************")
    print (" *                  *")
    print (" *  PL Fit to data  *")
    print (" *                  *")
    print (" ******************** \n")

    print ("\nConfig file: "+parameter_file)
    print ("Setup: "+FIT_SETUP)
    import json
    with open(parameter_file, 'r') as f:
        config = json.load(f)
        
    HISTO_FILE = config[FIT_SETUP]['file']
    ROOT_FILE = config[FIT_SETUP]['rootfile']
    print ("Simulated points from: "+HISTO_FILE)
    
    import os
    if not os.path.exists (ROOT_FILE):
            histos = dict()
    
            print ("No root file "+ROOT_FILE+" found, creating it!\nReading histos: ")
            from ROOT import TFile
            rootfile = TFile (ROOT_FILE,"RECREATE")
            rootfile.cd()
            for key, item in config[FIT_SETUP].iteritems():
                if not '_up' in key and not '_down' in key and key != 'nominal' and key != 'data':
                    continue
                print ("\t> "+key)
                histos [key] = read_histo (config[FIT_SETUP][key], HISTO_FILE,config[FIT_SETUP]['bin_min'],config[FIT_SETUP]['bin_max'])
                histos [key].Rebin (config[FIT_SETUP]['rebin'])
                histos [key].Write ('h_'+key)
            rootfile.Close()
    


    
    #######################################
    # TEST CANVASES                       #
    #######################################
    # c_test = TCanvas("test","test", 400,400)
    # histos['nominal'].SetStats(0)
    # histos['nominal'].Rebin (config[FIT_SETUP]['rebin'])
    # histos['data'].Rebin (config[FIT_SETUP]['rebin'])
    # histos['nominal'].Draw()
    # histos['data'].SetLineColor (3)
    # histos['data'].Draw("same")
    # c_test.SaveAs("test.pdf")

    # c_frame= TCanvas("frame","frame", 400,400)
    # c_frame.cd()
    # tframe = t.frame()
    # roohist['nominal'].plotOn(tframe)
    # roohist['data'].plotOn(tframe)
    # tframe.Draw()
    # c_frame.SaveAs("frame.pdf")
    



    #######################################
    # END OF TEST CANVASES                #
    #######################################
