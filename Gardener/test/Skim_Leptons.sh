#!/bin/bash

# --userflags a,b,c,... to be used inside of analyser
#############################
# userflags for Skim
# DoubleLepTrg
#############################

# options: see mkGardener for more details

# --no_exec :Dry run, job will not be submitted.
# --MonitJob True: default False
# -n : number of jobs in SNU, it is 999999 whatever number you put in.
# --nTotFiles : number of files to run

for sample in DoubleEG DoubleMuon DYJets10to50_MG DYJets TTLL_powheg WJets_MG WW_pythia WZ_pythia ZZ_pythia 
do
  echo $sample
  ./mkGardener.py --Category SMP -a Skim_Leptons -y 2017 -i $sample  -n 500 --nTotFiles 1  --userflags MetFt,L --skimV 9 --no_exec 
done

#for sample in DoubleEG DoubleMuon DYJets10to50_MG DYJets TT_powheg WJets_MG WW_pythia WZ_pythia ZZ_pythia 
#do
#  echo $sample
#  ./mkGardener.py --Category SMP -a Skim_Leptons -y 2016 -i $sample  -n 500 --nTotFiles 1  --userflags MetFt,L --skimV 9 --no_exec 
#done
