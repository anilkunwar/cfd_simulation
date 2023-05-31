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

# Create Streamlit app
st.title("Mesh Plot")

# File upload and download options
option = st.radio("Choose an option", ("Upload .grd file", "Download simulated files", "Download mesh files"))

if option == "Upload .grd file":
    grd_file = st.file_uploader("Upload .grd file")
    if grd_file:
        with open('step.grd', 'wb') as f:
            f.write(grd_file.getvalue())

elif option == "Download simulated files":
    # Run ElmerGrid command
    run_elmer_command('ElmerGrid 1 4 step.grd')

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

    # Provide download link for simulated files
    st.markdown("[Download Simulated Files](./step)")

elif option == "Download mesh files":
    # Run ElmerGrid command
    run_elmer_command('ElmerGrid 1 2 step.grd')

    # List files in the current directory
    file_list = os.listdir('.')
    st.title("Current Directory")
    st.write(file_list)

    # Provide download link for mesh files
    st.markdown("[Download Mesh Files](./)")

# Display the plot using Streamlit
st.pyplot(fig)
