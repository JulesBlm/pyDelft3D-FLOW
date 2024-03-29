'''
TODO:
* Make use of sedmor.py and TimeSeries.py to replace text in files
* Make use of D3Dmodel instead of finding files here
'''

import os, fileinput, shutil, copy #, pprint
from numpy import format_float_scientific
import pyd3d.input.mdf as mdf
from pyd3d.utils import formatSci


def stupidReplaceText(filename, new_filename, text_to_find, replacement_text):
    with fileinput.FileInput(filename) as file, open(new_filename, 'w') as outfile:
        for line in file:
            outfile.write(line.replace(text_to_find, replacement_text))

def stupidReplaceTimeBC(template_filename, new_filename, run, init_end_time):
    '''Doesn't read all of the BC file, just looks for times and replaces it there'''
    with open(template_filename,'r') as bc_template, open(new_filename, 'w') as new_bc_file:
        lines = bc_template.readlines()
        records_line_nrs = []

        # Make list of line numbers of lines with 'records'
        for i, line in enumerate(lines):
            if 'records-in-table' in line:
                records_in_table = int(line.split()[1]) # number of records in table
                start_end_line_nrs = (i + 1, i + 1 + records_in_table) # tuple containing first and last line nr's that contain records
                records_line_nrs.append(start_end_line_nrs)

        # Use line numbers of 'records' to add runtime
        for start_line_nr, end_line_nr in records_line_nrs:
            for line_nr in range(start_line_nr, end_line_nr):
                split_line = lines[line_nr].split('  ')
                time = float(split_line[0]) + run * init_end_time
                split_line[0] = formatSci(time) # replace time
                lines[line_nr] = ' ' + '  '.join(value for value in split_line)
                
        new_bc_file.writelines(lines)

# split into more functions
def makeMultipleRuns(template_folder=None, number_of_runs=2, **kwargs):
    """Takes a 'template_folder' and writes 'number_of_runs' new folders with times and some other parameters adjusted for subsequent restarts.
    RunTXT keyword is kind of mangled in subsequent MDF files because the mdf script joins alls runtxt strings

    Examples
    --------
    >>> from pyd3d.input.multipleruns import makeMultipleRuns
    >>> makeMultipleRuns(template_folder='/Users/your_folder_with_runs/D3DModel/Run01', number_of_runs=5)

    
    Parameters
    ----------
    template_folder : str
        Path containing template Delft3D-FLOW model
    
    number_of_runs : int
        Number of succesive runs to repeat this model
    
    Other Parameters
    ----------------

    restId_base : str, optional
        String that is added to "RestId" keyword in all subsequent runs. Only useful if restartId argument is not equal to the .mdf filename in the template folder

    init_MorStt : str, optional
        String containing initial value for Spin-up interval till start of morphological changes 
        ('MorSst' key in .mor file.) is changed to 0 for all subsequent runs by default.
        Default string to replace is '9.0000000e+000'
        
    new_Tlfsmo : float, optional
        Value for new 'Tlfsmo' keyword in .mdf file to write in subsequent models. 0 is the default argument
        Tlfsmo = Time interval to smooth the hydrodynamic boundary conditions

    remove_netcdf : bool, optional
        Flag to omit NetCDF output keywords in .mdf file; False by default

    Restid_timeindex : int, optional
        Manual value for time index to read from map file for restarting
    
    """
    if not template_folder:
        raise Exception('No read folder supplied, aborting')
    elif not os.path.exists(template_folder):
        raise Exception('Looks like read folder does not exist, aborting')
    
    restId_base = kwargs.get('restId_base', None)
    init_MorStt = kwargs.get(init_MorStt, "9.0000000e+000")
    new_Tlfsmo = kwargs.get(new_Tlfsmo, 0)
    remove_netcdf = kwargs.get(remove_netcdf, False)
    Restid_timeindex = kwargs.get(Restid_timeindex, None)
    
    base_folder = os.path.dirname(template_folder)

    copy_extensions = ('xml', 'ini', 'enc', 'grd', 'sh', 'dep', 'bnd', 'sed', 'tra', 'log')
    bc_extension = ('bct', 'bcc', 'dis')
    copy_filenames = [] # These files just need to be copied to the next runs folder
    bc_filenames = [] # In these files, times are changed for subsequent runs

    # Find filenames in template/read folder
    for _, _, files in os.walk(template_folder):
        for file in files:
            if file.endswith(copy_extensions):
                copy_filenames.append(file)
            elif file.endswith(bc_extension):
                bc_filenames.append(file)
            elif file.endswith('.mdf'):
                mdf_filename = file
                print('mdf_filename', mdf_filename)
            elif file.endswith('.mor'):
                morph_filename = file
                
    if not restId_base:
        restId_base = 'trim-' + os.path.splitext(mdf_filename)[0]
        print("No restart Id string provided. Got it from mdf filename: ", restId_base)
    elif 'trim-' not in restId_base:
        print("Restart Id must start with substring 'trim-'. Aborting")
        return
                
    if not copy_filenames:
        print('Missing one of these files', ' '.join(copy_ext for copy_ext in copy_extensions))
    elif not bc_filenames:
        print('Missing one of these files', ' '.join(copy_ext for copy_ext in copy_extensions))
    elif not mdf_filename:
        print('Can\'t find .mdf file in folder')    
    elif not morph_filename:
        print('Can\'t find .mor file in folder')

    mdf_filepath = os.path.join(template_folder, mdf_filename)
    mdf_dict = mdf.read(mdf_filepath)

    exclude_flags = []
    if 'FlNcdf' in mdf_dict and remove_netcdf == True:
        print("'remove_netcdf' is true and MDF file has Netcdf flags! Removing the NetCDF key to ensure DEF/DAT output")
        print("Note that the first runs (ie the template) .mdf file will remain untouched, remove Netcdf flags manually from this file")
        exclude_flags = ['FlNcdf', 'ncFormat', 'ncDeflate']
    
    # init_start_time = formatSci(mdf_dict['Tstart'][0])
    init_end_time = mdf_dict['Tstop'][0] # this is also the duration of each flow (of course!)
    output_timestep = mdf_dict['Flmap'][1]
    original_run_text = mdf_dict['Runtxt']

    nr_outputsteps = int(init_end_time/output_timestep)
    print(f"Total number of output timesteps is {nr_outputsteps+1}")
    
    # Delft3D fails silently when the requested Restid_timeindex is not found in the netCDF
    # In case of using a reset netCDF this is no problem as there is only one timestep in the dataset
    if Restid_timeindex:
        mdf_dict['Restid_timeindex'] = Restid_timeindex
    else:
        # nr_outputsteps + 1? I'm still not sure if +1 is necessary, another potential off-by-one bug
        mdf_dict['Restid_timeindex'] = [nr_outputsteps] 
        
    mdf_dict['Tlfsmo'] = [float(new_Tlfsmo)]    # Change smoothing time to zero for all subsequent runs
    mdf_dict['FlRst'] = 0                       # Dont write restart files

    for run in range(number_of_runs):
        print('**--------- RUN' + str(run + 1) + '-----------**')

        new_start_time = run * init_end_time
        new_end_time = (run + 1) * init_end_time
        
        if run > 0:
            new_mdf_dict = copy.deepcopy(mdf_dict)

            run_folder = f'Run{run+1:02d}' 
            
            new_run_folder = os.path.join(base_folder, run_folder)
            print("New folder:", new_run_folder)
            
            try:  
                os.mkdir(new_run_folder)
            except OSError:
                if os.path.exists(new_run_folder):
                    print (f"Creation of the directory '{new_run_folder}' failed, because it already exists! Carrying on")
                else:
                    print (f"Creation of the directory '{new_run_folder}' failed for unknown reasons, abort")
                    break
                    
            # Simply copy these files to new run folder
            for file_to_copy in copy_filenames:
                old_file = os.path.join(template_folder,file_to_copy)
                new_copied_file = os.path.join(new_run_folder, file_to_copy)
                shutil.copy(old_file, new_copied_file)

            # Change things in new MDF File
            new_mdf_dict['Tstart'] = [new_start_time]   # Write new start time
            new_mdf_dict['Tstop'] = [new_end_time]      # Write new end time
            new_mdf_dict['Flmap'][0] = new_start_time   # Start of writing map file
            new_mdf_dict['Flmap'][2] = new_end_time     # End of writing map file
            new_mdf_dict['Flhis'][0] = new_start_time   # Start of writing history file
            new_mdf_dict['Flhis'][2] = new_end_time     # End of writing history file

            new_run_text = f'{original_run_text} Run {run+1:02}'
            
            
            new_mdf_dict['Runtxt'] = new_run_text

            new_mdf_dict['Restid'] = f'{restId_base}Run{run:02}'
            
            new_mdf_filename = os.path.join(new_run_folder, mdf_filename)
            mdf.write(new_mdf_dict, new_mdf_filename, exclude=exclude_flags)
            
            # Change spin-up interval (MorStt) for morphological changes to 0 in .mor file            
            template_morph_filename = os.path.join(template_folder, morph_filename)
            new_morph_filename = os.path.join(new_run_folder, morph_filename)
            
            # Kinda finicky because strings need to match EXACTLY
            old_spin_up_time_str = f"MorStt           =  {init_MorStt}"
            new_spin_up_time_str = "MorStt           =  0.0000000e+000"
            
            print("Removing morphology smoothing time")
            stupidReplaceText(template_morph_filename, new_morph_filename, old_spin_up_time_str, new_spin_up_time_str)
            
            # Add runtime in boundary conidition & transport files
            for bc_filename in bc_filenames:
                print(f"\tChanging times in {bc_filename}")
                # Create new filename with run folder prefix
                template_filename = os.path.join(template_folder, bc_filename)
                new_filename = os.path.join(new_run_folder, bc_filename)
                
                # Add end times and write to new file
                # its kinda ugly but it works
                stupidReplaceTimeBC(template_filename, new_filename, run, init_end_time)
            
                
    print("Start time:", new_start_time, "\nEnd time:  ", new_end_time)