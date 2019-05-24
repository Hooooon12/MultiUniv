{ //JH : extract the Scale Factor
  TFile *file = new TFile("/home/jihkim/MultiUniv/data/Run2Legacy_v1/2017/ID/Muon/Mu_IdIso_runBCDEFGH_TightID_trkIso_QPlus_wonjun_v1.root");

  TH2F *h1 = (TH2F*)file->Get("SF_abseta_pt");

int pt[] = {20,25,30,35,40,45,50,60,120};
double eta[] = {-2.40,-2.10,-1.85,-1.60,-1.40,-1.20,-0.90,-0.60,-0.30,-0.20,0.00,0.20,0.30,0.60,0.90,1.20,1.40,1.60,1.85,2.10,2.40};

for(i=1;i<21;i++){
	for(j=1;j<9;j++){

  Float_t value = h1->GetBinContent(i,j);
  Float_t error = h1->GetBinError(i,j);
  cout << eta[i-1] << "\t" << eta[i] << "\t" << pt[j-1] << "\t" << pt[j] << "\t" << value << "\t" << error << endl;
}
}
}
