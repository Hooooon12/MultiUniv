#ifndef Electron_h
#define Electron_h

#include "Lepton.h"
#include "TString.h"

class Electron: public Lepton{

public:

  Electron();
  ~Electron();

  void SetEnShift(double en_up, double en_down);
  inline double EnShift(int s) const {
    if(s==0) return 1.;
    else if(s>0) return j_En_up;
    else return j_En_down;
  }
  void SetResShift(double res_up, double res_down);
  inline double ResShift(int s) const {
    if(s==0) return 1.;
    else if(s>0) return j_Res_up;
    else return j_Res_down;
  }

  void SetSC(double sceta, double scphi, double sce);
  inline double scEta() const { return j_scEta; }
  inline double scPhi() const { return j_scPhi; }
  inline double scE() const { return j_scE; }
  void SetMVA(double mvaiso, double mvanoiso);
  inline double MVAIso() const { return j_mvaiso; }
  inline double MVANoIso() const { return j_mvanoiso; }

  void SetSelectiveQ(bool isGsfCtfScPixChargeConsistent);
  inline bool SelectiveQ() const {return _isGsfCtfScPixChargeConsistent;}

  void SetUncorrE(double une);
  inline double UncorrE() const { return j_EnergyUnCorr; }
  inline double UncorrPt() const { return Pt() * j_EnergyUnCorr/E(); }

  void SetPassConversionVeto(bool b);
  inline int PassConversionVeto() const { return j_passConversionVeto; }
  void SetNMissingHits(int n);
  inline int NMissingHits() const { return j_NMissingHits; };

  enum EtaRegion{
    IB, OB, GAP, EC
  };
  inline EtaRegion etaRegion(){
    double sceta = fabs(scEta());
    if( sceta < 0.8 ) return IB;
    else if( sceta < 1.444 ) return OB;
    else if( sceta < 1.566 ) return GAP;
    else return EC;
  }
  
  void SetCutBasedIDVariables(
    double Full5x5_sigmaIetaIeta,
    double dEtaSeed,
    double dPhiIn,
    double HoverE,
    double InvEminusInvP,
    double e2x5OverE5x5,
    double e1x5OverE5x5,
    double trackIso,
    double dr03EcalRecHitSumEt,
    double dr03HcalDepth1TowerSumEt
  );
  inline double Full5x5_sigmaIetaIeta() const { return j_Full5x5_sigmaIetaIeta; }
  inline double dEtaSeed() const { return j_dEtaSeed; }
  inline double dPhiIn() const { return j_dPhiIn; }
  inline double HoverE() const { return j_HoverE; }
  inline double InvEminusInvP() const { return j_InvEminusInvP; }
  inline double e2x5OverE5x5() const { return j_e2x5OverE5x5; }
  inline double e1x5OverE5x5() const { return j_e1x5OverE5x5; }
  inline double TrkIso() const {return j_trkiso; }
  inline double dr03EcalRecHitSumEt() const { return j_dr03EcalRecHitSumEt; }
  inline double dr03HcalDepth1TowerSumEt() const { return j_dr03HcalDepth1TowerSumEt; }

  void SetIDBit(unsigned int idbit);

  enum Selector {
    POG_CB_VETO = 1<< 0,
    POG_CB_LOOSE = 1<< 1,
    POG_CB_MEDIUM = 1<< 2,
    POG_CB_TIGHT = 1<< 3,
    POG_MVA_ISO_WP80 = 1<< 4,
    POG_MVA_ISO_WP90 = 1<< 5,
    POG_MVA_ISO_WPHZZ = 1<< 6,
    POG_MVA_ISO_WPLOOSE = 1<< 7,
    POG_MVA_NOISO_WP80 = 1<< 8,
    POG_MVA_NOISO_WP90 = 1<< 9,
    POG_MVA_NOISO_WPLOOSE = 1<< 10,
    POG_HEEP = 1<< 11
  };

  inline bool PassSelector( unsigned int s ) const { return (j_IDBit & s)==s; }

  inline bool passVetoID()   const {return PassSelector(POG_CB_VETO); }
  inline bool passLooseID()  const {return PassSelector(POG_CB_LOOSE); }
  inline bool passMediumID() const {return PassSelector(POG_CB_MEDIUM); }
  inline bool passTightID()  const {return PassSelector(POG_CB_TIGHT); }
  inline bool passMVAID_noIso_WP80() const {return PassSelector(POG_MVA_NOISO_WP80); }
  inline bool passMVAID_noIso_WP90() const {return PassSelector(POG_MVA_NOISO_WP90); }
  inline bool passMVAID_iso_WP80() const {return PassSelector(POG_MVA_ISO_WP80); }
  inline bool passMVAID_iso_WP90() const {return PassSelector(POG_MVA_ISO_WP90); }
  inline bool passHEEPID() const {return PassSelector(POG_HEEP); }

  bool Pass_SUSYMVAWP(TString wp);
  bool Pass_SUSYTight();
  bool Pass_SUSYLoose();

  void SetRelPFIso_Rho(double r);
  double EA();

  //==== ID
  bool PassID(TString ID);
  bool Pass_TESTID();

  bool Pass_CutBasedTightNoIso();
  bool Pass_CutBasedTightVetoIso();
  bool Pass_CutBasedMediumNoIso();
  bool Pass_CutBasedLooseNoIso();
  bool Pass_CutBasedVetoNoIso();
  bool Pass_CutBasedLoose();
  bool Pass_CutBasedVeto();
  void SetRho(double r);
  inline double Rho() const { return j_Rho; }

  bool isCutBasedTightIso(); // for ABCD method
  bool isCutBasedMediumIso(); // for ABCD method
  bool isAntiIso(TString ID,  int syst=0); // for ABCD method

private:

  double j_En_up;
  double j_En_down;
  double j_Res_up;
  double j_Res_down;
  double j_scEta,j_scPhi, j_scE;
  double j_mvaiso, j_mvanoiso;
  double j_EnergyUnCorr;
  bool j_passConversionVeto;
  bool _isGsfCtfScPixChargeConsistent;
  int j_NMissingHits;
  double j_Full5x5_sigmaIetaIeta, j_dEtaSeed, j_dPhiIn, j_HoverE, j_InvEminusInvP, j_e2x5OverE5x5, j_e1x5OverE5x5, j_trkiso, j_dr03EcalRecHitSumEt, j_dr03HcalDepth1TowerSumEt;
  unsigned int j_IDBit;
  double j_RelPFIso_Rho;

  double j_Rho;

  ClassDef(Electron,1)

};

#endif
