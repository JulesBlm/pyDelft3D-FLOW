[SedimentFileInformation]
   FileCreatedBy    = Delft3D FLOW-GUI, Version: 3.42.00.17790         
   FileCreationDate = Wed Jun 26 2019, 15:50:39         
   FileVersion      = 02.00                        
[SedimentOverall]
   Cref             =  1.6000000e+003      [kg/m3]  CSoil Reference density for hindered settling calculations
   IopSus           = 0                             If Iopsus = 1: susp. sediment size depends on local flow and wave conditions
[Sediment]
   Name             = #Sediment vfsand#             Name of sediment fraction
   SedTyp           = sand                          Must be "sand", "mud" or "bedload"
   RhoSol           =  2.6500000e+003      [kg/m3]  Specific density
   SedDia           =  1.0000000e-004      [m]      Median sediment diameter (D50)
   CDryB            =  1.6000000e+003      [kg/m3]  Dry bed density
   IniSedThick      =  5.0000000e+000      [m]      Initial sediment layer thickness at bed (uniform value or filename)
   FacDSS           =  1.0000000e+000      [-]      FacDss * SedDia = Initial suspended sediment diameter. Range [0.6 - 1.0]
[Sediment]
   Name             = #Sediment msilt#              Name of sediment fraction
   SedTyp           = mud                           Must be "sand", "mud" or "bedload"
   RhoSol           =  2.6500000e+003      [kg/m3]  Specific density
   SalMax           =  0.0000000e+000      [ppt]    Salinity for saline settling velocity
   WS0              =  3.0000000e-004      [m/s]    Settling velocity fresh water
   WSM              =  3.0000000e-004      [m/s]    Settling velocity saline water
   TcrSed           =  1.0000000e+003      [N/m2]   Critical bed shear stress for sedimentation (uniform value or filename)
   TcrEro           =  1.0000000e-001      [N/m2]   Critical bed shear stress for erosion       (uniform value or filename)
   EroPar           =  1.0000000e-003      [kg/m2/s] Erosion parameter                           (uniform value or filename)
   CDryB            =  5.0000000e+002      [kg/m3]  Dry bed density
   IniSedThick      =  5.0000001e+000      [m]      Initial sediment layer thickness at bed (uniform value or filename)
   FacDSS           =  1.0000000e+000      [-]      FacDss * SedDia = Initial suspended sediment diameter. Range [0.6 - 1.0]
