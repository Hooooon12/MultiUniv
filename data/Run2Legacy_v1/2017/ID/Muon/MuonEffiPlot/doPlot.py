import argparse
import os
import commands as cmd
import libPython.MuonID_scaleFactors as muon_sf

basedir = os.getcwd()

parser = argparse.ArgumentParser(description='Draw muon efficiency plots')
parser.add_argument('--effi', default=None, nargs='*', help='put the txt file to draw [optional]')
parser.add_argument('--lumi', default=41.9, help='put your lumi [default = 41.9 fb^-1]')
args = parser.parse_args()

##################################################################################################

if args.effi == None:

	ls = cmd.getoutput("ls | grep txt$")
	files = ls.split('\n')

	print "=================== Making plots for: ====================="
	print ls
	print

	for txt in files: muon_sf.doMUON_SFs(basedir+'/'+txt,args.lumi)

elif args.effi:

	print "=================== Making plots for: ====================="
	for effi in args.effi: print effi
	print

	for effi in args.effi: muon_sf.doMUON_SFs(basedir+'/'+effi,args.lumi)

