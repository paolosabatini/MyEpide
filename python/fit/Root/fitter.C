#include<string>
#include<vector>
#include<map>
#include<TFile.h>
#include<TH1F.h>

std::string RED = "\033[1;31m";
std::string GRN = "\033[1;32m";
std::string FIN = "\033[0m";
bool DEBUG = 1;

using namespace RooStats;
using namespace HistFactory;


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


void fitter(std::string filename, std::string label) {

  std::string plot_dir = "plots/"+filename.substr(0,filename.find (".root"))+"/";
  // ROOT::SumW2Error (kFALSE);
  
  std::cout << GRN<<"FITTER::INFO Opening " << filename << ".." <<FIN<< std::endl;
  TFile* rootfile = new TFile (filename.c_str(),"READ");

  std::map <std::string, TH1F*> histos;
  std::map <std::string, RooDataHist*> roohistos;
  std::map <std::string, RooHistPdf*> roohistopdf;
  std::map<std::string, std::string> strings;
  
  std::cout << GRN<<"FITTER::INFO Histograms found:"<<FIN<< std::endl;
  
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
      
  std::cout << GRN <<"\n\nStarting setting up the HistFactory workspace.. " << FIN<<std::endl;
  std::cout << GRN <<"\tSettings:" << FIN<<std::endl;
  //
  // Measurement
  //
  Measurement meas("ModelNormFactor", "ModelNormFactor");
  meas.SetOutputFilePrefix( ("./results/"+label).c_str() );
  meas.SetExportOnly( 0 );
  meas.SetPOI( "ModelNormFactor" );
  meas.SetLumi( 1.0 );
  meas.SetLumiRelErr( 0.02 );
  meas.AddConstantParam("Lumi");
  std::cout<<GRN<<"\t Measurement = ModelNormFactor"<<FIN<<std::endl;
  //
  // Channel
  //
  Channel  chan( "TimeFrame" );
  // chan.SetStatErrorConfig(0.05, "Poisson");
  std::cout<<GRN<<"\t Region = TimeFrame"<<FIN<<std::endl;
  chan.SetData( "h_data",  filename );
  // chan.SetData( "h_data",  filename );
  std::cout<<GRN<<"\t Data = h_data"<<FIN<<std::endl;
  //
  // Sample
  //
  Sample model( "h_nominal", "h_nominal", filename );
  model.SetNormalizeByTheory( 0 );
  model.AddNormFactor( "ModelNormFactor", 1, 0, 3);
  std::cout << GRN << "\t Model = nominal" << FIN <<std::endl;
  
  std::map <std::string, HistoSys> systematics;
  for (std::pair <std::string, TH1F*> h : histos ){
    // std::cout << "         => "<< h.first << std::endl;
    if (h.first.find ("_up")!=std::string::npos) 
      continue;
    if (h.first.find ("data")!=std::string::npos) 
      continue;
    if (h.first.find ("nominal")!=std::string::npos || h.first.find ("prefit")!=std::string::npos) 
      continue;
    if (h.first.find ("symm")!=std::string::npos && h.first.find ("corrbin")==std::string::npos) 
      continue;
    // if (h.first.find ("beta")==std::string::npos) 
    //   continue;
    std::string key = h.first.substr(0,h.first.find ("_"));
    // std::string key = h.first;
    
    systematics [key] = HistoSys(key);
    //std::cout << GRN << "\t Systematics = " << key <<" to model" << FIN << std::endl;
    std::cout << GRN << "\t  HistoSys: " << key << FIN <<std::endl;
    systematics [key].SetInputFileHigh(filename);
    systematics [key].SetInputFileLow (filename);
    systematics [key].SetHistoNameHigh( "h_"+key+"_symm_up");
    systematics [key].SetHistoNameLow( "h_"+key+"_symm_down");
    model.AddHistoSys (systematics[key]);
   
								  
  }

  std::cout << GRN <<"Adding the model to the region" << FIN << std::endl;
  chan.AddSample( model );
  meas.AddChannel( chan );


  
  // std::cout << "DEBUG Is systematics filled?" << std::endl;
  // for (std::pair <std::string, HistoSys> s : systematics ){
  //    std::cout << "sys " << s.first << std::endl;
  // }
  
  meas.CollectHistograms();
  meas.PrintTree();
  meas.PrintXML( "xmlFromCCode", meas.GetOutputFilePrefix() );


  //
  // Set some initial values & fit
  //
  std::cout << GRN <<"Exporting the workspace!" << FIN << std::endl;
  RooWorkspace* w = HistoToWorkspaceFactoryFast (meas).MakeCombinedModel(meas);
  w->var ("alpha_beta") -> setVal( -1. );
  w->var ("alpha_corrbin4") -> setVal ( +1. );
  w->var ("alpha_corrbin2") -> setVal ( +2. );
  RooFitResult* r =w->pdf("model_TimeFrame")->fitTo( *w->data( "obsData" ) , RooFit::Save() );

  // ================================================================== //
  
  //
  // Output of the parameters!
  //
  std::map <std::string, TCanvas*> canvases;
  std::map <std::string, TH2*> histos2D;
  std::map <std::string, TGraphErrors*> graphs;

  std::cout << GRN <<"Printing resutls: VERBOSE" << FIN << std::endl;
  r->Print("v");

  std::cout << GRN <<"\t * Correlation Matrix" << FIN << std::endl;

  //
  // Correlation matrix
  //
  gStyle->SetOptStat(0) ;
  gStyle->SetPalette(105) ;
  histos2D ["corr_matrix"] = r->correlationHist() ;
  canvases ["corr_matrix"] = new TCanvas ("corr_matrix","Correlation matrix", 600,600);
  
  for (int x =1; x <= histos2D ["corr_matrix"]-> GetXaxis()-> GetNbins(); x++){
    histos2D ["corr_matrix"]->GetXaxis()->SetBinLabel (x, decode_var_names(histos2D ["corr_matrix"]->GetXaxis()->GetBinLabel(x)));
  }
  for (int y =1; y <= histos2D ["corr_matrix"]-> GetYaxis()-> GetNbins(); y++){
    histos2D ["corr_matrix"]->GetYaxis()->SetBinLabel (y, decode_var_names(histos2D ["corr_matrix"]->GetYaxis()->GetBinLabel(y)));
  }

  gStyle->SetPaintTextFormat(".2f");
  canvases ["corr_matrix"] -> SetBottomMargin (0.12);
  canvases ["corr_matrix"] -> SetTopMargin (0.02);
  canvases ["corr_matrix"] -> SetRightMargin (0.02);
  canvases ["corr_matrix"] -> SetLeftMargin (0.12);

  histos2D ["corr_matrix"] -> SetTitle ("");
  histos2D ["corr_matrix"] -> Draw("col");
  histos2D ["corr_matrix"] -> Draw("TEXT45 same");
  
  canvases ["corr_matrix"] -> SaveAs ((plot_dir+"/CorrMatrix.pdf").c_str());

  //
  // Fitted NPs plot!
  //
  std::cout << GRN <<"\t * Nuisance Parameters" << FIN << std::endl;
  
  canvases ["nps"] = new TCanvas ("nps","Nuisance parameters", 600,600);  
  graphs ["nps"] = new TGraphErrors (systematics.size());

  RooArgList list_of_parameters (r->floatParsFinal());
  std::map <std::string, RooRealVar*> vars;

  std::vector <TString> par_names;
  
  for (int i = 0; i < list_of_parameters.getSize(); i++){
    list_of_parameters[i].Print ();
    //std::cout << GRN << " -> " << list_of_parameters[i].GetName() << " " << list_of_parameters[i]->getVal () << FIN <<std::endl;
    std::string name_par (list_of_parameters[i].GetName());
    vars [name_par] = (RooRealVar*) r->floatParsFinal().find(name_par.c_str());
    // std::cout << GRN << " -> " << name_par << " " << vars[name_par]->getVal () << " " << vars[name_par]->getError() << FIN <<std::endl;
    graphs ["nps"]->SetPoint (i, vars[name_par]->getVal (), i+2);
    graphs ["nps"]->SetPointError (i, vars[name_par]->getError (), 0.);
    par_names.push_back (name_par);
  }

  graphs["nps"]->Draw("apz");

  
  float min_x = -2.5, max_x=7;
  graphs["nps"]->GetXaxis()->SetLimits(min_x,max_x);
  graphs["nps"]->GetYaxis()->SetLimits(0,systematics.size()+2+5);
  graphs["nps"]->SetLineWidth(2);
  graphs["nps"]->SetMarkerSize(1.2);
  graphs["nps"]->SetMarkerStyle(20);
  graphs["nps"]->SetTitle("");
  graphs["nps"]->GetYaxis()->SetLabelSize(0);
  graphs["nps"]->GetYaxis()->SetTickSize(0);

  TLatex latex;
  latex.SetTextSize(0.025);
  
  for (unsigned i = 0; i< par_names.size(); i++){
    TString key = par_names[i];
    Double_t x,y, er_x;
    graphs["nps"]->GetPoint(i,x,y);
    er_x = graphs["nps"]->GetErrorX(i);
    
    latex.DrawLatex (min_x+(max_x-min_x)*0.55, i+2,
		     decode_var_names(key) );
    latex.DrawLatex (min_x+(max_x-min_x)*0.70, i+2,
		     "=" );
    latex.DrawLatex (min_x+(max_x-min_x)*0.75, i+2,
		     Form ("%.1f #pm %.1f",x,er_x ) );
  }

  TBox cl (0-1,3-0.25,0+1,systematics.size()+2.25);
  cl.SetLineWidth(0);
  cl.SetFillStyle(3002);
  cl.SetFillColor (kGray+1);
  cl.Draw();

  TLine l(0,3-0.25,0,systematics.size()+2.25);
  l.SetLineColor(kBlack);
  l.SetLineWidth(1);
  l.SetLineStyle(2);
  l.DrawLine (1,2-0.25,1,2+0.25);
  l.Draw();
  
  
  canvases ["nps"] -> SaveAs ( (plot_dir+"PoI.pdf").c_str() );
  // ModelConfig* mc = (ModelConfig*) w->obj("mc");
  // RooArgSet* nps = (RooArgSet*) mc->GetNuisanceParameters ();
  // TIterator* nps_iter = nps->createIterator();
  // auto np = (RooAbsArg*)nps_iter->Next();
  // while (np)    {
  //   std::cout <<np->getVal() << " " <<np->getError() << std::endl;
						      
  // }
  

  // nps->Print ();
  

}
