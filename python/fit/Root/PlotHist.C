std::string RED = "\033[1;31m";
std::string GRN = "\033[1;32m";
std::string FIN = "\033[0m";


void PlotHist(std::string filename){
  // gStyle->SetErrorX (1e-6);

  std::string plot_dir = "plots/"+filename.substr(0,filename.find (".root"))+"/";
  
  std::cout << GRN<<"=============== "<<FIN<< std::endl;
  std::cout << GRN<<"=== PLOTTER === "<<FIN<< std::endl;
  std::cout << GRN<<"=============== "<<FIN<< std::endl;
  
  std::cout << GRN<<"PLOTTER::INFO Opening " << filename << ".." <<FIN<< std::endl;
  TFile* rootfile = new TFile (filename.c_str(),"READ");

  std::map <std::string, TH1F*> histos;
  std::map <std::string, TCanvas*>  canvases;
  std::map <std::string, TPad*>  pads;
  
  rootfile->ls();
  
  std::cout << GRN<<"PLOTTER::INFO Histograms found:"<<FIN<< std::endl;
  
  TIter nextkey(gDirectory->GetListOfKeys());
  while (auto key = (TKey*)nextkey()) {
    TObject* obj = key->ReadObj();
    if (!obj->IsA()->InheritsFrom("TH1")) continue;
    std::string name_dirty = std::string (obj->GetName());


    std:: string name = (name_dirty.find ("h_")!=std::string::npos) ? name_dirty.substr(name_dirty.find ("h_")+std::string ("h_").size()): name_dirty;
    histos [name] = (TH1F*) obj;
    std::cout << GRN <<"\t * "<< name << FIN << std::endl;    
  }

  std::cout << GRN<<"PLOTTER::INFO Systematic plots:"<<FIN<< std::endl;

  ///
  /// Systematics plots
  ///
  for (std::pair <std::string, TH1F*> h : histos){

    if (h.first.find ("nominal")!=std::string::npos ||
	h.first.find ("data")!=std::string::npos ||
	h.first.find ("_down")!=std::string::npos ||
	h.first.find ("r_")!=std::string::npos ) continue;
    if(	( h.first.find ("symm")!=std::string::npos && h.first.find ("bin")==std::string::npos) ) continue;

    
    // if (h.first.find ("gamma")==std::string::npos &&
    // 	h.first.find ("beta")==std::string::npos) continue;
    
 
    std::string name = h.first.substr (0, h.first.find ("_"));
    std::cout << GRN <<"\t Syst: "<< name << FIN << " ( " << h.first << ")" << std::endl;

    canvases ["syst_"+name] = new TCanvas ( ("syst_"+name).c_str(), ("syst_"+name).c_str(), 500,500);
    canvases ["syst_"+name] -> cd ();
    pads ["syst_"+name+"_large"] = new TPad ( ("syst_"+name+"_large").c_str(),("syst_"+name+"_large").c_str(),0,0.3,1,1);
    pads ["syst_"+name+"_large"] -> Draw();
    pads ["syst_"+name+"_large"] -> cd();
    pads ["syst_"+name+"_large"] -> SetBottomMargin (0.005);
    pads ["syst_"+name+"_large"] -> SetTopMargin (0.05);
    pads ["syst_"+name+"_large"] -> SetRightMargin (0.05);
    pads ["syst_"+name+"_large"] -> SetLeftMargin (0.12);
    histos ["nominal"] -> SetTitle( ( "; Time [days]; Total cases/"+std::to_string (int (histos["nominal"]->GetBinWidth(1) ))+" days").c_str() );
    histos ["nominal"] -> SetStats (0);
    histos ["nominal"] -> SetLineColor (kGray+1);
    histos ["nominal"] -> SetLineWidth (2);
    if (name.find ("corr")==std::string::npos){
      histos [name+"_down"] -> SetLineColor (kBlue-7);
      histos [name+"_down"] -> SetLineWidth (2);
      histos [name+"_up"] -> SetLineColor (kRed+3);
      histos [name+"_up"] -> SetLineWidth (2);
    }
    histos [name+"_symm_down"] -> SetLineColor (kBlue-7);
    histos [name+"_symm_down"] -> SetLineWidth (2);
    histos [name+"_symm_down"] -> SetLineStyle (2);
    histos [name+"_symm_up"] -> SetLineColor (kRed+3);
    histos [name+"_symm_up"] -> SetLineWidth (2);
    histos [name+"_symm_up"] -> SetLineStyle (2);
    
    float ymax = (histos ["nominal"]->GetMaximum () > histos [name+"_symm_down"] -> GetMaximum()) ?
      histos ["nominal"]->GetMaximum () : histos [name+"_symm_down"]->GetMaximum () ;
    ymax =  (histos [name+"_symm_up"]->GetMaximum () > histos [name+"_symm_down"] -> GetMaximum()) ?
      histos [name+"_symm_up"]->GetMaximum () : histos [name+"_symm_down"]->GetMaximum () ;

    histos ["nominal"] -> GetYaxis ()-> SetRangeUser (0, 1.5*ymax);
    histos ["nominal"] -> Draw ("hist");
    if (name.find ("corr")==std::string::npos){
      histos [name+"_down"] -> Draw ("hist same");
      histos [name+"_up"] -> Draw ("hist same");
    }
    histos [name+"_symm_down"] -> Draw ("hist same");
    histos [name+"_symm_up"] -> Draw ("hist same");

    histos ["data"]-> SetMarkerStyle(20);
    histos ["data"]-> SetMarkerSize(1.1);
    histos ["data"] -> Draw (" e1 x0 same");

    TLegend* leg = new TLegend (0.2,0.7,0.6,0.88);
    leg->SetBorderSize(0);
    leg->SetTextSize(0.04);
    if (name.find ("corr")==std::string::npos){
      leg->AddEntry (histos [name+"_down"],(name+" down").c_str(),"l");
      leg->AddEntry (histos [name+"_up"],(name+" up").c_str(),"l");
    }
    leg->AddEntry (histos [name+"_symm_down"],(name+" down (symmetr.)").c_str(),"l");
    leg->AddEntry (histos [name+"_symm_up"],(name+" up (symmetr.)").c_str(),"l");
    leg->Draw();
    
    canvases ["syst_"+name] -> cd();
    pads ["syst_"+name+"_small"] = new TPad (("syst_"+name+"_small").c_str(),("syst_"+name+"_small").c_str(),0,0,1,0.3);
    pads ["syst_"+name+"_small"] -> SetBottomMargin (0.25);
    pads ["syst_"+name+"_small"] -> SetTopMargin (0.02);
    pads ["syst_"+name+"_small"] -> SetRightMargin (0.05);
    pads ["syst_"+name+"_small"] -> SetLeftMargin (0.12);
    pads ["syst_"+name+"_small"] -> Draw();
    pads ["syst_"+name+"_small"] -> cd();
    histos ["r_nominal"] = (TH1F*) histos ["nominal"] -> Clone ("r_nominal");
    histos ["r_nominal"] -> Add (histos ["nominal"], -1);
    histos ["r_nominal"] -> Divide ( histos ["nominal"] );
    if (name.find ("corr")==std::string::npos){
      histos ["r_"+name+"_down"] = (TH1F*) histos [name+"_down"] -> Clone ( ("r_"+name+"_down").c_str() );
      histos ["r_"+name+"_down"] -> Add ( histos ["nominal"],-1 );
      histos ["r_"+name+"_down"] -> Divide ( histos ["nominal"] );
      histos ["r_"+name+"_up"] = (TH1F*) histos [name+"_up"] -> Clone ( ("r_"+name+"_up").c_str() );
      histos ["r_"+name+"_up"] -> Add (histos ["nominal"], -1);
      histos ["r_"+name+"_up"] -> Divide ( histos ["nominal"] );
    }
    histos ["r_"+name+"_symm_up"] = (TH1F*) histos [name+"_symm_up"] -> Clone ( ("r_"+name+"_symm_up").c_str() );
    histos ["r_"+name+"_symm_up"] -> Add (histos ["nominal"], -1);
    histos ["r_"+name+"_symm_up"] -> Divide ( histos ["nominal"] );
    histos ["r_"+name+"_symm_down"] = (TH1F*) histos [name+"_symm_down"] -> Clone ( ("r_"+name+"_symm_down").c_str() );
    histos ["r_"+name+"_symm_down"] -> Add ( histos ["nominal"],-1 );
    histos ["r_"+name+"_symm_down"] -> Divide ( histos ["nominal"] );
histos ["r_data"] = (TH1F*) histos ["data"] -> Clone ("r_nominal");
    histos ["r_data"] -> Add (histos ["nominal"], -1);
    histos ["r_data"] -> Divide ( histos ["nominal"] );
    histos ["r_nominal"] -> GetYaxis () -> SetRangeUser (-2,2);
    histos ["r_nominal"] -> GetYaxis () -> SetTitle ("Relative difference");
    histos ["r_nominal"] -> GetYaxis () -> SetLabelSize (0.08);
    histos ["r_nominal"] -> GetYaxis () -> SetTitleSize (0.1);
    histos ["r_nominal"] -> GetXaxis () -> SetTitleSize (0.1);
    histos ["r_nominal"] -> GetXaxis () -> SetTitleOffset (0.6);
    histos ["r_nominal"] -> GetYaxis () -> SetTitleOffset (0.6);
    histos ["r_nominal"] -> GetXaxis () -> SetLabelSize (0.08);
    histos ["r_nominal"] -> Draw ("hist");
    if (name.find ("corr")==std::string::npos){
      histos ["r_"+name+"_up"] -> Draw ("hist same");
      histos ["r_"+name+"_down"] -> Draw ("hist same");
    }
    histos ["r_"+name+"_symm_up"] -> Draw ("hist same");
    histos ["r_"+name+"_symm_down"] -> Draw ("hist same");
    histos ["r_data"] -> Draw ("e1 x0 same");

    
    canvases ["syst_"+name] -> SaveAs ( (plot_dir+"Syst_"+name+".pdf" ).c_str() );
    
  }
  
  ///
  /// Total model
  ///
  canvases ["c_tot"] = new TCanvas ("c_tot","Total model prediction",500,500);
  pads ["nominal_large"] = new TPad ( "nominal_large","nominal_large",0,0.3,1,1);
  pads ["nominal_large"] -> Draw();
  pads ["nominal_large"] -> cd();
  pads ["nominal_large"] -> SetBottomMargin (0.005);
  pads ["nominal_large"] -> SetTopMargin (0.05);
  pads ["nominal_large"] -> SetRightMargin (0.05);
  pads ["nominal_large"] -> SetLeftMargin (0.12);
  histos ["nominal_prefit"] -> SetStats(0);
  histos ["nominal_prefit"] -> SetTitle( ( "; Time [days]; Total cases/"+std::to_string (int (histos["nominal"]->GetBinWidth(1) ))+" days").c_str() );
  histos ["nominal"] -> SetLineColor (kGray+1);
  histos ["nominal"] -> SetLineWidth (2);
  histos ["data"] -> SetMarkerStyle(20);
  histos ["data"] -> SetMarkerColor(1);
  histos ["data"] -> SetLineColor(1);
  histos ["data"] -> SetLineWidth(2);
  histos ["nominal_prefit"] -> GetYaxis() -> SetRangeUser (0,1.2*histos ["nominal_prefit"]->GetMaximum()+histos ["nominal_prefit"]->GetBinError(histos ["nominal_prefit"]->GetXaxis()->GetNbins()));
  histos ["nominal_prefit"] -> SetLineColor (kGray+1);
  histos ["nominal_prefit"] -> SetFillColor (kGray+1);
  histos ["nominal_prefit"] -> SetFillStyle (3003);
    
  histos ["nominal_prefit"] -> Draw("e2");
  histos ["nominal"] -> Draw("hist same");

  histos ["data"] -> Draw("same e1 x0");

  TLegend* leg_nom = new TLegend (0.18,0.7,0.45,0.88);
  leg_nom->SetBorderSize(0);
  leg_nom->SetTextSize(0.04);
  leg_nom->AddEntry (histos ["data"],"Data","p");
  leg_nom->AddEntry (histos ["nominal_prefit"],"Nominal model","lf"); 
  leg_nom->Draw();

  canvases ["c_tot"] -> cd();
  pads ["nominal_small"] = new TPad ("nominal_small","nominal_small",0,0,1,0.3);
  pads ["nominal_small"] -> SetBottomMargin (0.25);
  pads ["nominal_small"] -> SetTopMargin (0.02);
  pads ["nominal_small"] -> SetRightMargin (0.05);
  pads ["nominal_small"] -> SetLeftMargin (0.12);
  pads ["nominal_small"] -> Draw();
  pads ["nominal_small"] -> cd();
  histos ["r_nominal_prefit"] = (TH1F*) histos ["nominal_prefit"] -> Clone ("r_nominal_prefit");
  histos ["r_nominal_prefit"] -> Add (histos ["nominal"], -1);
  histos ["r_nominal_prefit"] -> Divide ( histos ["nominal"] );
  // histos ["r_data"] = (TH1F*) histos ["data"] -> Clone ("r_data");
  // histos ["r_data"] -> Add (histos ["nominal"], -1);
  // histos ["r_data"] -> Divide ( histos ["nominal"] );

  histos ["r_nominal_prefit"] -> GetYaxis () -> SetRangeUser (-2,2);
  histos ["r_nominal_prefit"] -> GetYaxis () -> SetTitle ("Relative difference");
  histos ["r_nominal_prefit"] -> GetYaxis () -> SetLabelSize (0.08);
  histos ["r_nominal_prefit"] -> GetYaxis () -> SetTitleSize (0.1);
  histos ["r_nominal_prefit"] -> GetXaxis () -> SetTitleSize (0.1);
  histos ["r_nominal_prefit"] -> GetXaxis () -> SetTitleOffset (0.6);
  histos ["r_nominal_prefit"] -> GetYaxis () -> SetTitleOffset (0.6);
  histos ["r_nominal_prefit"] -> GetXaxis () -> SetLabelSize (0.08);



  histos ["r_nominal_prefit"] -> Draw("e2");   
  histos ["r_data"] -> Draw("same e1 x0");


  canvases ["c_tot"] -> SaveAs ( (plot_dir+"ModelPrefit.pdf").c_str());


}
