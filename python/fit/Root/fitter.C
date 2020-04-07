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

  //
  // Output of the parameters!
  //
  std::map <std::string, TCanvas*> canvases;
  std::map <std::string, TH2*> histos2D;

  std::cout << GRN <<"Printing resutls: VERBOSE" << FIN << std::endl;
  r->Print("v");


  // Correlation matrix
  gStyle->SetOptStat(0) ;
  gStyle->SetPalette(1) ;
  histos2D ["corr_matrix"] = r->correlationHist() ;
  canvases ["corr_matrix"] = new TCanvas ("corr_matrix","Correlation matrix", 600,600);
  histos2D ["corr_matrix"] -> Draw("colz");
  canvases ["corr_matrix"] -> SaveAs ((plot_dir+"/CorrMatrix.pdf").c_str());
  
  // std::cout << GRN <<"MEASURE!" << FIN << std::endl;
  // MakeModelAndMeasurementFast( meas );
  

  
  

  // //// 
  // //// Test plot
  // ////
  // TCanvas* c_test = new TCanvas("test","test", 400,400);
  // RooPlot* frame = w.var("t")->frame() ;
  // roohistos["data"]->plotOn(frame) ;
  // w.pdf("model")->plotOn(frame) ;  
  // frame->Draw();
  // c_test->Draw();
  // c_test->SaveAs ("test.pdf"); 







}
