#!/bin/bash
argfile=config_d_hydro.xml
export ARCH=lnx64
export DHSDELFT_LICENSE_FILE="${D3D_HOME}"
export D3D_HOME=/opt/delft3d_4.04.00
exedir=/opt/delft3d_4.04.00/lnx64/bin/

export LD_LIBRARY_PATH=${D3D_HOME}/lnx64/lib:$PATH
# export PATH=$exedir:$PATH
export PATH=${D3D_HOME}/lnx64/bin:$PATH
# Please do not put 'rm delft3d.log' due to unexpected behaviour
# this line creates a new clean log file upon restart
echo '' >> delft3d.log
$exedir/d_hydro $argfile

