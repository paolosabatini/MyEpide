#/usr/bin/env python3

def read_data (filename):
    import os
    if not os.path.exists ("data/"+filename+".dat"):
        print("\033[91m [error]  dataset data/"+filename+".dat not found \033[0m" )
        return None
    dataset = dict ()
    dataset ["name"] = filename
    dataset ["t"] = []
    dataset ["d"] = []
    dataset ["i"] = []
    dataset ["r"] = []
    dataset ["tot"] = []
    # print (open ("data/"+filename+".dat","r+").readlines())
    if filename not in ["Lombardia","Italy"]:
        print("\033[93m [warning] format of dataset data/"+filename+".dat not known, assumed two columns time vs tot \033[0m" )
    for l in open ("data/"+filename+".dat","r+").readlines():
        if l[0] == "\n" or l[0] == "#": continue
        if filename == "Lombardia":
            dataset["t"].append( str(l.split("\t\t")[0]) )
            dataset["tot"].append( int (l.split("\t\t")[1]) )
            
        elif filename == "Italy":
            dataset["t"].append( str(l.split("\t\t")[0]) )
            dataset["d"].append( int (l.split("\t\t")[1].split("\t")[0]) )
            dataset["i"].append( int (l.split("\t\t")[1].split("\t")[1]) )
            dataset["r"].append( int (l.split("\t\t")[1].split("\t")[2]) )
            dataset["tot"].append( int (l.split("\t\t")[1].split("\t")[3]) )
            
        else:
            dataset["t"].append( str(l.split("\t\t")[0]) )
            dataset["tot"].append( int (l.split("\t\t")[1]) )
            
            
    return dataset


def save_histo (t, y, histo_name, filename):
    # want to save as day-per-day increment on txt file
    import os
    opt = 'a' if os.path.exists (filename) else 'w+'
    with open (filename,opt) as f:
        f.write ("\n##############\n# "+histo_name+" # \n##############\n")
        f.write ("\n#Time \ttotal case\n")
        previous = 0
        for time, num in zip (t,y):
            delta_num = num - previous
            f.write (str (time)+"\t"+str(delta_num)+'\n')
            previous = num
        f.write ("END\n")
    f.close()
        
        # import ROOT
    # h = ROOT.TH1F (histo_name, histo_name, abs (max (t)-min (t)+1), min (t)-0.5, max (t)+0.5 )
    # for time, num in zip (t,y):
    #     bin_index = h.GetXaxis().FindBin (time)
    #     delta_num = num if time == min(t) else num - h.GetBinContent (bin_index-1)
    #     h.SetBinContent (bin_index,delta_num)
    # f = ROOT.TFile.Open (filename,"UPDATE")
    # f.cd()
    # h.Write()
    # h.Close()
    
