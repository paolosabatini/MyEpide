#/usr/bin/env python



dataset = {

    "00" : 2427, 
    "01" : 3681,
    "02" : 2966,
    "03" : 2466,
    "04" : 2218,
    "05" : 2511,
    "06" : 3981,
    "07" : 2525,
    "08" : 3997,
    "09" : 5703,
    "10" : 7875,
    "11" : 3889,
    "12" : 6935,
    "13" : 12393,
    "14" : 12857,
    "15" : 11477,
    "16" : 11682,
    "17" : 15729,
    "18" : 13063,
    "19" : 10695,
    "20" : 16884,
    "21" : 17236,
    "22" : 24109,
    "23" : 26336,
    "24" : 25180,
    "25" : 17066,
    "26" : 21496,
    "27" : 27481,
    "28" : 36615,
    "29" : 33019,
    "30" : 35447,
    "31" : 28004,
    }



import ROOT

ROOT.gStyle.SetErrorX(0)

h = ROOT.TH1F("h_tampons", "h_tampons", len (dataset.keys())+1,-0.5, len (dataset.keys())+0.5)

for t,n in dataset.iteritems():
    bin_index = h.GetXaxis().FindBin (float (t))
    h.SetBinContent (bin_index, n)
    
f = ROOT.TF1 ("quad","[0]+[1]*x+[2]*x*x",0,40)
f.SetParameter (0,2500)
f.SetParameter (1,1e3)
f.SetParameter (2,0.1)
h.Fit (f, "X","0",0,30)


c_test = ROOT.TCanvas ("c_test","c_test",400,400)
g = ROOT.TPad ("g","g",0,0.3,1,1)
g.SetBottomMargin (0.02)
g.Draw()
g.cd()

g.SetLeftMargin (0.15)
g.SetTopMargin (0.05)
g.SetRightMargin (0.05)
h.SetStats (0)
h.GetXaxis().SetLabelSize (0)
h.SetTitle (";Time [days];Numbers of tests")
h.SetLineColor (1)
h.SetMarkerColor (1)
h.SetMarkerSize (0.8) 
h.SetMarkerStyle (20) 
h.Draw("e1")
f.Draw("same")

leg = ROOT.TLegend (0.2,0.7,0.5,0.8)
leg.SetBorderSize(0)
leg.SetTextSize(0.04)
leg.AddEntry (h, "Data","l")
leg.AddEntry (f, "p_{0}+p_{1}t+p_{2}t^{2}","l")
leg.Draw()
c_test.cd()
s = ROOT.TPad ("s","s",0,0,1,0.3)
s.Draw()
s.cd()
s.SetBottomMargin (0.3)
s.SetLeftMargin (0.15)
s.SetTopMargin (0.02)
s.SetRightMargin (0.05)
h_ratio = h.Clone ("h_ratio")
h_ratio.Reset()
corrections = []
for b in range(1, h.GetXaxis().GetNbins()+2):
    content = h.GetBinContent (b)
    h_ratio.SetBinContent (b,content/f.Eval(h.GetBinCenter (b)))
    corrections.append (content/f.Eval(h.GetBinCenter (b)))
h_ratio.Draw("pl")
h_ratio.GetYaxis().SetTitle ("Correction")
h_ratio.GetYaxis().SetTitleOffset (0.5)
h_ratio.GetYaxis().SetRangeUser (0.4,1.6)
h_ratio.GetXaxis().SetTitleSize (0.1)
h_ratio.GetYaxis().SetTitleSize (0.1)
h_ratio.GetXaxis().SetLabelSize (0.08)
h_ratio.GetYaxis().SetLabelSize (0.08)



c_test.SaveAs ("tampons.pdf")


# printout
print "\n ==================== \n   CORRECTIONS \n ====================\n"
print corrections
