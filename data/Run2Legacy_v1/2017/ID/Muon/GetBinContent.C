{ //JH : extract the efficiency from *.root files to *.txt files
  TString filepath = "/home/jihkim/MultiUniv/data/Run2Legacy_v1/2017/ID/Muon/"; //JH : put the current directory
  TString files[] = {"Mu_IdIso_runBCDEFGH_TightID_trkIso_QPlus_wonjun_v1", "Mu_IdIso_runBCDEFGH_TightID_trkIso_QMinus_wonjun_v1", "Mu_TrigEff_runBCDEFGH_LeadMu17_QPlus_wonjun_v1", "Mu_TrigEff_runBCDEFGH_LeadMu17_QMinus_wonjun_v1", "Mu_TrigEff_runBCDEFGH_TailMu8_QPlus_wonjun_v1", "Mu_TrigEff_runBCDEFGH_TailMu8_QMinus_wonjun_v1"}; //JH : put the effi files name

for(k=0;k<4;k++){ //JH : the first 4 files starts from pt20...


  TFile *file = new TFile(filepath+files[k]+".root");

  TH2F *h1 = (TH2F*)file->Get("muonEffi_data_eta_pt");
  TH2F *h2 = (TH2F*)file->Get("muonEffi_mc_eta_pt");

int pt[] = {20,25,30,35,40,45,50,60,120};
double eta[] = {-2.40,-2.10,-1.85,-1.60,-1.40,-1.20,-0.90,-0.60,-0.30,-0.20,0.00,0.20,0.30,0.60,0.90,1.20,1.40,1.60,1.85,2.10,2.40};

ofstream out(files[k]+".txt");

for(i=1;i<21;i++){
	for(j=1;j<9;j++){

  Float_t value_data = h1->GetBinContent(i,j);
  Float_t error_data = h1->GetBinError(i,j);
//if (error_data > 0.1) error_data=0.05; /////// Use this if you want to handle the error
  Float_t value_mc = h2->GetBinContent(i,j);
  Float_t error_mc = h2->GetBinError(i,j);
//if (error_mc > 0.1) error_mc=0.05; ///////
  out << eta[i-1] << "\t" << eta[i] << "\t" << pt[j-1] << "\t" << pt[j] << "\t" << value_data << "\t" << error_data << "\t" << value_mc << "\t" << error_mc << "\t-1" << "\t-1" << "\t-1" << "\t-1" << endl;
}
}
out.close();
}


for(k=4;k<6;k++){ //JH : the last two files starts from pt10...


  TFile *file = new TFile(filepath+files[k]+".root");

  TH2F *h1 = (TH2F*)file->Get("muonEffi_data_eta_pt");
  TH2F *h2 = (TH2F*)file->Get("muonEffi_mc_eta_pt");

int pt2[] = {10,15,20,25,30,35,40,45,50,60,120};
double eta2[] = {-2.40,-2.10,-1.85,-1.60,-1.40,-1.20,-0.90,-0.60,-0.30,-0.20,0.00,0.20,0.30,0.60,0.90,1.20,1.40,1.60,1.85,2.10,2.40};

ofstream out(files[k]+".txt");

for(i=1;i<21;i++){
	for(j=1;j<11;j++){

  Float_t value_data = h1->GetBinContent(i,j);
  Float_t error_data = h1->GetBinError(i,j);
//if (error_data > 0.1) error_data=0.05; //////////
  Float_t value_mc = h2->GetBinContent(i,j);
  Float_t error_mc = h2->GetBinError(i,j);
//if (error_mc > 0.1) error_mc=0.05; /////////
  out << eta2[i-1] << "\t" << eta2[i] << "\t" << pt2[j-1] << "\t" << pt2[j] << "\t" << value_data << "\t" << error_data << "\t" << value_mc << "\t" << error_mc << "\t-1" << "\t-1" << "\t-1" << "\t-1" << endl;
}
}
out.close();
}

}
