import os
import shutil
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
st.title("CFD Simulation")

# Upload the .grd file
grd_file = st.file_uploader("Upload .grd File", type=".grd")

# Check if .grd file is uploaded
if grd_file is not None:
    # Save the .grd file
    with open("step.grd", "wb") as f:
        f.write(grd_file.getvalue())

    # Convert .grd to .msh
    run_elmer_command("ElmerGrid 1 2 step.grd")

    # Create flow_fem directory in the home directory
    flow_fem_dir = os.path.expanduser("~/flow_fem")
    os.makedirs(flow_fem_dir, exist_ok=True)

    # Move the .msh file to flow_fem directory
    shutil.move("step.msh", os.path.join(flow_fem_dir, "step.msh"))

    # Display download link for .msh file
    st.markdown("Download [.msh file](flow_fem/step.msh)")

    # Change current directory to flow_fem
    os.chdir(flow_fem_dir)

    # Run ElmerSolver command
    run_elmer_command("ElmerSolver case.sif")

    # Read VTU file
    mesh = meshio.read("case_t0001.vtu")

    # Extract the points and cells from the mesh
    points = mesh.points
    cells = mesh.cells

    # Extract velocity data
    velocity = mesh.point_data["velocity"]

    # Plotting 2D mesh with velocity data
    fig, ax = plt.subplots()

    # Plotting vertices with velocity data
    ax.quiver(points[:, 0], points[:, 1], velocity[:, 0], velocity[:, 1])

    # Plotting cells (triangles or tetrahedra)
    if "triangle" in cells:
        triangles = cells["triangle"]
        ax.tripcolor(points[:, 0], points[:, 1], triangles=triangles, facecolors="gray", alpha=0.5)
    elif "tetra" in cells:
        tetrahedra = cells["tetra"]
        ax.tripcolor(points[:, 0], points[:, 1], triangles=tetrahedra, facecolors="gray", alpha=0.5)

    # Set aspect ratio
    ax.set_aspect(1)  # or any other desired aspect ratio

    # Set axis labels
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    # Display the plot using Streamlit
    st.pyplot(fig)
