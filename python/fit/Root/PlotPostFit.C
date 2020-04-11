
std::string RED = "\033[1;31m";
std::string GRN = "\033[1;32m";
std::string FIN = "\033[0m";
bool DEBUG = 1;



TString decode_var_names(TString label){
  std::map <TString, TString> dict;
  dict [  "ModelNormFactor" ] =  "SF";
  dict [ "alpha_beta" ] = "#beta";
  dict [ "alpha_corrbin1" ] =  "Corr. bin 1";
  dict [ "alpha_corrbin2" ] =  "Corr. bin 2";
  dict [ "alpha_corrbin3"]  = "Corr. bin 3";
  dict [ "alpha_corrbin4" ]  = "Corr. bin 4";
  dict [ "alpha_d2" ]  =  "d_{2}";
  dict [ "alpha_delta" ] =  "#delta";
  dict [ "alpha_gamma" ] = "#gamma";
  dict [ "alpha_k" ] = "k";
  dict ["alpha_mu" ] =  "#mu";
  dict [ "alpha_tau" ] = "#tau";

  return dict [label];
  
};

void PlotPostFit( std::string fitname){

  std::map <std::string, TCanvas*> canvases;
  std::map <std::string, TPad*> pads;
  std::map <std::string, TH1F*> histos;
  std::map <std::string, TH2F*> histos2D;


  
  std::string fitfile = "plots/"+fitname+"/results.root";
  std::string histofile = fitname+".root";
  std::string plot_dir = "plots/"+fitname+"/";

  std::cout << GRN<<"FITTER::INFO Loading histograms from:"<<FIN<< histofile << std::endl;
  std::cout << GRN<<"FITTER::INFO Histograms found:"<<FIN<< std::endl;

  TFile* hf = new TFile (histofile.c_str(),"READ");

  TIter nextkey(gDirectory->GetListOfKeys());
  while (auto key = (TKey*)nextkey()) {
    TObject* obj = key->ReadObj();
    if (!obj->IsA()->InheritsFrom("TH1")) continue;
    std::string name = std::string (obj->GetName());
    name = (name.find ("h_")!=std::string::npos) ?
      name.substr(name.find ("_")+1) : name;
    histos [name] = (TH1F*) obj;

    std::cout << GRN <<"\t * "<< name << FIN << std::endl;
 
  }

  TFile* hfit = new TFile (fitfile.c_str(),"READ");
  
  std::cout << GRN<<"FITTER::INFO Loading fit results from:"<<FIN<< fitfile << std::endl;
  std::cout << GRN <<"\t * NPs" << FIN << std::endl;
  histos ["nps"] = (TH1F*) hfit->Get("nps");
  std::cout << GRN <<"\t * CorrMatrix"<< FIN << std::endl;
  histos2D ["corr_matrix"] = (TH2F*) hfit->Get("correlation_matrix");
  

  


  //
  // Post-fit hist
  //
  std::cout << GRN<<"FITTER::INFO Post-fit histograms:"<<FIN<< fitfile << std::endl;
  canvases ["postfit"] = new TCanvas ("postfit","Post-fit distribution",600,600);
  pads ["l_postfit"] = new TPad ( ("l_postfit"),("l_postfit"),0,0.3,1,1);
  pads ["l_postfit"] -> Draw();
  pads ["l_postfit"] -> cd();
  pads ["l_postfit"] -> SetBottomMargin (0.005);
  pads ["l_postfit"] -> SetTopMargin (0.05);
  pads ["l_postfit"] -> SetRightMargin (0.05);
  pads ["l_postfit"] -> SetLeftMargin (0.12);
  histos ["nominal_postfit"] = (TH1F*) histos ["nominal_prefit"] -> Clone ("nominal_postfit");
  for (int i =1; i <= histos ["nominal_prefit"]->GetXaxis()->GetNbins();i++){
    std::cout << " BIN " << i << std::endl;
    float postfit_content = histos ["nominal_prefit"] -> GetBinContent (i);
    float postfit_error = 0;
    // std::cout << "initial prefit " << postfit_content << std::endl;
    for (int np = 1 ; np <= histos["nps"]->GetXaxis()->GetNbins(); np++){
      TString np_name = histos["nps"]->GetXaxis()->GetBinLabel (np);
      if (!np_name.Contains ("alpha"))
	postfit_content*=histos["nps"]->GetBinContent (np);
      else{
  	np_name = np_name (6,np_name.Length());
  	float delta = histos [std::string (&np_name[0])+"_symm_up"]->GetBinContent (i) - histos["nominal_prefit"]->GetBinContent (i);
  	float alpha = histos ["nps"]->GetBinContent (np);
  	postfit_content += alpha * delta;

      }
      // post fit error estimation
      float curr_err = 0;
      if (!np_name.Contains ("alpha"))
	curr_err = postfit_content*histos["nps"]->GetBinError (np);
      else{
	TString np_name_stripped = np_name (6,np_name.Length());
  	float delta = histos [std::string (&np_name_stripped[0])+"_symm_up"]->GetBinContent (i) - histos["nominal_prefit"]->GetBinContent (i);
  	float alpha_err = histos ["nps"]->GetBinError (np);
	curr_err = alpha_err * delta;

      }
      std::cout << np_name <<" " << curr_err << std::endl;
      
      for (int np2 = 1 ; np2 <= histos["nps"]->GetXaxis()->GetNbins(); np2++){
	float curr_err2 = 0;
	TString np2_name = histos["nps"]->GetXaxis()->GetBinLabel (np2);
	if (!np2_name.Contains ("alpha"))
	  curr_err2= histos2D["corr_matrix"]->GetBinContent ( np,histos["nps"] ->GetXaxis() ->GetNbins()-np2+1)*postfit_content*histos["nps"]->GetBinError (np2);
	else{
	  TString np2_name_stripped = np2_name (6,np2_name.Length());
	  float delta = histos [std::string (&np2_name_stripped[0])+"_symm_up"]->GetBinContent (i) - histos["nominal_prefit"]->GetBinContent (i);
	  float alpha_err = histos ["nps"]->GetBinError (np);
	  curr_err2 = histos2D["corr_matrix"]->GetBinContent ( np,histos["nps"] ->GetXaxis() ->GetNbins()-np2+1)* alpha_err * delta;
	}
	std::cout << " * Corr " << (histos2D["corr_matrix"]->GetBinContent ( np,histos["nps"]->GetXaxis()->GetNbins()-np2+1)) << std::endl;
	postfit_error += curr_err*curr_err2;
	std::cout << " = " <<np2_name <<" " << curr_err2 << " -> " << postfit_error << std::endl;
      }
    }
    histos ["nominal_postfit"]->SetBinContent (i,postfit_content);
    histos ["nominal_postfit"]->SetBinError (i,sqrt(abs(postfit_error)));
    std::cout << " = " <<postfit_content <<" " << sqrt(abs(postfit_error)) << std::endl;
  }
  histos ["data"] -> SetLineColor (kBlack);
  histos ["data"] -> SetMarkerColor (kBlack);
  histos ["data"] -> SetMarkerSize (1.1);
  histos ["data"] -> SetMarkerStyle (20);

  histos ["nominal_postfit"] -> SetFillColor (kGray+1);
  histos ["nominal_postfit"] -> SetFillStyle (3003);
  histos ["nominal_postfit"] -> SetLineColor (kGray+1);
  histos ["nominal_postfit"] -> SetLineWidth (2);
  histos ["nominal_prefit"] -> SetLineColor (kGray+1);
  histos ["nominal_prefit"] -> SetLineStyle (2);
  histos ["nominal_prefit"] -> SetLineWidth (2);
  histos ["nominal_prefit"] -> GetYaxis()->SetRangeUser (0,1.5*histos ["nominal_prefit"]->GetMaximum());
    
  histos ["nominal_prefit"] -> SetTitle (Form ("; ; Total cases / %d days", (int)histos ["nominal_prefit"]->GetBinWidth(1)));
  histos ["nominal_prefit"]->SetStats(0);
  histos ["nominal_prefit"]->Draw("hist");
  histos ["nominal_prefit"]->SetLineStyle (2);
  histos ["nominal_postfit"]->DrawClone("e2 same");
  histos ["nominal_postfit"] -> SetFillStyle (0);
  histos ["nominal_postfit"]->Draw("hist same");
 

  TLegend* leg_postfit = new TLegend (0.18,0.7,0.45,0.88);
  leg_postfit->SetBorderSize(0);
  leg_postfit->SetTextSize(0.04);
  leg_postfit->AddEntry (histos ["data"],"Data","p");
  leg_postfit->AddEntry (histos ["nominal_prefit"],"Pre-Fit","l");
  leg_postfit->AddEntry (histos ["nominal_postfit"],"Post-Fit","l");
  leg_postfit->Draw();
  
  canvases ["postfit"] -> cd();
  pads ["s_postfit"] = new TPad (("s_postfit"),("s_postfit"),0,0,1,0.3);
  pads ["s_postfit"] -> SetBottomMargin (0.25);
  pads ["s_postfit"] -> SetTopMargin (0.02);
  pads ["s_postfit"] -> SetRightMargin (0.05);
  pads ["s_postfit"] -> SetLeftMargin (0.12);
  pads ["s_postfit"] -> Draw();
  pads ["s_postfit"] -> cd();

  histos ["r_nominal_prefit"] = (TH1F*) histos ["nominal_prefit"] -> Clone ("r_nominal_prefit");
  histos ["r_nominal_prefit"] -> Add (histos ["nominal_postfit"], -1);
  histos ["r_nominal_prefit"] -> Divide (histos ["nominal_postfit"]);

  histos ["r_nominal_postfit"] = (TH1F*) histos ["nominal_postfit"] -> Clone ("r_nominal_postfit");
  histos ["r_nominal_postfit"] -> Add (histos ["nominal_postfit"], -1);
  histos ["r_nominal_postfit"] -> Divide (histos ["nominal_postfit"]);

   
  histos ["r_data"] = (TH1F*) histos ["data"] -> Clone ("r_data");
  histos ["r_data"] -> Add (histos ["nominal_postfit"], -1);
  histos ["r_data"] -> Divide (histos ["nominal_postfit"]);

  for (int i =1; i <= histos ["data"]->GetXaxis()->GetNbins();i++){
    histos ["r_data"] -> SetBinError (i, sqrt (histos ["data"]->GetBinContent (i)) / histos ["nominal_postfit"] ->GetBinContent (i));
    histos ["data"] -> SetBinError (i, sqrt (histos ["data"]->GetBinContent (i)) );
  }

  histos ["r_nominal_postfit"]->SetStats(0);
  histos ["r_nominal_prefit"] -> SetTitle("; Time [days]; Relative difference");
  histos ["r_nominal_prefit"] -> GetYaxis () -> SetLabelSize (0.08);
  histos ["r_nominal_prefit"] -> GetYaxis () -> SetTitleSize (0.1);
  histos ["r_nominal_prefit"] -> GetXaxis () -> SetTitleSize (0.1);
  histos ["r_nominal_prefit"] -> GetXaxis () -> SetTitleOffset (0.6);
  histos ["r_nominal_prefit"] -> GetYaxis () -> SetTitleOffset (0.6);
  histos ["r_nominal_prefit"] -> GetXaxis () -> SetLabelSize (0.08);
  histos ["r_nominal_prefit"] -> Draw("hist ");
  histos ["r_nominal_postfit"] -> SetFillStyle (3003);
  histos ["r_nominal_postfit"] -> DrawClone("e2 same");
  histos ["r_nominal_postfit"] -> SetFillStyle (0);
  histos ["r_nominal_postfit"] -> Draw("hist same");
  
  histos ["r_data"] -> Draw("e1 x0 same");
  histos ["r_nominal_prefit"] -> GetYaxis() -> SetRangeUser (-2,2);  

  pads ["l_postfit"] -> cd();
  histos ["data"] -> Draw ("e1 x0 same");

  canvases ["postfit"] -> SaveAs( (plot_dir+"ModelPostFit.pdf").c_str() );
    

}
