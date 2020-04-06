Double_t modelTests (Double_t* x, Double_t* par){
  float shift = 7;
  if (x[0] < shift) return par[0];
  else {
    return par[0]+par[1]*(x[0]-shift)+par[2]*(x[0]-shift)*(x[0]-shift);
    // return par[0]*TMath::Exp ( par[1]*(x[0]-shift) );
  }
}

void TamponsCorrections(){

  // Tampons numbers from 27/02 05/04b
  std::vector <float> tampons = {
    2427,3681,2966,2466,2218,2511,3981,2525,3997,5703,7875,3889,6935,12393,12857,11477,11682,15729,13063,10695,16884,17236,24109,26336,25180,17066,21496,27481,36615,33019,35447,28004,19829,29603,34455,39809,38617,37375,34237
  };

  TH1F* h = new TH1F("h_tamp", "Tampons vs time", tampons.size()+1, -0.5, tampons.size()+0.5);
  for (int b =1; b <= tampons.size(); b++){
    h->SetBinContent (b,tampons.at(b-1));
  }
 
  // TF1* f = new TF1 ("f", "[0]+[1]*x+[2]*x*x",0,tampons.size());
  // f->SetParameter(0,2000);
  // f->SetParameter(1,1000);
  // f->SetParameter(2,0);

  TF1* f = new TF1 ("f", modelTests,0,tampons.size(),3);
  f->SetParameter(0,2000);
  f->SetParameter(1,1000);
  f->SetParameter(2,0);

  
  h->Fit (f, "L0","");
  f->SetLineColor (kGray+1);
  f->SetLineStyle (2);
  f->SetLineWidth (2);

  
  
  TCanvas* c_tamp  = new TCanvas ("c_tot","Total model prediction",500,500);
  TPad* l= new TPad ( "l","l",0,0.3,1,1);
  l -> Draw();
  l -> cd();
  l -> SetBottomMargin (0.005);
  l -> SetTopMargin (0.05);
  l -> SetRightMargin (0.05);
  l -> SetLeftMargin (0.12);
  h->SetTitle ("; Time [days]; Number of tests");
  h->SetStats(0);
  h->SetMarkerStyle(20);
  h->SetMarkerSize(1.1);
  h->SetLineColor (kBlack);
  h->Draw("e1 x0");
  f->Draw("same");

  TLegend* leg_nom = new TLegend (0.2,0.7,0.6,0.88);
  leg_nom->SetBorderSize(0);
  leg_nom->SetTextSize(0.04);
  leg_nom->AddEntry (h,"Data","p");
  leg_nom->AddEntry (f,"p_{0}+p_{1}x+p_{2}*x^{2}","l"); 
  leg_nom->Draw();

  c_tamp-> cd();
  TPad* s = new TPad ("s","s",0,0,1,0.3);
  s -> SetBottomMargin (0.25);
  s -> SetTopMargin (0.02);
  s -> SetRightMargin (0.05);
  s -> SetLeftMargin (0.12);
  s -> Draw();
  s -> cd();
  
  TH1F* h_ratio = (TH1F*) h->Clone ("h_ratio");
  h_ratio -> Reset();
  for (int b =1; b <= tampons.size(); b++){
    float content = h -> GetBinContent (b);
    std::cout << content << "->" << content/f->Eval(h->GetBinCenter(b)) << std::endl;
    
    h_ratio->SetBinContent (b, (float (content)/f->Eval(h->GetBinCenter(b))) );
  }
  h_ratio -> GetYaxis() -> SetRangeUser (0.3,1.7);

  h_ratio -> GetYaxis () -> SetTitle ("Correction");
  h_ratio -> GetYaxis () -> SetLabelSize (0.08);
  h_ratio -> GetYaxis () -> SetTitleSize (0.1);
  h_ratio -> GetXaxis () -> SetTitleSize (0.1);
  h_ratio -> GetXaxis () -> SetTitleOffset (0.6);
  h_ratio -> GetYaxis () -> SetTitleOffset (0.6);
  h_ratio -> GetXaxis () -> SetLabelSize (0.08);

  h_ratio -> Draw("pl");

  TF1* lim_up = new TF1("lim_up","[0]",0,40);
  TF1* lim_down = new TF1("lim_down","[0]",0,40);
  float lim_val = 0.20;
  lim_up->SetParameter(0,1+lim_val);
  lim_up->SetLineColor(kGray+1);
  lim_up->SetLineStyle(2);
  lim_down->SetParameter(0,1-lim_val);
  lim_down->SetLineColor(kGray+1);
  lim_down->SetLineStyle(2);
  lim_up -> Draw("same");
  lim_down -> Draw("same");

  c_tamp -> SaveAs ("plots/TamponsCorrections.pdf");

  
  ///
  /// Set up the output for corrections
  ///
  std::cout << "\n ==== OUTPUT ====" << std::endl;
  std::cout << "tampons_corrections = [ " ;
  for (int b =1; b <= tampons.size(); b++)
    if (b == 1)
      std::cout <<std::to_string (h_ratio->GetBinContent(b));
    else
      std::cout << ","+std::to_string (h_ratio->GetBinContent(b));
  std::cout << " ]";
  std::cout << "\n ================" << std::endl;

    
}
