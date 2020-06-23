import re
from collections import OrderedDict
from datetime import date
import json


class Mor(object):
    '''
    Read and write Delft3D morphology file
    
    Parameters
    ----------
    
    filename: str
        Filename of sediment or morphology file that is read
    
    TODO
    ----
    * Maybe split into separate Mor and Sed subclass?
    * Add description with units from FLOW manual and display those when a sed or mor file is loaded
    * Should check against hardcoded dict to see if options are ok and show possible options and unitss
    * Same for loading descriptions of keywords
    * Parse number values    
    '''

    
    def __init__(self, filename=None):
        self.filename = filename
        self.data = OrderedDict() 
        self.read(filename)

    def __repr__(self):
        return json.dumps(self.data, indent=4)

    def read(self, filename=None):
        valid_extension = ".mor"
        mor_header_name = ["[MorphologyFileInformation]", "[Morphology]", "[Underlayer]", "[Output]"]

        if not filename:
            raise Exception("No file name supplied!")
        elif not filename.endswith(valid_extension):
            raise Exception("Filename does not end with .mor")
            

        with open(filename, "r") as sed_file:
            data = OrderedDict()            

            for line in sed_file.readlines():
                stripped_lined = line.strip()
                
                if stripped_lined in mor_header_name:
                    header_name = stripped_lined[1:-1] # remove square brackets
                    data[header_name] = OrderedDict()
                        
                if "=" in line:
                    keyword, values = line.split("=", 1)
                    keyword = keyword.strip()

                    list_of_values = re.split(r'\s{2,}', values.strip()) # split on more than two spaces           
                    data[header_name][keyword] = list_of_values[0]

            self.data = data

        return self.data
        
    def write(self, filename=None, exclude=[]):
        """Write OrderedDict to Delft3D-FLOW *.sed file.
          To ignore a keyword pass a list to keyword argument 'exclude',
          
          Parameters
          ----------
          filename: str
              Paths to sed/mor file
              
          exclude: list
              List of keyword to exclude from writing
          
          Examples
          --------
          >>> sed.write(inp, '5050.sed', exclude=['NearBedRefConcentration']) 
          """
        if not filename:
            raise Exception("No filename provided")
            
        data = self.data
            
        # update file info
        today = date.today()
        creation_date_string = today.strftime("%m/%d/%Y, %H:%M:%S")        
        
        info_header = "MorphologyFileInformation"    
        
        data[info_header]['FileCreatedBy'] = "pyDelft3D-FLOW v ????" # TODO add global version here
        data[info_header]['FileCreationDate'] = creation_date_string

        
        with open(filename, 'w') as new_file:
            for header_name in data:
                new_file.write(f"[{header_name}]\n")
                
                for keyword in data[header_name]:
                    if not (keyword in exclude):
                        new_file.write(f"   {keyword.ljust(16)} = {data[header_name][keyword]}\n")        

class Sed(object):
    def __init__(self, filename=None):
        self.names = []
        self.filename = filename
        self.data = OrderedDict() 
        self.read(filename)        

    def __repr__(self):
        return json.dumps(self.data, indent=4)        
        
    def read(self, filename=None):
        valid_extension = ".sed"
        sed_header_names = ["[SedimentFileInformation]", "[SedimentOverall]", "[Sediment]"]
        
        if not filename:
            raise Exception("No file name supplied!")
        elif not filename.endswith(valid_extension):
            raise Exception("Filename does not end with .mor or .sed!")
        
        with open(filename, "r") as sed_file:
            data = OrderedDict()

            for line in sed_file.readlines():
                stripped_lined = line.strip()
                
                if stripped_lined in sed_header_names:
                    header_name = stripped_lined[1:-1] # remove square brackets
                    
                    # to prevent overwriting the previous sediment
                    if header_name == 'Sediment':
                        sed_nr = len(self.names)
                        header_name = header_name + str(sed_nr)
                        data[header_name] = OrderedDict()

                    data[header_name] = OrderedDict()
                        
                if "=" in line:
                    keyword, values = line.split("=", 1)
                    keyword = keyword.strip()

                    list_of_values = re.split(r'\s{2,}', values.strip()) # split on more than two spaces
                    
                    if keyword == "Name":
                        self.names.append(list_of_values[0][1:-1]) # add sediment to list of sediment names

                    data[header_name][keyword] = list_of_values[0]

            self.data = data

        return self.data                    
                    
    def write(self, filename=None, exclude=[]):
        """Write OrderedDict to Delft3D-FLOW *.sed file.
        To ignore a keyword pass a list to keyword argument 'exclude',

        Parameters
        ----------
        filename: str
            Paths to sed/mor file

        exclude: list
            List of keyword to exclude from writing

        Examples
        --------
        >>> sed.write(inp, '5050.sed', exclude=['NearBedRefConcentration']) 
        """
        if not filename:
            raise Exception("No filename provided")

        data = self.data

        # update file info
        today = date.today()
        creation_date_string = today.strftime("%m/%d/%Y, %H:%M:%S")        

        info_header = "SedimentFileInformation" 

        data[info_header]['FileCreatedBy'] = "pyDelft3D-FLOW v ?" # TODO add global version here
        data[info_header]['FileCreationDate'] = creation_date_string

        with open(filename, 'w') as new_file:
            for header_name in data:

                # remove the sediment nr again when writing to file
                if re.search(r'Sediment[0-9]*$', header_name):
                    new_file.write("[Sediment]\n")
                else:
                    new_file.write(f"[{header_name}]\n")

                for keyword in data[header_name]:
                    if not (keyword in exclude):
                        new_file.write(f"   {keyword.ljust(16)} = {data[header_name][keyword]}\n")        

                    
# TODO: 
# Make this a hardcoded dict to match values against
#     mor_string_keywords = ['FileCreatedBy', 'FileCreationDate', 'FileVersion', 'MorUpd', 'IHidExp', 'ISlope', 'BcFil', 'IBedCond', 'ICmpCond', 'IUnderLyr', 'TTLForm', 'ThTrLyr', 'UpdBaseLyr', 'IniComp']
#     mor_bool_keywords = ['NeuBcSand', 'NeuBcMud', 'DensIn', 'MorUpd', 'BedUpd', 'CmpUpd', 'NeglectEntrainment', 'EqmBc', 'UpdInf', 'Multi', 'UpwindBedload'] 
#     mor_bool_output_keywords = ['VelocAtZeta', 'VelocMagAtZeta', 'VelocZAtZeta', 'ShearVeloc','MaximumWaterdepth','BedTranspAtFlux',
#         'BedTranspDueToCurrentsAtZeta','BedTranspDueToCurrentsAtFlux','BedTranspDueToWavesAtZeta','BedTranspDueToWavesAtFlux',
#         'SuspTranspDueToWavesAtZeta','SuspTranspDueToWavesAtFlux','SuspTranspAtFlux','NearBedTranspCorrAtFlux','NearBedRefConcentration',
#         'EquilibriumConcentration','SettlingVelocity','SourceSinkTerms','Bedslope', 'Taurat','Bedforms','Dm','Dg',
#         'Frac','MudFrac','FixFac','HidExp','Percentiles','CumNetSedimentationFlux','BedLayerSedimentMass','BedLayerDepth',
#         'BedLayerVolumeFractions','BedLayerPorosity','StatWaterDepth',
#         ]
#     bool_keywords = mor_bool_keywords + mor_bool_output_keywords
#     
#     string_keywords = bool_keywords + mor_string_keywords # temporary hack
# elif filename.endswith(".sed"):
#     string_keywords = ['FileCreatedBy', 'VERSION', 'IopSus', 'SedTyp', 'Name']
#     bool_keywords = []