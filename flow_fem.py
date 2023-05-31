import os
import streamlit as st
import meshio
import numpy as np
import matplotlib.pyplot as plt
import subprocess

def run_elmer_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode(), stderr.decode()

# Run ElmerGrid command
run_elmer_command('ElmerGrid 1 4 step.grd')

# Read mesh file
mesh = meshio.read('step.msh')

# Extract the mesh points and cells information
points = mesh.points
cells = mesh.cells[0]  # Assuming there is only one cell type in the MSH file

# Create Streamlit app
st.title("Mesh Plot")

# Plot the mesh cells
fig, ax = plt.subplots()

if cells.type == "quad":
    cell_quads = cells.data
    for quad in cell_quads:
        quad_points = points[quad]
        quad_points = [*quad_points, quad_points[0]]  # Close the quad
        xs, ys, _ = zip(*quad_points)
        ax.plot(xs, ys, 'b-')
elif cells.type == "triangle":
    cell_triangles = cells.data
    for triangle in cell_triangles:
        triangle_points = points[triangle]
        triangle_points = [*triangle_points, triangle_points[0]]  # Close the triangle
        xs, ys, _ = zip(*triangle_points)
        ax.plot(xs, ys, 'b-')
elif cells.type == "line":
    cell_lines = cells.data
    for line in cell_lines:
        line_points = points[line]
        xs, ys, _ = zip(*line_points)
        ax.plot(xs, ys, 'b-')

# Set the aspect ratio to 'equal'
ax.set_aspect('equal')

# Display the plot using Streamlit
st.pyplot(fig)

# Run ElmerGrid command
run_elmer_command('ElmerGrid 1 2 step.grd')

# List files in the current directory
file_list = os.listdir('.')
st.title("Current Directory")
st.write(file_list)

# Create Elmer sif file
sif_content = '''
Header
  CHECK KEYWORDS Warn
  Mesh DB "." "step"
  Include Path ""
  Results Directory ""
End

Simulation
  Max Output Level = 4
  Coordinate System = Cartesian
  Coordinate Mapping(3) = 1 2 3
  Simulation Type = Steady state
  Steady State Max Iterations = 1
  Output Intervals(1) = 1
  Solver Input File = case.sif
  Post File = case.vtu
End

Constants
  Gravity(4) = 0 -1 0 9.82
  Stefan Boltzmann = 5.67e-08
  Permittivity of Vacuum = 8.8542e-12
  Permeability of Vacuum = 1.25663706e-6
  Boltzmann Constant = 1.3807e-23
  Unit Charge = 1.602e-19
End

Body 1
  Target Bodies(1) = 1
  Name = "Body Property 1"
  Equation = 1
  Material = 1
End

Solver 1
  Equation = Navier-Stokes
  Procedure = "FlowSolve" "FlowSolver"
  Variable = Flow Solution[Velocity:2 Pressure:1]
  Exec Solver = Always
  Stabilize = True
  Optimize Bandwidth = True
  Steady State Convergence Tolerance = 1.0e-5
  Nonlinear System Convergence Tolerance = 1.0e-8
  Nonlinear System Max Iterations = 20
  Nonlinear System Newton After Iterations = 3
  Nonlinear System Newton After Tolerance = 1.0e-3
  Nonlinear System Relaxation Factor = 1
  Linear System Solver = Iterative
  Linear System Iterative Method = BiCGStab
  Linear System Max Iterations = 500
  Linear System Convergence Tolerance = 1.0e-8
  BiCGstabl polynomial degree = 2
  Linear System Preconditioning = ILU0
  Linear System ILUT Tolerance = 1.0e-3
  Linear System Abort Not Converged = False
  Linear System Residual Output = 1
  Linear System Precondition Recompute = 1
End

Equation 1
  Name = "Navier-Stokes"
  Active Solvers(1) = 1
End

Material 1
  Name = "Ideal"
  Density = 1.0
  Viscosity = 0.01
End

Boundary Condition 1
  Target Boundaries(1) = 1 
  Name = "Inlet"
  Velocity 2 = 0.0
  Velocity 1 = Variable Coordinate 2; Real MATC "6*(tx-1)*(2-tx)"
End

Boundary Condition 2
  Target Boundaries(1) = 2 
  Name = "Outlet"
  Velocity 2 = 0.0
End

Boundary Condition 3
  Target Boundaries(1) = 3 
  Name = "Walls"
  Noslip wall BC = True
End
'''

# Save sif file
with open('case.sif', 'w') as f:
    f.write(sif_content)

# Run ElmerSolver command
run_elmer_command('ElmerSolver case.sif')

# List files in the current directory
file_list = os.listdir('.')
st.title("Current Directory")
st.write(file_list)

# Read VTU file
mesh = meshio.read("./step/case_t0001.vtu")

# Extract the points and cells from the mesh
points = mesh.points
cells = mesh.cells

# Extract velocity data
velocity = mesh.point_data['velocity']

# Plotting 2D mesh with velocity data
fig, ax = plt.subplots()

# Plotting vertices with velocity data
ax.quiver(points[:, 0], points[:, 1], velocity[:, 0], velocity[:, 1])

# Plotting cells (triangles or tetrahedra)
if 'triangle' in cells:
    triangles = cells['triangle']
    ax.tripcolor(points[:, 0], points[:, 1], triangles=triangles, facecolors='gray', alpha=0.5)
elif 'tetra' in cells:
    tetrahedra = cells['tetra']
    ax.tripcolor(points[:, 0], points[:, 1], triangles=tetrahedra, facecolors='gray', alpha=0.5)

# Set aspect ratio
ax.set_aspect(1)  # or any other desired aspect ratio

# Set axis labels
ax.set_xlabel('X')
ax.set_ylabel('Y')

# Display the plot using Streamlit
st.pyplot(fig)