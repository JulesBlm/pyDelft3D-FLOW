'''
TODO:
* If uniform grid read grid cell size
* If 
'''
import numpy as np
import datetime
from pyd3d.utils import formatSci, formatInt

class Grid(object):
    """Create a Delft3D grid file

    Examples
    --------
    Create an empty grid
	>>> grid = Grid()
	
    Load a grid from file
	>>> grid = Grid.read('filename.grd')
	
    Write grid to file
	>>> Grid.write(grid,'filename.grd')
	"""

    def __init__(self, **kwargs):
        self.properties = kwargs.get("properties", {})
        self.shape = kwargs.get("shape", None)
        self.x = kwargs.get("x", None)
        self.y = kwargs.get("y", None)
        # following two for rectilinear grids!
        self.x_gridstep = kwargs.get("x_gridstep", None)
        self.y_gridstep = kwargs.get("y_gridstep", None)


    def newRectilinear(self):
        """Makes rectilinear grid with numpy meshgrid"""
        print("------ Making new Delft3D grid ------")
        print("x_gridstep", self.x_gridstep)
        print("y_gridstep", self.y_gridstep)
        print("width", self.width)
        print("length", self.length)
        
        if self.width % self.x_gridstep:
            raise Exception("Width is not a multiple of x_gridstep")
        if self.length % self.y_gridstep:
            raise Exception("Length is not a multiple of y_gridstep")
            
        x_gridstep = self.x_gridstep
        y_gridstep = self.y_gridstep

        xList = np.array([i for i in range(0, self.width + x_gridstep, x_gridstep)])
        yList = np.array([i for i in range(0, self.length + y_gridstep, y_gridstep)]) + 100 # + 100 is default start y in REFGRID

        xDim, yDim = [len(xList), len(yList)]
        print(f"MNKmax = {xDim + 1} {yDim + 1} SIGMALAYERS") # to mdf file
        
        print("xDim", xDim)
        print("yDim", yDim)
        
        self.shape.append([xDim, yDim])
        
        x_grid, y_grid = np.meshgrid(xList, yList)
        self.x_grid = x_grid
        self.y_grid = y_grid
        self.shape = (xDim, yDim)
        
        return x_grid, y_grid

    @staticmethod
    def read(filename=None, **kwargs):
        if not filename:
            raise Exception("No grid filename given!")
        
        grid = Grid()
        grid.filename = filename
        grid.shape = None
        rows = []
        
        with open(filename) as f:
            for line in f:
                line = line.strip()
                # skip comments and empty lines
                if line.startswith("*") or not line:
                    continue
                elif "=" in line:
                    key, value = line.split("=")
                    if "Coordinate" in key:
                        grid.properties[key.strip()] = value.strip()
                    if "ETA" in key:
                        row = value.split()
                        n, row = row[0], row[1:]
                        while len(row) < grid.shape[1]:
                            line = f.readline()
                            row.extend(line.split())
                        rows.append(row)
                # Read grid size
                elif grid.shape == None:
                    # line should contain size
                    # convert to nrow x ncolumns
                    grid.shape = tuple(np.array(line.split()[::-1], dtype="int"))
                    assert (len(grid.shape) == 2), f"Expected shape (2,), got {grid.shape}, (subgrids not supported)"
                    
                    # also read next line
                    line = f.readline()
                    grid.properties["xori"], grid.properties["yori"], grid.properties["alfori"] = np.array(line.split(), dtype="float")
                    
        # rows now contain [X Y]
        data = np.array(rows, dtype="double")
        assert (data.shape[0], data.shape[1]) == (grid.shape[0] * 2, grid.shape[1]), f"Expected shape of data:{(grid.shape[0] * 2, grid.shape[1])} , got {(data.shape[0], data.shape[1])}"
        
        X, Y = data[: grid.shape[0], :], data[grid.shape[0] :, :]
        grid.x = np.ma.MaskedArray(X, mask=X == 0.0)  # apply standard nodatavalue of 0
        grid.y = np.ma.MaskedArray(Y, mask=Y == 0.0)  # apply standard nodatavalue of 0
        return grid

    def write(self, filename, **kwargs):

        with open(filename, "w") as f:

            nDim, mDim = np.shape(self.x)

            f.write(f"* Created at {str(datetime.datetime.now())}\n")
            f.write(
                "* by pyDelft3D-FLOW version ? \n" + 
                "* Git url: https://github.com/JulesBlm/pyDelft3D-FLOW $\n"
            )
            f.write(f"Coordinate System = {self.properties['Coordinate System']}\n")
            coordinatesString = f'      {formatInt(mDim)}      {formatInt(nDim)}\n'
            f.write(coordinatesString)
            properties = f" {formatInt(self.properties['xori'])} {formatInt(self.properties['yori'])} {formatInt(self.properties['alfori'])}\n"
            f.write(properties)

            max_m_lines = 5

            nrow = int(np.ceil(mDim / max_m_lines))  # max 5 m-values per line

            for n in range(nDim):
                lowerBound = 0
                upperBound = min(5, mDim)
                nstr = formatInt(n + 1)

                # Write values with ETA = x prepended            
                ETAstring = " ETA= {:>4}   {}\n".format(nstr, "   ".join(formatSci(x) for x in self.x[n][lowerBound:upperBound]))
                f.write(ETAstring)

                # Write remaining values in ETA = m
                for i in range(1, nrow):
                    lowerBound = i * max_m_lines
                    upperBound = min((i + 1) * max_m_lines, mDim)
                    f.write("             {}\n".format("   ".join(formatSci(x) for x in self.x[n][lowerBound:upperBound] )))

            # ?
            for n in range(nDim):
                lowerBound = 0
                upperBound = min(max_m_lines, mDim)
                nstr = formatInt(n + 1)

                lastETAstring = ' ETA= {:>4}   {}\n'.format(nstr, "   ".join(formatSci(y) for y in self.y[n][lowerBound:upperBound]))
                f.write(lastETAstring)

                for i in range(1, nrow):
                    lowerBound = i * max_m_lines
                    upperBound = min((i + 1) * max_m_lines, mDim)
                    f.write('             {}\n'.format("   ".join(formatSci(y) for y in self.y[n][lowerBound:upperBound])))
