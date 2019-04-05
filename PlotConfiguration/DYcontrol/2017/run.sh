

###################################################################################
#
#            _     _____ _                         ____        _   _             
#           | |   / ____| |                       / __ \      | | (_)            
#  _ __ ___ | | _| (___ | |__   __ _ _ __   ___  | |  | |_ __ | |_ _  ___  _ __  
# | '_ ` _ \| |/ /\___ \| '_ \ / _` | '_ \ / _ \ | |  | | '_ \| __| |/ _ \| '_ \ 
# | | | | | |   < ____) | | | | (_| | |_) |  __/ | |__| | |_) | |_| | (_) | | | |
# |_| |_| |_|_|\_\_____/|_| |_|\__,_| .__/ \___|  \____/| .__/ \__|_|\___/|_| |_|
#                                   | |                 | |                      
#                                   |_|                 |_|                      
#
###################################################################################
# --debug 0 default, 1 INFO, 2 DEBUG
# -q :Queue tamsa1(fastq)
# --dry_run : no execution
# --overWrite : 
# --doBatch
# --doHadd
# --cleanUp
# --onlyVariable=mll


###########################################################################
#            _    _____  _       _                 _   _             
#           | |  |  __ \| |     | |               | | (_)            
#  _ __ ___ | | _| |__) | | ___ | |_    ___  _ __ | |_ _  ___  _ __  
# | '_ ` _ \| |/ /  ___/| |/ _ \| __|  / _ \| '_ \| __| |/ _ \| '_ \ 
# | | | | | |   <| |    | | (_) | |_  | (_) | |_) | |_| | (_) | | | |
# |_| |_| |_|_|\_\_|    |_|\___/ \__|  \___/| .__/ \__|_|\___/|_| |_|
#                                           | |                      
#                                           |_|                      
#
###########################################################################
# --scaleToPlot : default 2.0
# --showIntegralLegend=1 default


python $SKFlat_WD/ShapeAnalysis/scripts/mkShapes.py --pycfg  configuration.py -n 400 --nTotFiles 0  --overWrite --doBatch 
python $SKFlat_WD/ShapeAnalysis/scripts/mkShapes.py --pycfg  configuration.py -n 400 --nTotFiles 0  --overWrite --doHadd --cleanUp
python $SKFlat_WD/ShapeAnalysis/scripts/mkPlot.py --pycfg configuration.py --inputFile=Output_MetFt_L_v0_LL_v0_MuMuOrElEl_v0_hadd_v0_DY/DY.root --onlyVariable=mll --minLogC=1 --maxLogC=1000