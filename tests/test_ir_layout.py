import pytest
import matplotlib.pyplot as plt
from src.ir.animate import setup_ir_dashboard

def test_dashboard_plot_count_and_projections():
    fig, (ax_seq, ax_mz, ax_3d) = setup_ir_dashboard()
    
    assert len(fig.axes) == 3, f"Layout violation: Expected exactly 3 subplots, got {len(fig.axes)}."
    
    assert ax_seq.name == 'rectilinear', "Pulse Sequence plot must be 2D."
    assert ax_mz.name == 'rectilinear', "Longitudinal Relaxation plot must be 2D."
    assert ax_3d.name == '3d', "Rotating Frame plot must be a 3D projection."
    
    plt.close(fig)

def test_dashboard_gridspec_geometry():
    fig, (ax_seq, ax_mz, ax_3d) = setup_ir_dashboard()
    
    seq_pos = ax_seq.get_subplotspec()
    mz_pos = ax_mz.get_subplotspec()
    frame_3d_pos = ax_3d.get_subplotspec()
    
    # Check Column Placements
    assert seq_pos.colspan.start == 0, "Pulse Sequence must be in the left column."
    assert mz_pos.colspan.start == 0, "Mz Relaxation must be in the left column."
    assert frame_3d_pos.colspan.start == 1, "3D Rotating Frame must be in the right column."
    
    # Check Row Placements
    assert seq_pos.rowspan.start == 0, "Pulse Sequence must be on the top row."
    assert mz_pos.rowspan.start == 1, "Mz Relaxation must be on the bottom row."
    
    # Check Row Spanning for the 3D plot
    assert frame_3d_pos.rowspan.start == 0 and frame_3d_pos.rowspan.stop == 2, \
        "3D frame must span both the top and bottom rows to match the wireframe."
        
    plt.close(fig)

def test_dashboard_labels_and_limits():
    fig, (ax_seq, ax_mz, ax_3d) = setup_ir_dashboard()
    
    ymin, ymax = ax_mz.get_ylim()
    assert ymin <= -1.0 and ymax >= 1.0, "Mz plot Y-limits must accommodate full inversion recovery."
    
    assert ax_3d.get_xlim() == ax_3d.get_ylim() == ax_3d.get_zlim(), \
        "3D Rotating Frame axes limits must be perfectly symmetrical."
        
    plt.close(fig)