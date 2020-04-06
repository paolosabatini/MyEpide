#/usr/bin/env python

FIT_SETUP = 'aggressive'
EXPORT = True
from ROOT import TH1F, TCanvas

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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
    print (bcolors.OKGREEN+"\n ********************"+bcolors.ENDC)
    print (bcolors.OKGREEN+" *                  *"+bcolors.ENDC)
    print (bcolors.OKGREEN+" *  PL Fit to data  *"+bcolors.ENDC)
    print (bcolors.OKGREEN+" *                  *"+bcolors.ENDC)
    print (bcolors.OKGREEN+" ******************** \n"+bcolors.ENDC)

    print (bcolors.OKGREEN+"\nConfig file: "+parameter_file+bcolors.ENDC)
    print (bcolors.OKGREEN+"Setup: "+FIT_SETUP+bcolors.ENDC)
    import json
    with open(parameter_file, 'r') as f:
        config = json.load(f)
        
    HISTO_FILE = config[FIT_SETUP]['file']
    ROOT_FILE = config[FIT_SETUP]['rootfile']
    print (bcolors.OKGREEN+"Simulated points from: "+HISTO_FILE+bcolors.ENDC)
    
    histos = dict()
        
    from ROOT import TFile
    for key, item in config[FIT_SETUP].iteritems():
        if not '_up' in key and not '_down' in key and key != 'nominal' and key != 'data':
            continue
        print (bcolors.OKGREEN+"\t> "+key+bcolors.ENDC)
        histos [key] = read_histo (config[FIT_SETUP][key], HISTO_FILE,config[FIT_SETUP]['bin_min'],config[FIT_SETUP]['bin_max'])
        histos [key].Rebin (config[FIT_SETUP]['rebin'])
        histos [key].SetName ('h_'+key)

    #
    # Creation of the overall pre-fit prediction
    #
    histos ["nominal_prefit"] = histos["nominal"].Clone ("nominal_prefit")
    for b in range (1, histos ["nominal"].GetXaxis().GetNbins()+1):
        histos ["nominal_prefit"].SetBinError (b,0)
    
    #
    # Simmetrisation of systematics
    #
    for key,h in dict ( histos ).iteritems():
        if "nominal" in key: continue
        if "data" in key: continue
        if "down" in key: continue
        if "symm" in key: continue
        name = key.split("_")[0]
        histos [name+"_symm_up"] = histos [name+"_up"].Clone(name+"_symm_up")  
        histos [name+"_symm_down"] = histos [name+"_down"].Clone(name+"_symm_down")  
        for b in range (1, histos [name+"_symm_up"].GetXaxis().GetNbins()+1):
            up_var = histos [name+"_up"].GetBinContent (b)
            down_var = histos [name+"_down"].GetBinContent (b)
            nom = histos ["nominal"].GetBinContent (b)
            if (up_var-nom)*(down_var-nom) > 0: # systematics on the same side
                larger_var = 0.5*(up_var+down_var)
                histos [name+"_symm_up"].SetBinContent (b, nom+(larger_var-nom) if nom+(larger_var-nom)>0 else 0)
                histos [name+"_symm_down"].SetBinContent (b,nom-(larger_var-nom) if nom-(larger_var-nom)>0 else 0)
                # print "\nOne sided variation: "+name
                # print "up original "+str(up_var)+" down original "+str(down_var)+" nom "+str(nom)
                # print "up mod "+str( (nom+(larger_var-nom) if nom+(larger_var-nom)>0 else 0) )+" down original "+str( (nom-(larger_var-nom) if nom-(larger_var-nom)>0 else 0) )
                
            else:
                histos [name+"_symm_up"].SetBinContent (b,nom+abs(up_var-down_var)/2. if nom+abs(up_var-down_var)/2.>0 else 0)
                histos [name+"_symm_down"].SetBinContent (b,nom-abs(up_var-down_var)/2. if nom-abs(up_var-down_var)/2.>0 else 0)
                # print "\n2 sided variation: "+name
                # print "up original "+str(up_var)+" down original "+str(down_var)+" nom "+str(nom)
                # print "up mod "+str( (nom+abs(up_var-down_var)/2. if nom+abs(up_var-down_var)/2.>0 else 0) )+" down original "+str( (nom-abs(up_var-down_var)/2. if nom-abs(up_var-down_var)/2.>0 else 0) )
            from math import sqrt
            histos ["nominal_prefit"].SetBinError (b, sqrt (histos ["nominal_prefit"].GetBinError(b)*histos ["nominal_prefit"].GetBinError(b)+(histos [name+"_symm_up"].GetBinContent(b)-histos ["nominal"].GetBinContent(b))*(histos [name+"_symm_up"].GetBinContent(b)-histos ["nominal"].GetBinContent(b))));
            
    import os
    if EXPORT and not os.path.exists(ROOT_FILE):
        print (bcolors.OKGREEN+"Exporting into: "+ROOT_FILE+bcolors.ENDC)
        rootfile = TFile (ROOT_FILE,"RECREATE")
        rootfile.cd()
        for key,h in histos.iteritems():
            h.SetTitle ('h_'+key)
            h.Write ('h_'+key)
        rootfile.Close()

    # os.system ( 'root -l fitter.C ("'+ROOT_FILE+'")' )
    print (bcolors.OKGREEN+"Launching the fitter.."+bcolors.ENDC)
    # os.system ( 'root -l -q '+"'"+'Root/fitter.C ("'+ROOT_FILE+'","'+FIT_SETUP+'")'+"'" )







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
