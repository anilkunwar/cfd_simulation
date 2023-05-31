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
    # Your sif file content here
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
st.image(fig.canvas.to_rgba(), use_column_width=True)
