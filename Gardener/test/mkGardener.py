#!/usr/bin/python

import os,sys,time
#import os.path
import argparse
import datetime
import random
#import importlib

from CommonPyTools.getEvn import *
from CommonPyTools.CheckJobStatus import *
from CommonPyTools.TimeTools import *
#sys.path.insert(0,'../../data/python')
from CommonPyTools.DataSample.SampleDef import *

parser = argparse.ArgumentParser(description='SKFlat Command')
parser.add_argument('-a', dest='Analyzer', default="")
parser.add_argument('-i', dest='InputSampleKey', default="")
parser.add_argument('-p', dest='DataPeriod', default="ALL")
parser.add_argument('-l', dest='InputSampleKeyList', default="")
parser.add_argument('-n', dest='NJobs', default=1, type=int)
parser.add_argument('-o', dest='Outputdir', default="")
parser.add_argument('-q', dest='Queue', default="fastq")
parser.add_argument('-y', dest='Year', default="2017")
parser.add_argument('--InSkim', dest='InSkim', default="")
parser.add_argument('--no_exec', action='store_true')
parser.add_argument('--userflags', dest='Userflags', default="")
parser.add_argument('--skimV', dest='skimV', default="0")
parser.add_argument('--nTotFiles', dest='nTotFiles', default=0, type=int)
parser.add_argument('--MonitJob', dest='MonitJob', default=False, type=bool)
parser.add_argument('--Category', dest='Category', default="SMP")

args = parser.parse_args()
print '=================================================================='
print "Let's go for",SKFlatV,"Skimming "
print '=================================================================='
## make flags
Userflags = []
if args.Userflags != "":
  Userflags = (args.Userflags).split(',')

## Add Abosolute path for outputdir
if args.Outputdir!='':
  if args.Outputdir[0]!='/':
    args.Outputdir = os.getcwd()+'/'+args.Outputdir

## TimeStamp

# 1) dir/file name style
JobStartTime = datetime.datetime.now()
timestamp =  JobStartTime.strftime('%Y_%m_%d_%H%M%S')
# 2) log style
JobStartTime = datetime.datetime.now()
string_JobStartTime =  JobStartTime.strftime('%Y-%m-%d %H:%M:%S')
string_ThisTime = ""


if SKFlatLogEmail=='':
  print '[mkGardener.py] Put your email address in setup.sh'
  exit()
SendLogToWeb = True
if SKFlatLogWeb=='' or SKFlatLogWebDir=='':
  SendLogToWeb = False

if IsKISTI:
  HOSTNAME = "KISTI"
if IsSNU:
  HOSTNAME = "SNU"
if IsKNU:
  HOSTNAME = "KNU"

## Is Skim run?
IsSKim = "Skim" in args.Analyzer
if IsSKim:
  if IsSNU:
    print  "Skim in SNU setting NJobs = 999999 !!!!!!!!!!!"
    args.NJobs = 999999
  elif IsKISTI:
    print "Skim in Kisti"
  else:
    print "Skimming in ", HOSTNAME, "is not prepared kkk"
    exit()



## Machine-dependent variables
if IsKNU:
  args.Queue = "cms"

## Make Sample List

DataPeriods = DataPeriods(args.Year)

SAMPLE_DATA_DIR = SampleDataDir(args.Year)
ProductionKey = SKFlatV+'_'+args.Year
print 'Productions key:',ProductionKey

InputSamples = {}
StringForHash = ""

##############################
# Dump Input Sample list
##############################
## When using list
if args.InputSampleKeyList is not "":
  lines = open(args.InputSampleKeyList)
  for line in lines:
    if "#" in line:
      continue
    line = line.strip('\n')
    #TODO MC case put the Sample name instead of key name
    InputSamples[line]=line
    StringForHash += line
else:
  if args.InputSampleKey in InputSample_Data:
    if args.DataPeriod=="ALL":
      print args.InputSampleKey, args.Year,'ALL', DataPeriods
      for period in DataPeriods:
	InputSamples[args.InputSampleKey+":"+period]={'key':args.InputSampleKey}
        StringForHash += args.InputSampleKey+":"+period
    elif args.DataPeriod in DataPeriods:
      print InputSampleKey, args.Year, args.DataPeriod
      InputSamples[args.InputSampleKey+":"+args.DataPeriod]={'key':args.InputSampleKey}
      StringForHash += args.InputSampleKey+":"+args.DataPeriod
  else:
    print 'File to import', Productions[args.Category][ProductionKey]['MC']
    #importlib.import_module(Productions[args.Category][ProductionKey]['MC'])
    #cmd = SKFlat_WD + Productions[args.Category][ProductionKey]['MC']
    #cmd = 'MCsamples : '+Productions[args.Category][ProductionKey]['MC']
    cmd = 'from '+Productions[args.Category][ProductionKey]['MC'] +' import *'
    exec(cmd, globals())
    #SampleInfo = __import__(Productions[args.Category][ProductionKey]['MC'])
    #SampleName = getattr(SampleInfo, MCsamples)
    #print sampleInfo
    #print sampleName[args.InputSampleKey]['name']
    #print sampleInfo[args.InputSampleKey]['name']
    InputSamples[sampleInfo[args.InputSampleKey]['name']]={'key':args.InputSampleKey}
    StringForHash += args.InputSampleKey
FileRangesForEachSample = []

print 'InputSamples', InputSamples  
####################################
# Get Random Number for webdir
####################################

random.seed(StringForHash)
RandomNumber = random.random()
str_RandomNumber = str(RandomNumber).replace('0.','')
webdirname = timestamp+"_"+str_RandomNumber
webdirpathbase = SKFlatRunlogDir+'/www/SKFlatAnalyzerJobLogs/'+webdirname

## If KISTI, compress files
if IsKISTI:
  cwd = os.getcwd()
  os.chdir(SKFlat_WD)
  os.system('tar --exclude=data/'+SKFlatV+'/Sample -czf '+str_RandomNumber+'_data.tar.gz data/'+SKFlatV+'/')
  os.system('tar -czf '+str_RandomNumber+'_lib.tar.gz lib/*')
  os.chdir(cwd)




############################
## Loop over samples
############################

SampleFinishedForEachSample = []
PostJobFinishedForEachSample = []
BaseDirForEachSample = []

for InputSample in InputSamples:

  NJobs = args.NJobs

  SampleFinishedForEachSample.append(False)
  PostJobFinishedForEachSample.append(False)

  ## Global Varialbes

  IsDATA = False
  DataPeriod = ""
  print 'InputSample', InputSample
  if ":" in InputSample:
    IsDATA = True
    #tmp = InputSample
    #InputSample = tmp.split(":")[0]
    DataPeriod = InputSample.split(":")[1]
    print 'DataPeriod', DataPeriod

  InSkimString = args.InSkim

  ## Prepare RunDir

  base_rundir = SKFlatRunlogDir+'/'+args.Analyzer+'_'+'Y'+args.Year+'_'+InputSamples[InputSample]['key']
  if IsDATA:
    base_rundir = base_rundir + '_'+DataPeriod
  if InSkimString !="":
    base_rundir = base_rundir + '_'+InSkimString
    #base_rundir = SKFlatRunlogDir+'/'+args.Analyzer+'_'+timestamp+'_'+'Y'+args.Year+'_'+InSkimString+'_'+InputSamples[InputSample]['key']
  for flag in Userflags:
    base_rundir += '_'+flag
  #base_rundir += '_'+HOSTNAME
  base_rundir = base_rundir+'_v'+args.skimV+"/"
  print "base_rundir: ", base_rundir
  if os.path.isdir(base_rundir):
    print 'base_rundir already exists exiting... remove or mv this directory to run again'
    exit()

  os.system('mkdir -p '+base_rundir)
  os.system('mkdir -p '+base_rundir+'/output/')

  ## Set Output directory
  ### if args.Outputdir is not set, go to default setting
  FinalOutputPath = args.Outputdir
  if args.Outputdir=="":
    if InSkimString == "":
      FinalOutputPath = Productions[args.Category][ProductionKey]['SkimDir']+'/'
      #FinalOutputPath = SKFlatOutputDir+'/'+SKFlatV+'/'+args.Analyzer+'/'+args.Year+'/'
    else:
      FinalOutputPath = Productions[args.Category][ProductionKey]['SkimDir']+'/'+InSkimString
      #FinalOutputPath = SKFlatOutputDir+'/'+SKFlatV+'/'+args.Analyzer+'/'+args.Year+'/'+InSkimString
    IsFirstFlag=True
    for flag in Userflags:
      if IsFirstFlag:
        IsFirstFlag=False
	if InSkimString == "":
          FinalOutputPath += flag
	else:
          FinalOutputPath += '_'+flag
      else:
        FinalOutputPath += '_'+flag
    #FinalOutputPath +='/'+InputSample+'/'
    FinalOutputPath +='_v'+args.skimV+'/'
  os.system('mkdir -p '+FinalOutputPath)
  print 'FinalOutputPath', FinalOutputPath



  ## Copy shared library file

  if IsKISTI:
    ## In KISTI, we have copy both library and data file
    os.system('cp '+SKFlat_WD+'/'+str_RandomNumber+'_data.tar.gz '+base_rundir+'/data.tar.gz')
    os.system('cp '+SKFlat_WD+'/'+str_RandomNumber+'_lib.tar.gz '+base_rundir+'/lib.tar.gz')
    os.system('cp '+SKFlat_WD+'/lib/CommonPyTools.tar.gz '+base_rundir)
    os.system('cp '+SKFlat_WD+'/lib/CommonTools.tar.gz '+base_rundir)
    os.system('cp '+SKFlat_WD+'/lib/Analyzers.tar.gz '+base_rundir)
    os.system('cp '+SKFlat_WD+'/lib/AnalyzerTools.tar.gz '+base_rundir)
    os.system('cp '+SKFlat_WD+'/lib/DataFormats.tar.gz '+base_rundir)

  else:
    ## Else, we only have to copy libray
    os.system('mkdir -p '+base_rundir+'/lib/')
    os.system('cp '+SKFlat_LIB_PATH+'/* '+base_rundir+'/lib')

  ## Create webdir

  this_webdir = webdirpathbase+'/'+base_rundir.replace(SKFlatRunlogDir,'')
  os.system('mkdir -p '+this_webdir)

  ## If KNU, copy grid cert
  if IsKNU:
    os.system('cp /tmp/x509up_u'+UID+' '+base_rundir)

  ## Get Sample Path

  inputFileList = []

  if InSkimString == "":
    if IsDATA:
      tmpfilepath = SAMPLE_DATA_DIR+'/For'+HOSTNAME+'/'+InputSamples[InputSample]['key']+'_'+DataPeriod+'.txt'
    else:
      tmpfilepath = SAMPLE_DATA_DIR+'/For'+HOSTNAME+'/'+InputSamples[InputSample]['key']+'.txt'

    inputFileList = open(tmpfilepath).readlines()
    os.system('cp '+tmpfilepath+' '+base_rundir+'/input_filelist.txt')
    print 'Sample ROOT file list', tmpfilepath

  else:
    # Skim data list setup
    if IsDATA:
      tmpSkimDir=Productions[args.Category][ProductionKey]['SkimDir']+'/'+InSkimString+'/'+InputSamples[InputSample]['key']+'/'+'period'+DataPeriod+'/'
    else:
      tmpSkimDir=Productions[args.Category][ProductionKey]['SkimDir']+'/'+InSkimString+'/'+InputSample+'/'
    
    print 'Input SkimDir',tmpSkimDir
    input_filelist = open(base_rundir+'/input_filelist','w')
    for dirName, subdirList, fileList in os.walk(tmpSkimDir):
      for aFile in fileList:
	if '.root' in aFile:
	  fileFullPathName = dirName +'/'+aFile
          inputFileList.append(fileFullPathName)
	  input_filelist.write(fileFullPathName+'\n')

    input_filelist.close()


  #print 'inputFiles',inputFileList



  if args.nTotFiles > 0:
    NTotalFiles = args.nTotFiles
  else:
    NTotalFiles = len(inputFileList)

  print "NTotalFiles: ", NTotalFiles

  if NJobs>NTotalFiles:
    NJobs = NTotalFiles

  SubmitOutput = open(base_rundir+'/SubmitOutput.log','w')

  SubmitOutput.write("<SKFlat> NTotalFiles = "+str(NTotalFiles)+'\n')
  SubmitOutput.write("<SKFlat> NJobs = "+str(NJobs)+'\n')
  nfilepjob = int(NTotalFiles/NJobs)
  SubmitOutput.write("<SKFlat> --> # of files per job = "+str(nfilepjob)+'\n')
  nfilepjob_remainder = NTotalFiles-(NJobs)*(nfilepjob)
  if nfilepjob_remainder>=(NJobs):
    SubmitOutput.write('nfilepjob_remainder = '+str(nfilepjob_remainder)+'\n')
    SubmitOutput.write('while, NJobs = '+str(NJobs)+'\n')
    SubmitOutput.write('--> exit'+'\n')
    sys.exit()

  # FileRanges format: [[0,1,2],[3,4,5]]
  FileRanges = []
  temp_end_largerjob = 0
  nfile_checksum = 0
  ## First nfilepjob_remainder jobs will have (nfilepjob+1) files per job
  for it_job in range(0,nfilepjob_remainder):
    FileRanges.append(range(it_job*(nfilepjob+1),(it_job+1)*(nfilepjob+1)))
    temp_end_largerjob = (it_job+1)*(nfilepjob+1)
    nfile_checksum += len(range(it_job*(nfilepjob+1),(it_job+1)*(nfilepjob+1)))
  ## Remaining NJobs-nfilepjob_remainder jobs will have (nfilepjob) files per job
  for it_job in range(0,NJobs-nfilepjob_remainder):
    FileRanges.append(range(temp_end_largerjob+(it_job*nfilepjob),temp_end_largerjob+((it_job+1)*nfilepjob) ))
    nfile_checksum += len(range(temp_end_largerjob+(it_job*nfilepjob),temp_end_largerjob+((it_job+1)*nfilepjob) ))
  SubmitOutput.write('nfile_checksum = '+str(nfile_checksum)+'\n')
  SubmitOutput.write('NTotalFiles = '+str(NTotalFiles)+'\n')
  FileRangesForEachSample.append(FileRanges)

  ## Get xsec and SumW
  this_xsec = 1.;
  this_sumw = 1.;
  if not IsDATA:
    print 'Reading x-section and sumw'
    this_xsec = sampleInfo[InputSamples[InputSample]['key']]['xsec']
    this_sumw = sampleInfo[InputSamples[InputSample]['key']]['Nsum']
    print this_xsec, this_sumw
#### Old method
#    lines_SamplePath = open(SAMPLE_DATA_DIR+'/CommonSampleInfo/'+InputSamples[InputSample]['key']+'.txt').readlines()
#    for line in lines_SamplePath:
#      if line[0]=="#":
#        continue
#      words = line.split()
#      if InputSample==words[0]:
#        this_xsec = words[2]
#        this_sumw = words[4]
#        break
#

  ## Write run script

  if IsKISTI:

    commandsfilename = args.Analyzer+'_'+InputSamples[InputSample]['key']
    if IsDATA:
      commandsfilename += '_'+DataPeriod
    for flag in Userflags:
      commandsfilename += '_'+flag
    run_commands = open(base_rundir+'/'+commandsfilename+'.sh','w')
    print>>run_commands,'''#!/bin/bash
SECTION=`printf %03d $1`
WORKDIR=`pwd`
echo "####  Extracting CommonPyTools ####"
tar -zxvf CommonPyTools.tar.gz
echo "####  Extracting CommonTools ####"
tar -zxvf CommonTools.tar.gz
echo "#### Extracting DataFormats ####"
tar -zxvf DataFormats.tar.gz
echo "####  Extracting AnalyzerTools ####"
tar -zxvf AnalyzerTools.tar.gz
echo "####  Extracting Analyzers ####"
tar -zxvf Analyzers.tar.gz
echo "#### Extracting libraries ####"
tar -zxvf lib.tar.gz
echo "#### Extracting run files ####"
tar -zxvf runFile.tar.gz
echo "#### Extracting data files ####"
tar -zxvf data.tar.gz
echo "#### cmsenv ####"
export CMS_PATH=/cvmfs/cms.cern.ch
source $CMS_PATH/cmsset_default.sh
export SCRAM_ARCH=slc6_amd64_gcc630
cd /cvmfs/cms.cern.ch/slc6_amd64_gcc630/cms/cmssw/CMSSW_9_4_4/src/
eval `scramv1 runtime -sh`
cd -
echo "#### setup root ####"
source /cvmfs/cms.cern.ch/slc6_amd64_gcc630/cms/cmssw/CMSSW_9_4_4/external/slc6_amd64_gcc630/bin/thisroot.sh

export SKFlatV="{0}"
export SKFlat_WD=`pwd`
export SKFlat_LIB_PATH=$SKFlat_WD/lib/
export DATA_DIR=data/$SKFlatV
export ROOT_INCLUDE_PATH=$ROOT_INCLUDE_PATH:$SKFlat_WD/DataFormats/include/:$SKFlat_WD/Analyzers/include/:$SKFlat_WD/AnalyzerTools/include/:$SKFlat_WD/CommonTools/include/
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$SKFlat_LIB_PATH

SumNoAuth=999
Trial=0

while [ "$SumNoAuth" -ne 0 ]; do

  if [ "$Trial" -gt 9999 ]; then
    break
  fi

  echo "#### running ####"
  echo "root -l -b -q run_${{SECTION}}.C"
  root -l -b -q run_${{SECTION}}.C 2> err${{SECTION}}.log
  NoAuthError_Open=`grep "Error in <TNetXNGFile::Open>" err${{SECTION}}.log -R | wc -l`
  NoAuthError_Close=`grep "Error in <TNetXNGFile::Close>" err${{SECTION}}.log -R | wc -l`

  SumNoAuth=$(($NoAuthError_Open + $NoAuthError_Close))

  if [ "$SumNoAuth" -ne 0 ]; then
    echo "SumNoAuth="$SumNoAuth
    echo "AUTH error occured.. running again in 30 seconds.."
    Trial=$((Trial+=1))
    sleep 30
  fi

done

cat err${{SECTION}}.log >&2
'''.format(SKFlatV)
    run_commands.close()

    submit_command = open(base_rundir+'/submit.jds','w')
    if IsUI10:
      print>>submit_command,'''executable = {3}.sh
universe   = vanilla
arguments  = $(Process)
requirements = OpSysMajorVer == 6
log = condor.log
getenv     = False
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
output = job_$(Process).log
error = job_$(Process).err
transfer_input_files = {0}, {1}, {4}, {5}, {6}, {7}, {8}, {9}
transfer_output_remaps = "hists.root = output/hists_$(Process).root"
queue {2}
'''.format(base_rundir+'/runFile.tar.gz', base_rundir+'/lib.tar.gz',str(NJobs), commandsfilename, base_rundir+'/data.tar.gz', base_rundir+'/Analyzers.tar.gz', base_rundir+'/AnalyzerTools.tar.gz', base_rundir+'/DataFormats.tar.gz',base_rundir+'/CommonTools.tar.gz',base_rundir+'/CommonPyTools.tar.gz')
      submit_command.close()
    if IsUI20:
      print>>submit_command,'''executable = {3}.sh
universe   = vanilla
requirements = ( HasSingularity == true )
arguments  = $(Process)
log = condor.log
getenv     = False
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
output = job_$(Process).log
error = job_$(Process).err
transfer_input_files = {0}, {1}, {4}, {5}, {6}, {7}, {8}, {9}
accounting_group=group_cms
+SingularityImage = "/cvmfs/singularity.opensciencegrid.org/opensciencegrid/osgvo-el6:latest"
+SingularityBind = "/cvmfs, /cms, /share"
transfer_output_remaps = "hists.root = output/hists_$(Process).root"
queue {2}
'''.format(base_rundir+'/runFile.tar.gz', base_rundir+'/lib.tar.gz',str(NJobs), commandsfilename, base_rundir+'/data.tar.gz', base_rundir+'/Analyzers.tar.gz', base_rundir+'/AnalyzerTools.tar.gz', base_rundir+'/DataFormats.tar.gz',base_rundir+'/CommonTools.tar.gz',base_rundir+'/CommonPyTools.tar.gz')
      submit_command.close()



  CheckTotalNFile=0
  for it_job in range(0,len(FileRanges)):
    time.sleep(0.3)

    #print "["+str(it_job)+"th]",
    #print FileRanges[it_job],
    #print " --> "+str(len(FileRanges[it_job]))

    CheckTotalNFile = CheckTotalNFile+len(FileRanges[it_job])

    thisjob_dir = base_rundir+'/job_'+str(it_job)+'/'

    runfunctionname = "run"
    libdir = (base_rundir+'/lib').replace('///','/').replace('//','/')+'/'
    #print "libdir: ",libdir
    runCfileFullPath = ""
    if IsKISTI:
      libdir = './lib/'
      runfunctionname = "run_"+str(it_job).zfill(3)
      runCfileFullPath = base_rundir+'/run_'+str(it_job).zfill(3)+'.C'
    else:
      os.system('mkdir -p '+thisjob_dir)
      runCfileFullPath = thisjob_dir+'run.C'

    IncludeLine  = 'R__LOAD_LIBRARY(libPhysics.so)\n'
    IncludeLine += 'R__LOAD_LIBRARY(libTree.so)\n'
    IncludeLine += 'R__LOAD_LIBRARY(libHist.so)\n'
    IncludeLine += 'R__LOAD_LIBRARY({0}libCommonTools.so)\n'.format(libdir)
    IncludeLine += 'R__LOAD_LIBRARY({0}libDataFormats.so)\n'.format(libdir)
    IncludeLine += 'R__LOAD_LIBRARY({0}libAnalyzerTools.so)\n'.format(libdir)
    IncludeLine += 'R__LOAD_LIBRARY({0}libAnalyzers.so)\n'.format(libdir)
    IncludeLine += 'R__LOAD_LIBRARY(/cvmfs/cms.cern.ch/slc6_amd64_gcc630/external/lhapdf/6.2.1-fmblme/lib/libLHAPDF.so)\n'
    #IncludeLine = 'R__LOAD_LIBRARY({1}/{0}_C.so)'.format(args.Analyzer, libdir)

    out = open(runCfileFullPath, 'w')
    print>>out,'''{3}

void {2}(){{

  {0} m;

  m.SetTreeName("recoTree/SKFlat");
'''.format(args.Analyzer, libdir, runfunctionname, IncludeLine)

    if IsDATA:
      out.write('  m.IsDATA = true;\n')
      out.write('  m.DataStream = "'+InputSamples[InputSample]['key']+'";\n')
    else:
      out.write('  m.MCSample = "'+InputSamples[InputSample]['key']+'";\n');
      out.write('  m.IsDATA = false;\n')
      out.write('  m.xsec = '+str(this_xsec)+';\n')
      out.write('  m.sumW = '+str(this_sumw)+';\n')

    out.write('  m.DataYear = '+str(args.Year)+';\n')

    if len(Userflags)>0:
      out.write('  m.Userflags = {\n')
      for flag in Userflags:
        out.write('    "'+flag+'",\n')
      out.write('  };\n')

    for it_file in FileRanges[it_job]:
      thisfilename = inputFileList[it_file].strip('\n')
      out.write('  m.AddFile("'+thisfilename+'");\n')

#TODO
    if IsSKim:
      if IsSNU:
        tmp_inputFilename = inputFileList[ FileRanges[it_job][0] ].strip('\n')
	#print 'tmp_inputFilename', tmp_inputFilename
	#print 'InputSample',InputSample
	#if "_" in InputSample:
	#  delemeter = InputSample.split('_')[0]+'_'
	#  chunkedInputFileName = delemeter+tmp_inputFilename.split(delemeter)[1]
	#else:
	#  chunkedInputFileName = InputSample+tmp_inputFilename.split(InputSample)[1]
	if IsDATA:
	  chunkedInputFileName = InputSamples[InputSample]['key']+tmp_inputFilename.split(InputSamples[InputSample]['key'])[1]
	else:
	  chunkedInputFileName = InputSample+tmp_inputFilename.split(InputSample)[1]

	#print 'chumkedInputFileName',chunkedInputFileName

        ## /data7/DATA/SKFlat/v949cand2_2/2017/DATA/SingleMuon/periodB/181107_231447/0000
        ## /data7/DATA/SKFlat/v949cand2_2/2017/MC/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/181108_152345/0000/SKFlatNtuple_2017_MC_100.root
        #dir1 = '/data7/DATA/SKFlat/'+SKFlatV+'/'+args.Year+'/'
        #dir2 = dir1
        #if IsDATA:
        #  dir1 += "DATA/"
        #  dir2 += "DATA_"+args.Analyzer+"/"
        #else:
        #  dir1 += "MC/"
        #  dir2 += "MC_"+args.Analyzer+"/"

        #skimoutname = tmp_filename.replace(dir1,dir2)

        #tmp_filename = skimoutname.split('/')[-1]
	#outPath = skimoutname.replace(tmp_filename,'')
	#print "outPath", outPath
	#outPath = FinalOutputPath + '/'+InSkimString
	out_Path_FileName = FinalOutputPath+'/'+chunkedInputFileName
	out_FileName = out_Path_FileName.split('/')[-1]
	out_Path          = out_Path_FileName.replace(out_FileName,'')
	#print 'out_Path_FileName',out_Path_FileName
	#print 'out_Path',out_Path
	#print 'out_FileName',out_FileName
	#fileName=InSkimString+str(it_job).zfill(3)+'root'
        os.system('mkdir -p '+ out_Path)
        out.write('  m.SetOutfilePath("'+out_Path_FileName+'");\n')
      else:
        out.write('  m.SetOutfilePath("hists.root");\n')

    else:
      if IsKISTI:
        out.write('  m.SetOutfilePath("hists.root");\n')
      else:
        out.write('  m.SetOutfilePath("'+thisjob_dir+'/hists.root");\n')


    out.write('  m.Init();'+'\n')
    if not IsSKim:
      out.write('  m.initializeAnalyzerTools();'+'\n')
    print>>out,'''  m.initializeAnalyzer();
  m.Loop();

  m.WriteHist();

}'''
    out.close()

    if IsSNU:
      run_commands = open(thisjob_dir+'commands.sh','w')
      print>>run_commands,'''cd {0}
echo "[mkGardener.py] Okay, let's run the analysis"
root -l -b -q run.C
'''.format(thisjob_dir)
      run_commands.close()

      jobname = 'job_'+str(it_job)+'_'+args.Analyzer
      cmd = 'qsub -V -q '+args.Queue+' -N '+jobname+' -wd '+thisjob_dir+' commands.sh '

      if not args.no_exec:
        cwd = os.getcwd()
        os.chdir(thisjob_dir)
	print 'submitting',cmd
        os.system(cmd+' > submitlog.log')
        os.chdir(cwd)
      else:
	print 'Dry-Run: cmd',cmd
      sublog = open(thisjob_dir+'/submitlog.log','a')
      sublog.write('\nSubmission command was : '+cmd+'\n')
      sublog.close()

    if IsKNU:
      run_commands = open(thisjob_dir+'commands.sh','w')
      print>>run_commands,'''cd {0}
cp ../x509up_u{1} /tmp/
echo "[mkGardener.py] Okay, let's run the analysis"
root -l -b -q run.C 1>stdout.log 2>stderr.log
'''.format(thisjob_dir,UID)
      run_commands.close()

      jobname = 'job_'+str(it_job)+'_'+args.Analyzer
      cmd = 'qsub -V -q '+args.Queue+' -N '+jobname+' commands.sh'

      if not args.no_exec:
        cwd = os.getcwd()
        os.chdir(thisjob_dir)
        os.system(cmd+' > submitlog.log')
        os.chdir(cwd)
      sublog = open(thisjob_dir+'/submitlog.log','a')
      sublog.write('\nSubmission command was : '+cmd+'\n')
      sublog.close()

  if IsKISTI:

    cwd = os.getcwd()
    os.chdir(base_rundir)
    os.system('tar -czf runFile.tar.gz run_*.C')
    cmd = 'condor_submit submit.jds'
    if not args.no_exec:
      os.system(cmd)
    else:
      print 'Dry run, command "'+cmd+'" will be excuted for real run at '+ base_rundir
    os.chdir(cwd)

  else:

    if args.no_exec:
      continue

    ## Write Kill Command

    KillCommand = open(base_rundir+'/Script_JobKill.sh','w')
    for it_job in range(0,len(FileRanges)):
      thisjob_dir = base_rundir+'/job_'+str(it_job)+'/'
      jobid = GetJobID(thisjob_dir, args.Analyzer, it_job, HOSTNAME)
      KillCommand.write('qdel '+jobid+' ## job_'+str(it_job)+' ##\n')
    KillCommand.close()

  SubmitOutput.write('Job submitted at '+string_JobStartTime+'\n')

### remove tar.gz
os.system('rm -f '+SKFlat_WD+'/'+str_RandomNumber+'_data.tar.gz')
os.system('rm -f '+SKFlat_WD+'/'+str_RandomNumber+'_lib.tar.gz')



print '##################################################'
print 'Submission Finished'
print '- Analyzer = '+args.Analyzer
print '- InSkim = '+args.InSkim
print '- InputSamples =',
print InputSamples
print '- NJobs = '+str(NJobs)
print '- Year = '+args.Year
print '- UserFlags =',
print Userflags, args.skimV
if IsSNU or IsKNU:
  print '- Queue = '+args.Queue
print '- output will be send to : '+ out_Path
print '##################################################'

if args.no_exec:
  print "Exiting no_exec run"
  exit()

if not args.MonitJob:
  print 'No monitering job'
  print 'Bye!!!'
  exit()

###########################
### Submittion all done. ##
### Now monitor job      ##
###########################
#
### Loop over samples again
#
#AllSampleFinished = False
#GotError = False
#ErrorLog = ""
#
#try:
#  while not AllSampleFinished:
#
#    if GotError:
#      break
#
#    AllSampleFinished = True
#
#    for it_sample in range(0,len(InputSamples)):
#
#      InputSample = InputSamples[it_sample]
#      SampleFinished = SampleFinishedForEachSample[it_sample]
#      PostJobFinished = PostJobFinishedForEachSample[it_sample]
#
#      if PostJobFinished:
#        continue
#      else:
#        AllSampleFinished = False
#
#      ## Global Varialbes
#
#      IsDATA = False
#      DataPeriod = ""
#      if ":" in InputSample:
#        IsDATA = True
#        tmp = InputSample
#        InputSample = tmp.split(":")[0]
#        DataPeriod = tmp.split(":")[1]
#
#      InSkimString = ""
#      if args.InSkim!="":
#        InSkimString = args.InSkim
#
#      ## Prepare output
#      ## This should be copied from above
#
#      if InSkimString != "":
#        base_rundir = SKFlatRunlogDir+'/'+args.Analyzer+'_'+timestamp+'_'+'Y'+args.Year+'_'+InSkimString+'_'+InputSample
#      else:
#        base_rundir = SKFlatRunlogDir+'/'+args.Analyzer+'_'+timestamp+'_'+'Y'+args.Year+'_'+InputSample
#
#      if IsDATA:
#        base_rundir = base_rundir+'_'+DataPeriod
#
#      for flag in Userflags:
#        base_rundir += '_'+flag
#      #base_rundir += '_'+HOSTNAME
#      base_rundir = base_rundir+'_v'+args.skimV+"/"
#
#      this_webdir = webdirpathbase+'/'+base_rundir.replace(SKFlatRunlogDir,'')
#
#      if not SampleFinished:
#
#        ## This sample was not finished in the previous monitoring
#        ## Monitor again this time
#
#        ThisSampleFinished = True
#
#        ## Write Job status until it's done
#
#        statuslog = open(base_rundir+'/JobStatus.log','w')
#        statuslog.write('Job submitted at '+string_JobStartTime+'\n')
#        statuslog.write('JobNumber\t| Status\n')
#
#        ToStatuslog = []
#        n_eventran = 0
#        finished = []
#        EventDone = 0
#        EventTotal = 0
#
#        TotalEventRunTime = 0
#        MaxTimeLeft = 0
#        MaxEventRunTime = 0
#
#        FileRanges = FileRangesForEachSample[it_sample]
#
#        for it_job in range(0,len(FileRanges)):
#
#          thisjob_dir = base_rundir+'/'
#          #if IsKISTI:
#           # thisjob_dir = base_rundir
#
#          this_status = ""
#          this_status = CheckJobStatus(thisjob_dir, args.Analyzer, it_job, HOSTNAME)
#
#          if "ERROR" in this_status:
#            GotError = True
#            statuslog.write("#### ERROR OCCURED ####\n")
#            statuslog.write(this_status+'\n')
#            ErrorLog = this_status
#            break
#
#          if "FINISHED" not in this_status:
#            ThisSampleFinished = False
#
#          outlog = ""
#          if "FINISHED" in this_status:
#            finished.append("Finished")
#
#            EventInfo = this_status.split()[1].split(':')
#
#	    # Finished status, this is a trick to make Ntotal = NDone
#            this_EventDone = int(EventInfo[2])
#            this_EventTotal = int(EventInfo[2])
#
#            EventDone += this_EventDone
#            EventTotal += this_EventTotal
#
#            #### start
#            line_EventRunTime = this_status.split()[2]+' '+this_status.split()[3]
#            this_jobstarttime = GetDatetimeFromMyFormat(line_EventRunTime)
#            #### end
#            line_EventEndTime = this_status.split()[4]+' '+this_status.split()[5]
#            this_jobendtime   = GetDatetimeFromMyFormat(line_EventEndTime)
#
#            this_diff = this_jobendtime-this_jobstarttime
#            this_EventRunTime = 86400*this_diff.days+this_diff.seconds
#
#            this_TimePerEvent = float(this_EventRunTime)/float(this_EventDone)
#            this_TimeLeft = (this_EventTotal-this_EventDone)*this_TimePerEvent
#
#            TotalEventRunTime += this_EventRunTime
#            MaxTimeLeft = max(MaxTimeLeft,this_TimeLeft)
#            MaxEventRunTime = max(MaxEventRunTime,this_EventRunTime)
#
#          elif "RUNNING" in this_status:
#            outlog = str(it_job)+'\t| '+this_status.split()[1]+' %'
#
#            if len(this_status.split())<3 :
#              SubmitOutput.write('len(this_status.split())<3;; Priting this_status.split()\n')
#              SubmitOutput.write(this_status.split()+'\n')
#
#            EventInfo = this_status.split()[2].split(':')
#
#            this_EventDone = int(EventInfo[1])
#            this_EventTotal = int(EventInfo[2])
#
#            EventDone += this_EventDone
#            EventTotal += this_EventTotal
#
#            line_EventRunTime = this_status.split()[3]+' '+this_status.split()[4]
#            this_jobstarttime = GetDatetimeFromMyFormat(line_EventRunTime)
#            this_diff = datetime.datetime.now()-this_jobstarttime
#            this_EventRunTime = 86400*this_diff.days+this_diff.seconds
#
#            if this_EventDone==0:
#              this_EventDone = 1
#
#            this_TimePerEvent = float(this_EventRunTime)/float(this_EventDone)
#            this_TimeLeft = (this_EventTotal-this_EventDone)*this_TimePerEvent
#
#            TotalEventRunTime += this_EventRunTime
#            MaxTimeLeft = max(MaxTimeLeft,this_TimeLeft)
#            MaxEventRunTime = max(MaxEventRunTime,this_EventRunTime)
#
#            round_this_TimeLeft = round(this_TimeLeft,1)
#            round_this_EventRunTime = round(this_EventRunTime,1)
#
#            outlog += ' ('+str(round_this_EventRunTime)+' s ran, and '+str(round_this_TimeLeft)+' s left)'
#            ToStatuslog.append(outlog)
#            n_eventran += 1
#
#          else:
#            outlog = str(it_job)+'\t| '+this_status
#            ToStatuslog.append(outlog)
#
#          ##---- END it_job loop
#
#        if GotError:
#          ## When error occured, change both Finished/PostJob Flag to True
#          SampleFinishedForEachSample[it_sample] = True
#          PostJobFinishedForEachSample[it_sample] = True
#          break
#
#        for l in ToStatuslog:
#          statuslog.write(l+'\n')
#        statuslog.write('\n==============================================================\n')
#        statuslog.write('HOSTNAME = '+HOSTNAME+'\n')
#        statuslog.write('queue = '+args.Queue+'\n')
#        statuslog.write(str(len(FileRanges))+' jobs submitted\n')
#        statuslog.write(str(n_eventran)+' jobs are running\n')
#        statuslog.write(str(len(finished))+' jobs are finished\n')
#
#        ThisTime = datetime.datetime.now()
#        string_ThisTime =  ThisTime.strftime('%Y-%m-%d %H:%M:%S')
#
#        statuslog.write('EventDone = '+str(EventDone)+'\n')
#        statuslog.write('EventTotal = '+str(EventTotal)+'\n')
#        statuslog.write('EventLeft = '+str(EventTotal-EventDone)+'\n')
#        statuslog.write('TotalEventRunTime = '+str(TotalEventRunTime)+'\n')
#        statuslog.write('MaxTimeLeft = '+str(MaxTimeLeft)+'\n')
#        statuslog.write('MaxEventRunTime = '+str(MaxEventRunTime)+'\n')
#
#        t_per_event = 1
#        if EventDone is not 0:
#          t_per_event = float(TotalEventRunTime)/float(EventDone)
#        statuslog.write('t_per_event = '+str(t_per_event)+'\n')
#
#        EstTime = ThisTime+datetime.timedelta(0, MaxTimeLeft)
#
#        statuslog.write('Estimated Finishing Time : '+EstTime.strftime('%Y-%m-%d %H:%M:%S')+'\n')
#        statuslog.write('Last checked at '+string_ThisTime+'\n')
#        statuslog.close()
#
#        ## copy statuslog to webdir
#        os.system('cp '+base_rundir+'/JobStatus.log '+this_webdir)
#
#        ## This time, it is found to be finished
#        ## Change the flag
#        if ThisSampleFinished:
#          SampleFinishedForEachSample[it_sample] = True
#        ##---- END if finished
#
#      else:
#
#        ## Job was finished in the previous monitoring
#        ## Check if PostJob is also finished
#
#        if not PostJobFinished:
#
#          ## PostJob was not done in the previous monitoring
#          ## Copy output, and change the PostJob flag
#
#
#          ## if Skim, no need to hadd. move on!
#          if IsSKim:
#            PostJobFinishedForEachSample[it_sample] = True
#            continue
#
#          if InSkimString !="":
#            outputname = args.Analyzer+'_'+InSkimString+'_'+InputSample
#	  else:
#            outputname = args.Analyzer+'_'+InputSample
#
#          if IsDATA:
#            outputname += '_'+DataPeriod
#
#          if not GotError:
#            cwd = os.getcwd()
#            os.chdir(base_rundir)
#
#            if IsKISTI:
#              os.system('hadd -f '+outputname+'.root output/*.root >> JobStatus.log')
#              os.system('rm output/*.root')
#            else:
#              os.system('hadd -f '+outputname+'.root job_*/*.root >> JobStatus.log')
#              os.system('rm job_*/*.root')
#
#            ## Final Outputpath
#
#            os.system('mv '+outputname+'.root '+FinalOutputPath)
#            os.chdir(cwd)
#
#          PostJobFinishedForEachSample[it_sample] = True
#
#    if SendLogToWeb:
#
#      os.system('scp -r '+webdirpathbase+'/* '+SKFlatLogWeb+':'+SKFlatLogWebDir)
#      os.system('ssh -Y '+SKFlatLogWeb+' chmod -R 777 '+SKFlatLogWebDir+'/'+args.Analyzer+"*")
#
#    time.sleep(20)
#
#except KeyboardInterrupt:
#  print('interrupted!')
#
### Send Email now
#
#from SendEmail import *
#JobFinishEmail = '''#### Job Info ####
#HOST = {3}
#Analyzer = {0}
#InSkim = {5}
## of Jobs = {4}
#InputSample = {1}
#Output sent to : {2}
#'''.format(args.Analyzer,InputSamples,FinalOutputPath,HOSTNAME,NJobs,args.InSkim)
#JobFinishEmail += '''##################
#Job started at {0}
#Job finished at {1}
#'''.format(string_JobStartTime,string_ThisTime)
#
#if IsSNU or IsKNU:
#  JobFinishEmail += 'Queue = '+args.Queue+'\n'
#
#EmailTitle = '['+HOSTNAME+']'+' Job Summary'
#if GotError:
#  JobFinishEmail = "#### ERROR OCCURED ####\n"+JobFinishEmail
#  JobFinishEmail = ErrorLog+"\n------------------------------------------------\n"+JobFinishEmail
#  EmailTitle = '[ERROR] Job Summary'
#
#if IsKNU:
#  SendEmailbyGMail(USER,SKFlatLogEmail,EmailTitle,JobFinishEmail)
#else:
#  SendEmail(USER,SKFlatLogEmail,EmailTitle,JobFinishEmail)


print "Every process has done, bye!!!"
exit()
