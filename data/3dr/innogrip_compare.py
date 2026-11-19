"""
Batch point-cloud comparison across all samples.

Expected folder layout under ROOT:

    <ROOT>/<sample>/multiple/ground_truth.ply
    <ROOT>/<sample>/multiple/da3/final_processed.ply
    <ROOT>/<sample>/multiple/vggt/final_processed.ply

    <ROOT>/<sample>/stacked/ground_truth.ply
    <ROOT>/<sample>/stacked/da3/final_processed.ply
    <ROOT>/<sample>/stacked/vggt/final_processed.ply

    <ROOT>/<sample>/single/orientation_a/ground_truth.ply
    <ROOT>/<sample>/single/orientation_a/da3/final_processed.ply
    <ROOT>/<sample>/single/orientation_a/vggt/final_processed.ply
    <ROOT>/<sample>/single/orientation_b/ground_truth.ply
    ... etc (one ground_truth.ply PER orientation)

For every (sample, config, model) combination found, this script:
  1. Runs the same alignment/metric pipeline as the original compare.py
  2. Writes the debug .ply files and a per-run metrics.csv next to the
     reconstruction's final_processed.ply (i.e. inside the da3/ or vggt/ folder)
  3. Collects the metrics into one row per sample (or per sample+orientation
     for "single"), with da3 and vggt columns side by side

At the end, three Excel files are written:
    <ROOT>/single_results.xlsx
    <ROOT>/multiple_results.xlsx
    <ROOT>/stacked_results.xlsx

===========================================================================
IMPORTANT - PER-MODEL SCALE + TRANSFORM
===========================================================================
da3 and vggt reconstructions live in different coordinate scales/frames, so
each model gets its own scale factor and 4x4 initial transform (applied in
that order: scale first, then transform), chosen per sample / config / orientation (see get_transform).
See MODEL_SCALES and MODEL_TRANSFORMS below.
===========================================================================
"""

import os
import csv
import traceback
import numpy as np
import open3d as o3d
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

# ---------------------------------------------------------------------------
# CONFIGURATION - edit these
# ---------------------------------------------------------------------------

ROOT = "/home/innogrip/inno-grip-codebase/test"

MODELS = ["da3", "vggt"]

ICP_THRESHOLD = 0.001          # meters, alignment ICP correspondence threshold
CROP_SIZE = 0.10               # meters, central region cube size
PLANE_DISTANCE_THRESHOLD = 0.001
COMPLETENESS_THRESHOLDS = [0.002, 0.001, 0.0005]  # meters (2mm, 1mm, 0.5mm)
GT_SCALE = 0.001               # applied to ground truth point cloud (mm -> m)

# Per-model uniform scale applied to the RECONSTRUCTION before the transform.
MODEL_SCALES = {
    "da3": 1.0,
    "vggt": 0.325127,
}

# Fallback per-model 4x4 initial transform applied to the RECONSTRUCTION after scaling.
MODEL_TRANSFORMS = {
    "da3": np.array([
        [0.006, -1.000, 0.012, 0.044],
        [1.000,  0.006, 0.006, -0.044],
        [-0.006, 0.012, 1.000, -0.280],
        [0.000,  0.000, 0.000, 1.000],
    ]),
    "vggt": np.array([
        [0.267, -0.963, 0.026,  0.056],
        [0.963,  0.268, 0.010, -0.028],
        [-0.016, 0.022, 1.000, -0.300],
        [0.000,  0.000, 0.000,  1.000],
    ]),
}

# Per-SAMPLE, per-model 4x4 initial transforms. Keys are the sample folder
# names under ROOT. These override MODEL_TRANSFORMS (which acts as the
# fallback for any sample not listed here).
SAMPLE_MODEL_TRANSFORMS = {
    "G-MS-I-LO-1": {
        "da3": np.array([
            [ 1.000, -0.027,  0.007,  0.108],
            [ 0.027,  1.000, -0.002, -0.044],
            [-0.007,  0.002,  1.000, -0.281],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 1.000,  0.018,  0.005,  0.108],
            [-0.018,  1.000,  0.004, -0.050],
            [-0.004, -0.004,  1.000, -0.273],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "G-MS-O-LO-2": {
        "da3": np.array([
            [-0.023, -1.000,  0.004,  0.041],
            [ 1.000, -0.023,  0.000, -0.043],
            [-0.000,  0.004,  1.000, -0.289],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.032, -0.999,  0.017,  0.046],
            [ 0.999,  0.032,  0.009, -0.044],
            [-0.010,  0.017,  1.000, -0.272],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "G-TS-P-HI-3": {
        "da3": np.array([
            [-0.013, -1.000,  0.006,  0.040],
            [ 1.000, -0.013, -0.002, -0.043],
            [ 0.002,  0.006,  1.000, -0.281],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.033, -0.999,  0.016,  0.043],
            [ 0.999,  0.034,  0.020, -0.047],
            [-0.021,  0.015,  1.000, -0.275],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "G-MS-I-HI-4": {
        "da3": np.array([
            [ 0.112, -0.994,  0.020,  0.038],
            [ 0.994,  0.111, -0.006, -0.024],
            [ 0.004,  0.021,  1.000, -0.281],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.253, -0.967,  0.012,  0.057],
            [ 0.967,  0.253,  0.014, -0.027],
            [-0.016,  0.008,  1.000, -0.273],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "G-TS-P-HI-5": {
        "da3": np.array([
            [-0.011, -1.000,  0.007,  0.040],
            [ 1.000, -0.011,  0.002, -0.045],
            [-0.002,  0.007,  1.000, -0.282],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.031, -0.999,  0.015,  0.045],
            [ 0.999,  0.031,  0.017, -0.046],
            [-0.018,  0.015,  1.000, -0.273],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "R-TS-I-HI-6": {
        "da3": np.array([
            [-0.026, -1.000,  0.004,  0.037],
            [ 1.000, -0.026, -0.000, -0.044],
            [ 0.001,  0.004,  1.000, -0.284],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.028, -0.999,  0.022,  0.039],
            [ 1.000,  0.028,  0.009, -0.045],
            [-0.010,  0.022,  1.000, -0.277],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "G-TS-O-HI-7": {
        "da3": np.array([
            [-0.032, -0.999,  0.009,  0.042],
            [ 0.999, -0.032, -0.002, -0.043],
            [ 0.003,  0.009,  1.000, -0.280],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.025, -1.000,  0.017,  0.049],
            [ 1.000,  0.025,  0.019, -0.046],
            [-0.019,  0.016,  1.000, -0.270],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "R-MS-I-HI-8": {
        "da3": np.array([
            [ 0.118, -0.993,  0.025,  0.036],
            [ 0.993,  0.118, -0.000, -0.026],
            [-0.003,  0.025,  1.000, -0.277],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.270, -0.963,  0.008,  0.057],
            [ 0.963,  0.270,  0.015, -0.026],
            [-0.016,  0.004,  1.000, -0.278],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "M-MS-P-HI-9": {
        "da3": np.array([
            [ 0.113, -0.993,  0.010,  0.047],
            [ 0.993,  0.113, -0.011, -0.030],
            [ 0.010,  0.011,  1.000, -0.281],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.300, -0.954,  0.019,  0.062],
            [ 0.954,  0.300,  0.010, -0.034],
            [-0.015,  0.015,  1.000, -0.262],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "G-MS-O-LO-10": {
        "da3": np.array([
            [-0.016, -1.000,  0.003,  0.040],
            [ 1.000, -0.016, -0.002, -0.042],
            [ 0.002,  0.003,  1.000, -0.284],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.022, -1.000, -0.001,  0.050],
            [ 1.000,  0.022,  0.012, -0.045],
            [-0.012, -0.002,  1.000, -0.277],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "R-MS-I-HI-11": {
        "da3": np.array([
            [ 0.137, -0.990,  0.008,  0.052],
            [ 0.991,  0.137, -0.001, -0.032],
            [ 0.000,  0.009,  1.000, -0.281],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.275, -0.961,  0.013,  0.066],
            [ 0.961,  0.275,  0.015, -0.033],
            [-0.018,  0.008,  1.000, -0.274],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "R-MS-P-LO-12": {
        "da3": np.array([
            [-0.026, -1.000,  0.002,  0.041],
            [ 1.000, -0.026,  0.002, -0.044],
            [-0.002,  0.002,  1.000, -0.285],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.036, -0.999,  0.002,  0.048],
            [ 0.999,  0.036,  0.011, -0.045],
            [-0.011,  0.002,  1.000, -0.268],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "R-MS-I-LO-13": {
        "da3": np.array([
            [-0.016, -1.000,  0.008,  0.039],
            [ 1.000, -0.016, -0.008, -0.041],
            [ 0.009,  0.008,  1.000, -0.286],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.050, -0.999,  0.009,  0.048],
            [ 0.999,  0.050,  0.016, -0.045],
            [-0.016,  0.008,  1.000, -0.270],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "R-MS-I-LO-14": {
        "da3": np.array([
            [ 0.105, -0.994,  0.007,  0.043],
            [ 0.994,  0.105, -0.003, -0.025],
            [ 0.002,  0.007,  1.000, -0.283],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.225, -0.974,  0.012,  0.059],
            [ 0.974,  0.225,  0.005, -0.027],
            [-0.008,  0.010,  1.000, -0.265],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "R-TS-P-LO-15": {
        "da3": np.array([
            [ 0.105, -0.994,  0.014,  0.051],
            [ 0.994,  0.104, -0.014, -0.032],
            [ 0.012,  0.016,  1.000, -0.270],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.282, -0.959,  0.012,  0.066],
            [ 0.959,  0.283,  0.011, -0.033],
            [-0.014,  0.009,  1.000, -0.271],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "M-TS-P-HI-16": {
        "da3": np.array([
            [-0.019, -1.000, -0.001,  0.043],
            [ 1.000, -0.019,  0.000, -0.044],
            [-0.000, -0.001,  1.000, -0.281],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.033, -0.999,  0.008,  0.048],
            [ 0.999,  0.033,  0.005, -0.043],
            [-0.005,  0.008,  1.000, -0.277],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "M-LS-P-HI-17": {
        "da3": np.array([
            [ 0.130, -0.991,  0.011,  0.048],
            [ 0.991,  0.130, -0.012, -0.030],
            [ 0.011,  0.012,  1.000, -0.279],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.297, -0.955,  0.012,  0.062],
            [ 0.955,  0.298,  0.015, -0.034],
            [-0.018,  0.007,  1.000, -0.271],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "M-LS-P-LO-18": {
        "da3": np.array([
            [ 0.123, -0.992, -0.000,  0.055],
            [ 0.992,  0.123, -0.009, -0.031],
            [ 0.009,  0.001,  1.000, -0.274],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.278, -0.961,  0.015,  0.061],
            [ 0.960,  0.278,  0.020, -0.036],
            [-0.023,  0.009,  1.000, -0.272],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "M-LS-P-HI-19": {
        "da3": np.array([
            [ 0.085, -0.996, -0.004,  0.055],
            [ 0.996,  0.085, -0.014, -0.030],
            [ 0.015, -0.003,  1.000, -0.275],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.266, -0.964,  0.016,  0.060],
            [ 0.963,  0.267,  0.023, -0.037],
            [-0.027,  0.009,  1.000, -0.275],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "M-LS-P-HI-20": {
        "da3": np.array([
            [ 0.115, -0.993, -0.000,  0.052],
            [ 0.993,  0.115, -0.015, -0.030],
            [ 0.015,  0.001,  1.000, -0.276],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.277, -0.961,  0.005,  0.064],
            [ 0.961,  0.277,  0.010, -0.032],
            [-0.012,  0.002,  1.000, -0.272],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "R-MS-I-LO-21": {
        "da3": np.array([
            [ 0.115, -0.993,  0.014,  0.050],
            [ 0.993,  0.115, -0.005, -0.033],
            [ 0.003,  0.015,  1.000, -0.275],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.288, -0.958,  0.009,  0.068],
            [ 0.958,  0.288,  0.009, -0.032],
            [-0.012,  0.006,  1.000, -0.272],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "R-MS-I-LO-22": {
        "da3": np.array([
            [-0.015, -1.000,  0.016,  0.034],
            [ 1.000, -0.015, -0.000, -0.043],
            [ 0.000,  0.016,  1.000, -0.286],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.051, -0.999,  0.017,  0.046],
            [ 0.999,  0.051,  0.015, -0.044],
            [-0.015,  0.016,  1.000, -0.272],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "R-MS-I-LO-23": {
        "da3": np.array([
            [ 0.007, -1.000,  0.009,  0.040],
            [ 1.000,  0.007,  0.010, -0.046],
            [-0.011,  0.009,  1.000, -0.280],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.028, -1.000,  0.013,  0.047],
            [ 0.999,  0.028,  0.028, -0.050],
            [-0.029,  0.012,  1.000, -0.273],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "R-MS-I-LO-24": {
        "da3": np.array([
            [ 0.112, -0.994,  0.017,  0.050],
            [ 0.994,  0.112, -0.005, -0.032],
            [ 0.003,  0.018,  1.000, -0.280],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.290, -0.957,  0.012,  0.068],
            [ 0.957,  0.290,  0.015, -0.034],
            [-0.018,  0.007,  1.000, -0.275],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "T-TS-P-HI-25": {
        "da3": np.array([
            [-0.034, -0.999, -0.001,  0.042],
            [ 0.999, -0.034,  0.001, -0.043],
            [-0.001, -0.001,  1.000, -0.292],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.031, -0.999,  0.010,  0.047],
            [ 0.999,  0.031,  0.009, -0.043],
            [-0.010,  0.009,  1.000, -0.270],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "M-LS-P-HI-26": {
        "da3": np.array([
            [ 0.098, -0.995,  0.003,  0.051],
            [ 0.995,  0.098, -0.012, -0.030],
            [ 0.012,  0.004,  1.000, -0.278],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.288, -0.958,  0.017,  0.060],
            [ 0.957,  0.288,  0.019, -0.035],
            [-0.024,  0.011,  1.000, -0.272],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "M-MS-P-HI-27": {
        "da3": np.array([
            [ 0.119, -0.993,  0.022,  0.050],
            [ 0.993,  0.119, -0.022, -0.027],
            [ 0.019,  0.025,  1.000, -0.277],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.306, -0.952,  0.015,  0.062],
            [ 0.952,  0.307,  0.013, -0.033],
            [-0.017,  0.010,  1.000, -0.266],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "M-MS-P-HI-28": {
        "da3": np.array([
            [ 0.090, -0.996,  0.011,  0.046],
            [ 0.996,  0.090, -0.016, -0.030],
            [ 0.015,  0.012,  1.000, -0.270],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.285, -0.958,  0.024,  0.060],
            [ 0.958,  0.285,  0.010, -0.033],
            [-0.016,  0.020,  1.000, -0.264],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "M-LS-P-HI-29": {
        "da3": np.array([
            [ 0.101, -0.995,  0.004,  0.051],
            [ 0.995,  0.101, -0.009, -0.030],
            [ 0.008,  0.004,  1.000, -0.280],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.291, -0.957,  0.017,  0.061],
            [ 0.956,  0.291,  0.018, -0.035],
            [-0.022,  0.011,  1.000, -0.270],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "R-LS-P-HI-30": {
        "da3": np.array([
            [ 0.123, -0.992,  0.020,  0.046],
            [ 0.992,  0.123, -0.015, -0.027],
            [ 0.013,  0.022,  1.000, -0.289],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.291, -0.956,  0.020,  0.059],
            [ 0.956,  0.292,  0.009, -0.032],
            [-0.014,  0.017,  1.000, -0.261],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "R-LS-P-LO-31": {
        "da3": np.array([
            [ 0.130, -0.991,  0.008,  0.048],
            [ 0.991,  0.130, -0.002, -0.031],
            [ 0.001,  0.008,  1.000, -0.286],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.275, -0.961,  0.014,  0.061],
            [ 0.961,  0.276,  0.015, -0.036],
            [-0.019,  0.009,  1.000, -0.272],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "R-MS-O-LO-32": {
        "da3": np.array([
            [-0.020, -1.000,  0.009,  0.041],
            [ 1.000, -0.020,  0.000, -0.045],
            [-0.000,  0.009,  1.000, -0.275],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.031, -0.999,  0.016,  0.049],
            [ 0.999,  0.031,  0.015, -0.046],
            [-0.016,  0.015,  1.000, -0.273],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "G-LS-I-LO-33": {
        "da3": np.array([
            [-0.041, -0.999,  0.013,  0.039],
            [ 0.999, -0.041,  0.000, -0.044],
            [ 0.000,  0.013,  1.000, -0.279],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.029, -1.000,  0.012,  0.050],
            [ 0.999,  0.029,  0.018, -0.048],
            [-0.019,  0.011,  1.000, -0.273],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "G-LS-P-LO-34": {
        "da3": np.array([
            [-0.005, -1.000,  0.013,  0.035],
            [ 1.000, -0.005,  0.004, -0.044],
            [-0.004,  0.013,  1.000, -0.285],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.036, -0.999,  0.011,  0.044],
            [ 0.999,  0.036,  0.016, -0.046],
            [-0.016,  0.011,  1.000, -0.271],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "M-MS-P-HI-35": {
        "da3": np.array([
            [ 0.088, -0.996,  0.008,  0.042],
            [ 0.996,  0.088, -0.003, -0.027],
            [ 0.002,  0.008,  1.000, -0.277],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.241, -0.970,  0.019,  0.059],
            [ 0.971,  0.241,  0.010, -0.027],
            [-0.014,  0.016,  1.000, -0.271],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "R-LS-I-HI-36": {
        "da3": np.array([
            [ 0.001, -1.000,  0.012,  0.045],
            [ 1.000,  0.001,  0.006, -0.044],
            [-0.006,  0.012,  1.000, -0.279],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.042, -0.999,  0.013,  0.051],
            [ 0.999,  0.042,  0.014, -0.045],
            [-0.015,  0.012,  1.000, -0.270],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
    "T-LS-I-HI-37": {
        "da3": np.array([
            [ 0.148, -0.989,  0.022,  0.043],
            [ 0.989,  0.148, -0.012, -0.029],
            [ 0.009,  0.024,  1.000, -0.276],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
        "vggt": np.array([
            [ 0.305, -0.952,  0.012,  0.062],
            [ 0.952,  0.305,  0.011, -0.033],
            [-0.014,  0.008,  1.000, -0.268],
            [ 0.000,  0.000,  0.000,  1.000],
        ]),
    },
}


# Per-sample VARIANT overrides: sample -> variant -> model -> 4x4.
# variant is "multiple", "stacked", or a single-orientation folder name
# (e.g. "orientation_b"). Anything not listed here uses the sample's base
# matrix in SAMPLE_MODEL_TRANSFORMS above (the plain per-sample da3/vggt
# matrices, i.e. single / orientation_a).
SAMPLE_VARIANT_TRANSFORMS = {
    "G-MS-I-LO-1": {
        "orientation_b": {
            "da3": np.array([
                [ 0.031, -0.999,  0.009,  0.038],
                [ 0.999,  0.031,  0.012, -0.045],
                [-0.012,  0.009,  1.000, -0.283],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
            "vggt": np.array([
                [ 0.032, -0.999,  0.007,  0.046],
                [ 0.999,  0.032,  0.023, -0.047],
                [-0.024,  0.006,  1.000, -0.273],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
        "multiple": {
            "da3": np.array([
                [ 0.037, -0.999,  0.019,  0.032],
                [ 0.999,  0.037,  0.012, -0.045],
                [-0.013,  0.018,  1.000, -0.284],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
            "vggt": np.array([
                [ 0.039, -0.999,  0.011,  0.045],
                [ 0.999,  0.039,  0.018, -0.047],
                [-0.019,  0.010,  1.000, -0.276],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
        "stacked": {
            "da3": np.array([
                [ 0.003, -1.000,  0.007,  0.036],
                [ 1.000,  0.003,  0.008, -0.045],
                [-0.009,  0.007,  1.000, -0.285],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
            "vggt": np.array([
                [ 0.037, -0.999,  0.013,  0.046],
                [ 0.999,  0.037,  0.012, -0.045],
                [-0.012,  0.012,  1.000, -0.281],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
    },
    "G-MS-O-LO-2": {
        "multiple": {
            "da3": np.array([
                [-0.003, -1.000,  0.008,  0.039],
                [ 1.000, -0.003,  0.003, -0.045],
                [-0.003,  0.008,  1.000, -0.279],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
    },
    "R-TS-I-HI-6": {
        "stacked": {
            "da3": np.array([
                [-0.008, -1.000,  0.004,  0.034],
                [ 1.000, -0.008,  0.009, -0.044],
                [-0.009,  0.004,  1.000, -0.295],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
    },
    "G-TS-O-HI-7": {
        "multiple": {
            "vggt": np.array([
                [ 0.031, -1.000, -0.000,  0.053],
                [ 0.999,  0.031,  0.017, -0.045],
                [-0.017, -0.001,  1.000, -0.278],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
    },
    "M-MS-P-HI-9": {
        "multiple": {
            "vggt": np.array([
                [ 0.311, -0.950,  0.012,  0.062],
                [ 0.950,  0.311,  0.015, -0.034],
                [-0.018,  0.007,  1.000, -0.273],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
        "stacked": {
            "vggt": np.array([
                [ 0.295, -0.956,  0.010,  0.063],
                [ 0.956,  0.295,  0.008, -0.032],
                [-0.011,  0.007,  1.000, -0.272],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
    },
    "R-MS-I-HI-11": {
        "stacked": {
            "vggt": np.array([
                [ 0.290, -0.957,  0.011,  0.067],
                [ 0.957,  0.290,  0.008, -0.032],
                [-0.010,  0.008,  1.000, -0.279],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
    },
    "R-MS-P-LO-12": {
        "orientation_c": {
            "da3": np.array([
                [-0.019, -1.000,  0.005,  0.041],
                [ 1.000, -0.019,  0.002, -0.045],
                [-0.001,  0.005,  1.000, -0.279],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
        "orientation_d": {
            "da3": np.array([
                [-0.017, -1.000, -0.000,  0.042],
                [ 1.000, -0.017,  0.002, -0.045],
                [-0.002, -0.000,  1.000, -0.278],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
        "multiple": {
            "vggt": np.array([
                [ 0.050, -0.999,  0.010,  0.043],
                [ 0.999,  0.050,  0.016, -0.044],
                [-0.017,  0.009,  1.000, -0.279],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
        "stacked": {
            "vggt": np.array([
                [ 0.042, -0.999,  0.005,  0.044],
                [ 0.999,  0.042,  0.014, -0.044],
                [-0.014,  0.004,  1.000, -0.277],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
    },
    "R-MS-I-LO-14": {
        "multiple": {
            "da3": np.array([
                [ 0.093, -0.996,  0.002,  0.045],
                [ 0.996,  0.093, -0.003, -0.027],
                [ 0.002,  0.003,  1.000, -0.272],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
            "vggt": np.array([
                [ 0.242, -0.970,  0.012,  0.058],
                [ 0.970,  0.242,  0.009, -0.025],
                [-0.011,  0.010,  1.000, -0.281],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
    },
    "R-TS-P-LO-15": {
        "multiple": {
            "da3": np.array([
                [ 0.137, -0.991,  0.013,  0.051],
                [ 0.991,  0.136, -0.014, -0.029],
                [ 0.012,  0.015,  1.000, -0.279],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
            "vggt": np.array([
                [ 0.309, -0.951,  0.006,  0.071],
                [ 0.951,  0.309,  0.010, -0.031],
                [-0.012,  0.003,  1.000, -0.280],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
        "stacked": {
            "da3": np.array([
                [ 0.990,  0.141, -0.006,  0.132],
                [-0.141,  0.990,  0.005, -0.058],
                [ 0.007, -0.004,  1.000, -0.282],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
    },
    "M-LS-P-LO-18": {
        "multiple": {
            "da3": np.array([
                [ 0.108, -0.994, -0.006,  0.054],
                [ 0.994,  0.108, -0.009, -0.030],
                [ 0.010, -0.005,  1.000, -0.281],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
            "vggt": np.array([
                [ 0.289, -0.957,  0.009,  0.061],
                [ 0.957,  0.289,  0.016, -0.032],
                [-0.018,  0.004,  1.000, -0.277],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
        "stacked": {
            "vggt": np.array([
                [ 0.287, -0.958,  0.014,  0.060],
                [ 0.958,  0.287,  0.001, -0.028],
                [-0.005,  0.013,  1.000, -0.280],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
    },
    "M-LS-P-HI-19": {
        "multiple": {
            "da3": np.array([
                [ 0.107, -0.994, -0.002,  0.055],
                [ 0.994,  0.107, -0.011, -0.030],
                [ 0.011, -0.001,  1.000, -0.278],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
            "vggt": np.array([
                [ 0.296, -0.955,  0.006,  0.066],
                [ 0.955,  0.296,  0.014, -0.032],
                [-0.015,  0.002,  1.000, -0.275],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
    },
    "R-MS-I-LO-21": {
        "stacked": {
            "vggt": np.array([
                [ 0.285, -0.959,  0.008,  0.067],
                [ 0.959,  0.285,  0.008, -0.030],
                [-0.010,  0.006,  1.000, -0.283],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
    },
    "R-MS-I-LO-22": {
        "multiple": {
            "vggt": np.array([
                [ 0.049, -0.999,  0.013,  0.044],
                [ 0.999,  0.050,  0.018, -0.045],
                [-0.018,  0.012,  1.000, -0.284],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
        "stacked": {
            "vggt": np.array([
                [ 0.041, -0.999,  0.010,  0.047],
                [ 0.999,  0.041,  0.015, -0.045],
                [-0.015,  0.010,  1.000, -0.282],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
    },
    "R-MS-I-LO-23": {
        "stacked": {
            "vggt": np.array([
                [ 0.041, -0.999,  0.009,  0.044],
                [ 0.999,  0.041,  0.013, -0.044],
                [-0.013,  0.008,  1.000, -0.281],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
    },
    "R-MS-I-LO-24": {
        "stacked": {
            "vggt": np.array([
                [ 0.291, -0.957,  0.008,  0.067],
                [ 0.957,  0.292,  0.008, -0.030],
                [-0.010,  0.005,  1.000, -0.282],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
    },
    "M-MS-P-HI-27": {
        "multiple": {
            "vggt": np.array([
                [ 0.297, -0.955,  0.007,  0.064],
                [ 0.955,  0.297,  0.011, -0.030],
                [-0.013,  0.004,  1.000, -0.274],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
        "stacked": {
            "da3": np.array([
                [ 0.081, -0.997,  0.018,  0.044],
                [ 0.997,  0.081, -0.010, -0.032],
                [ 0.009,  0.019,  1.000, -0.265],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
            "vggt": np.array([
                [ 0.314, -0.949,  0.016,  0.063],
                [ 0.949,  0.314,  0.021, -0.033],
                [-0.025,  0.009,  1.000, -0.273],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
    },
    "M-MS-P-HI-28": {
        "multiple": {
            "da3": np.array([
                [ 0.117, -0.993,  0.012,  0.048],
                [ 0.993,  0.116, -0.014, -0.028],
                [ 0.012,  0.014,  1.000, -0.285],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
        "stacked": {
            "vggt": np.array([
                [ 0.301, -0.954,  0.003,  0.067],
                [ 0.954,  0.301,  0.015, -0.033],
                [-0.015, -0.002,  1.000, -0.275],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
    },
    "R-LS-P-HI-30": {
        "multiple": {
            "da3": np.array([
                [ 0.126, -0.992,  0.006,  0.048],
                [ 0.992,  0.126, -0.013, -0.028],
                [ 0.012,  0.007,  1.000, -0.279],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
            "vggt": np.array([
                [ 0.293, -0.956,  0.008,  0.063],
                [ 0.956,  0.293,  0.013, -0.032],
                [-0.015,  0.004,  1.000, -0.276],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
    },
    "R-LS-P-LO-31": {
        "multiple": {
            "vggt": np.array([
                [ 0.298, -0.954,  0.017,  0.061],
                [ 0.954,  0.299,  0.014, -0.031],
                [-0.018,  0.012,  1.000, -0.283],
                [ 0.000,  0.000,  0.000,  1.000],
            ]),
        },
    },
}


def get_transform(sample, model, config="single", orientation=None):
    """Resolve the initial transform for one (sample, config, orientation, model).

    Priority:
      1. SAMPLE_VARIANT_TRANSFORMS[sample][variant][model], where variant is
         the config ("multiple"/"stacked") or, for single, the orientation name
      2. SAMPLE_MODEL_TRANSFORMS[sample][model]  (the sample's base matrix)
      3. MODEL_TRANSFORMS[model]                 (generic fallback)
    """
    variant = config if config in ("multiple", "stacked") else orientation
    if variant:
        v = SAMPLE_VARIANT_TRANSFORMS.get(sample, {}).get(variant, {})
        if model in v:
            return v[model]
    base = SAMPLE_MODEL_TRANSFORMS.get(sample, {})
    if model in base:
        if variant and variant not in ("orientation_a",):
            print(f"  NOTE: no {variant}-specific transform for {sample}/{model}; using the sample's base matrix.")
        return base[model]
    print(f"  NOTE: no sample-specific transform for {sample}/{model}; using MODEL_TRANSFORMS fallback.")
    return MODEL_TRANSFORMS[model]


SUMMARY_OUTPUT_DIR = ROOT  # where single_results.xlsx etc. get written


# ---------------------------------------------------------------------------
# Core comparison logic (adapted from the original compare.py)
# ---------------------------------------------------------------------------

def calculate_completeness(gt_pc, da3_pc, distance_threshold):
    """Custom completeness metric: fraction/avg of points within threshold."""
    distances = np.asarray(gt_pc.compute_point_cloud_distance(da3_pc))
    valid_distances = distances[distances <= distance_threshold]
    n_val = len(valid_distances)
    d_c_avg = np.mean(valid_distances) if n_val > 0 else 0.0
    return n_val, d_c_avg


def compute_metrics(da3_pc_path, gt_pc_path, output_dir, transform_matrix, recon_scale=1.0):
    """
    Runs the full alignment + metric pipeline for one (reconstruction, gt)
    pair. Writes debug .ply files and metrics.csv into output_dir, and
    returns a dict of {metric_label: value} for downstream Excel compilation.

    recon_scale: uniform scale applied to the reconstruction BEFORE the
    transform matrix (e.g. vggt needs a different scale than da3).
    """
    os.makedirs(output_dir, exist_ok=True)

    # 1. Load point clouds
    source = o3d.io.read_point_cloud(gt_pc_path)   # Ground truth
    target = o3d.io.read_point_cloud(da3_pc_path)  # Reconstruction

    print("  Scaling ground truth point cloud...")
    source.scale(GT_SCALE, center=np.array([0., 0., 0.]))

    if recon_scale != 1.0:
        print(f"  Scaling reconstruction by {recon_scale}...")
        target.scale(recon_scale, center=np.array([0., 0., 0.]))

    print("  Applying initial transformation matrix to reconstruction...")
    target.transform(transform_matrix)

    # 2. Crop reconstruction to GT bounding box in X/Y only
    print("  Cropping reconstruction to GT bounding box (X/Y only)...")
    gt_bbox = source.get_axis_aligned_bounding_box()
    gt_min = gt_bbox.get_min_bound()
    gt_max = gt_bbox.get_max_bound()

    target_points = np.asarray(target.points)
    mask = (
        (target_points[:, 0] >= gt_min[0]) & (target_points[:, 0] <= gt_max[0]) &
        (target_points[:, 1] >= gt_min[1]) & (target_points[:, 1] <= gt_max[1])
    )
    target = target.select_by_index(np.where(mask)[0])

    print(f"  GT points: {len(source.points)} | Reconstruction after XY crop: {len(target.points)}")

    # 3. First (global) ICP
    print("  Running global ICP alignment...")
    reg_p2p_global = o3d.pipelines.registration.registration_icp(
        source, target, ICP_THRESHOLD, np.identity(4),
        o3d.pipelines.registration.TransformationEstimationPointToPoint(),
        o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=20000),
    )
    source.transform(reg_p2p_global.transformation)

    o3d.io.write_point_cloud(
        os.path.join(output_dir, "1st_cropped_results.ply"), source + target
    )

    # 4. Extract central region
    combined_points = np.concatenate((np.asarray(source.points), np.asarray(target.points)), axis=0)
    centroid = np.mean(combined_points, axis=0)
    half_size = CROP_SIZE / 2.0
    min_bound = centroid - np.array([half_size, half_size, half_size])
    max_bound = centroid + np.array([half_size, half_size, half_size])
    center_bbox = o3d.geometry.AxisAlignedBoundingBox(min_bound, max_bound)

    source_cropped = source.crop(center_bbox)
    target_cropped = target.crop(center_bbox)

    if len(source_cropped.points) == 0 or len(target_cropped.points) == 0:
        raise ValueError("Central-region crop resulted in an empty point cloud (check scale/units).")

    # 5. Second (local) ICP on cropped region
    print("  Running local ICP alignment on cropped region...")
    reg_p2p_local = o3d.pipelines.registration.registration_icp(
        source_cropped, target_cropped, ICP_THRESHOLD, np.identity(4),
        o3d.pipelines.registration.TransformationEstimationPointToPoint(),
        o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=20000),
    )
    source_cropped.transform(reg_p2p_local.transformation)

    o3d.io.write_point_cloud(os.path.join(output_dir, "cropped_reconstruction.ply"), target_cropped)
    o3d.io.write_point_cloud(
        os.path.join(output_dir, "compare_cropped_results.ply"), source_cropped + target_cropped
    )

    # 6. Metrics with table
    dists1 = np.asarray(source_cropped.compute_point_cloud_distance(target_cropped))
    dists2 = np.asarray(target_cropped.compute_point_cloud_distance(source_cropped))
    chamfer_dist = np.mean(dists1 ** 2) + np.mean(dists2 ** 2)
    hausdorff = max(np.max(dists1), np.max(dists2))
    icp_fitness = reg_p2p_local.fitness

    completeness_scores = {}
    for t in COMPLETENESS_THRESHOLDS:
        n_val, score = calculate_completeness(source_cropped, target_cropped, t)
        completeness_scores[t] = (n_val, score)

    # 7. Table-surface removal
    print("  Removing table surface from GT and reconstruction...")
    _, inliers_crop_gt = source_cropped.segment_plane(
        distance_threshold=PLANE_DISTANCE_THRESHOLD, ransac_n=3, num_iterations=1000
    )
    parts_gt = source_cropped.select_by_index(inliers_crop_gt, invert=True)

    _, inliers_crop_rec = target_cropped.segment_plane(
        distance_threshold=PLANE_DISTANCE_THRESHOLD, ransac_n=3, num_iterations=1000
    )
    parts_rec = target_cropped.select_by_index(inliers_crop_rec, invert=True)

    o3d.io.write_point_cloud(
        os.path.join(output_dir, "compare_cropped_results_without_table.ply"), parts_gt + parts_rec
    )

    reg_p2p_parts = o3d.pipelines.registration.registration_icp(
        parts_gt, parts_rec, ICP_THRESHOLD, np.identity(4),
        o3d.pipelines.registration.TransformationEstimationPointToPoint(),
        o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=20000),
    )

    dists1_parts = np.asarray(parts_gt.compute_point_cloud_distance(parts_rec))
    dists2_parts = np.asarray(parts_rec.compute_point_cloud_distance(parts_gt))
    chamfer_dist_parts = np.mean(dists1_parts ** 2) + np.mean(dists2_parts ** 2)
    hausdorff_parts = max(np.max(dists1_parts), np.max(dists2_parts))
    icp_fitness_parts = reg_p2p_parts.fitness

    completeness_scores_parts = {}
    for t in COMPLETENESS_THRESHOLDS:
        n_val, score = calculate_completeness(parts_gt, parts_rec, t)
        completeness_scores_parts[t] = (n_val, score)

    # 8. Write per-run metrics.csv (same format as the original script)
    csv_path = os.path.join(output_dir, "metrics.csv")
    with open(csv_path, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Value", "Unit"])
        writer.writerow(["Total points (ground truth cropped)", f"{len(source_cropped.points)}", "-"])
        writer.writerow(["Total points (reconstruction cropped)", f"{len(target_cropped.points)}", "-"])
        writer.writerow(["Chamfer Distance", f"{chamfer_dist * 1e6:.4f}", "mm^2"])
        writer.writerow(["Hausdorff Distance", f"{hausdorff * 1e3:.4f}", "mm"])
        writer.writerow(["ICP Fitness", f"{icp_fitness:.4f}", "-"])
        for t, v in completeness_scores.items():
            writer.writerow([f"Completeness @ {t*1e3} mm", f"{v[1]*1e3:.4f}", "mm"])
            writer.writerow([f"Completeness Valid Points @ {t*1e3} mm", f"{v[0]}", "-"])
            writer.writerow([f"Completeness Valid Point Ratio @ {t*1e3} mm", f"{v[0]/len(source_cropped.points)}", "-"])
        writer.writerow(["Total points (ground truth without table)", f"{len(parts_gt.points)}", "-"])
        writer.writerow(["Total points (reconstruction without table)", f"{len(parts_rec.points)}", "-"])
        writer.writerow(["Chamfer Distance (without table)", f"{chamfer_dist_parts * 1e6:.4f}", "mm^2"])
        writer.writerow(["Hausdorff Distance (without table)", f"{hausdorff_parts * 1e3:.4f}", "mm"])
        writer.writerow(["ICP Fitness (without table)", f"{icp_fitness_parts:.4f}", "-"])
        for t, v in completeness_scores_parts.items():
            writer.writerow([f"Completeness (without table) @ {t*1e3} mm", f"{v[1]*1e3:.4f}", "mm"])
            writer.writerow([f"Completeness Valid Points (without table) @ {t*1e3} mm", f"{v[0]}", "-"])
            writer.writerow([f"Completeness Valid Point Ratio (without table) @ {t*1e3} mm", f"{v[0]/len(parts_gt.points)}", "-"])

    # 9. Build the metrics dict returned for Excel compilation
    metrics = {
        "Total points (GT cropped)": len(source_cropped.points),
        "Total points (Recon cropped)": len(target_cropped.points),
        "Chamfer Distance (mm^2)": chamfer_dist * 1e6,
        "Hausdorff Distance (mm)": hausdorff * 1e3,
        "ICP Fitness": icp_fitness,
    }
    for t, v in completeness_scores.items():
        label = f"{t*1e3:g}mm"
        metrics[f"Completeness @ {label} (mm)"] = v[1] * 1e3
        metrics[f"Completeness Valid Points @ {label}"] = v[0]
        metrics[f"Completeness Valid Ratio @ {label}"] = v[0] / len(source_cropped.points)

    metrics["Total points (GT no-table)"] = len(parts_gt.points)
    metrics["Total points (Recon no-table)"] = len(parts_rec.points)
    metrics["Chamfer Distance no-table (mm^2)"] = chamfer_dist_parts * 1e6
    metrics["Hausdorff Distance no-table (mm)"] = hausdorff_parts * 1e3
    metrics["ICP Fitness no-table"] = icp_fitness_parts
    for t, v in completeness_scores_parts.items():
        label = f"{t*1e3:g}mm"
        metrics[f"Completeness no-table @ {label} (mm)"] = v[1] * 1e3
        metrics[f"Completeness Valid Points no-table @ {label}"] = v[0]
        metrics[f"Completeness Valid Ratio no-table @ {label}"] = v[0] / len(parts_gt.points)

    return metrics


# ---------------------------------------------------------------------------
# Batch driver
# ---------------------------------------------------------------------------

def run_one(recon_path, gt_path, output_dir, transform_matrix, sample, config, model, extra=None, recon_scale=1.0):
    """Runs compute_metrics for one (sample, config, model) combo, tagging the result row."""
    row = {"Sample": sample}
    if extra:
        row.update(extra)
    print(f"[{sample}/{config}" + (f"/{extra.get('Orientation')}" if extra else "") + f"/{model}] running...")
    try:
        metrics = compute_metrics(recon_path, gt_path, output_dir, transform_matrix, recon_scale=recon_scale)
        for k, v in metrics.items():
            row[f"{k} ({model})"] = v
        print(f"  -> OK")
    except Exception as e:
        print(f"  -> FAILED: {e}")
        traceback.print_exc()
        row[f"ERROR ({model})"] = str(e)
    return row


# ---------------------------------------------------------------------------
# Sample-name parsing: <Surface>-<Size>-<Shape>-<Complexity>-<Ser. no.>
#   e.g. "G-MS-I-LO-1"  ->  Glossy, Medium, Isotropic, Low, #1
# ---------------------------------------------------------------------------
SURFACE_NAMES = {"R": "Rough", "G": "Glossy", "M": "Metallic", "T": "Transparent"}
SIZE_NAMES = {"TS": "Tiny", "MS": "Medium", "LS": "Large"}
SHAPE_NAMES = {"O": "Oblate", "I": "Isotropic", "P": "Prolate"}
COMPLEXITY_NAMES = {"HI": "High", "LO": "Low"}

# False -> columns hold the short codes (R, TS, O, HI ...);
# True  -> columns hold the full words (Rough, Tiny, Oblate, High ...).
USE_FULL_ATTRIBUTE_NAMES = False

ATTRIBUTE_COLS = ["Surface", "Size", "Shape", "Complexity"]


def parse_sample_name(sample):
    """Split a sample name into its attribute columns. Unparseable -> blanks."""
    parts = str(sample).strip().split("-")
    if len(parts) < 4:
        return {c: "" for c in ATTRIBUTE_COLS}
    codes = parts[:4]
    maps = [SURFACE_NAMES, SIZE_NAMES, SHAPE_NAMES, COMPLEXITY_NAMES]
    out = {}
    for col, code, mapping in zip(ATTRIBUTE_COLS, codes, maps):
        if code not in mapping:
            print(f"  NOTE: unrecognised {col} code '{code}' in sample name '{sample}'.")
        out[col] = mapping.get(code, code) if USE_FULL_ATTRIBUTE_NAMES else code
    return out


def merge_rows(rows_by_model, key_fields):
    """Merges the da3-row and vggt-row for the same sample/orientation into one row."""
    merged = {}
    for row in rows_by_model:
        for k, v in row.items():
            merged[k] = v
    return merged


def write_two_row_header_excel(df, id_cols, metric_base_names, leftover_cols, out_path, sheet_name):
    """
    Writes df to an .xlsx file with a two-row header:
      Row 1: Sample | Surface | Size | Shape | Complexity | Orientation | Metric1 (merged across da3/vggt) | Metric2 (merged) | ...
      Row 2: (merged from row1)   | (merged from row1) | da3 | vggt  | da3 | vggt | ...
    Data starts on row 3.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name[:31]  # Excel sheet name limit

    bold = Font(bold=True)
    center = Alignment(horizontal="center", vertical="center")

    col_idx = 1

    # ID columns: merged vertically across both header rows.
    for id_col in id_cols:
        ws.cell(row=1, column=col_idx, value=id_col).font = bold
        ws.merge_cells(start_row=1, start_column=col_idx, end_row=2, end_column=col_idx)
        ws.cell(row=1, column=col_idx).alignment = center
        col_idx += 1

    # Metric columns: merged horizontally across da3/vggt in row 1,
    # with model names as sub-header in row 2.
    metric_col_map = {}  # (base, model) -> column index
    for base in metric_base_names:
        start_col = col_idx
        present_models = [m for m in MODELS if f"{base} ({m})" in df.columns]
        if not present_models:
            continue
        for model in present_models:
            ws.cell(row=2, column=col_idx, value=model).font = bold
            ws.cell(row=2, column=col_idx).alignment = center
            metric_col_map[(base, model)] = col_idx
            col_idx += 1
        end_col = col_idx - 1
        ws.cell(row=1, column=start_col, value=base).font = bold
        ws.cell(row=1, column=start_col).alignment = center
        if end_col > start_col:
            ws.merge_cells(start_row=1, start_column=start_col, end_row=1, end_column=end_col)

    # Leftover columns (e.g. ERROR (da3)): single column, merged vertically.
    leftover_col_map = {}
    for col in leftover_cols:
        ws.cell(row=1, column=col_idx, value=col).font = bold
        ws.merge_cells(start_row=1, start_column=col_idx, end_row=2, end_column=col_idx)
        ws.cell(row=1, column=col_idx).alignment = center
        leftover_col_map[col] = col_idx
        col_idx += 1

    # Data rows, starting at row 3.
    for r, row in enumerate(df.to_dict(orient="records"), start=3):
        for i, id_col in enumerate(id_cols):
            ws.cell(row=r, column=i + 1, value=row.get(id_col, ""))
        for (base, model), c in metric_col_map.items():
            ws.cell(row=r, column=c, value=row.get(f"{base} ({model})", ""))
        for col, c in leftover_col_map.items():
            ws.cell(row=r, column=c, value=row.get(col, ""))

    # Reasonable column widths.
    total_cols = col_idx - 1
    for c in range(1, total_cols + 1):
        ws.column_dimensions[get_column_letter(c)].width = 16

    wb.save(out_path)


def main():
    results = {"single": [], "multiple": [], "stacked": []}

    if not os.path.isdir(ROOT):
        raise SystemExit(f"ROOT does not exist: {ROOT}")

    samples = sorted(
        d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d))
    )

    for sample in samples:
        sample_dir = os.path.join(ROOT, sample)

        # --- multiple & stacked: one ground_truth.ply per config dir ---
        for config in ["multiple", "stacked"]:
            config_dir = os.path.join(sample_dir, config)
            if not os.path.isdir(config_dir):
                continue

            gt_path = os.path.join(config_dir, "ground_truth.ply")
            if not os.path.isfile(gt_path):
                print(f"[{sample}/{config}] WARNING: missing ground_truth.ply, skipping.")
                continue

            model_rows = []
            for model in MODELS:
                recon_path = os.path.join(config_dir, model, "final_processed.ply")
                if not os.path.isfile(recon_path):
                    print(f"[{sample}/{config}/{model}] WARNING: missing final_processed.ply, skipping.")
                    continue
                output_dir = os.path.join(config_dir, model)
                row = run_one(
                    recon_path, gt_path, output_dir,
                    get_transform(sample, model, config), sample, config, model,
                    recon_scale=MODEL_SCALES[model],
                )
                model_rows.append(row)

            if model_rows:
                results[config].append(merge_rows(model_rows, ["Sample"]))

        # --- single: EITHER orientation subfolders (each with its own
        # ground_truth.ply) OR, sometimes, no orientation layer at all
        # (ground_truth.ply directly inside single/, same layout as
        # multiple/stacked). Handle both.
        single_dir = os.path.join(sample_dir, "single")
        if os.path.isdir(single_dir):
            direct_gt_path = os.path.join(single_dir, "ground_truth.ply")

            if os.path.isfile(direct_gt_path):
                # No orientation subfolder for this sample.
                model_rows = []
                for model in MODELS:
                    recon_path = os.path.join(single_dir, model, "final_processed.ply")
                    if not os.path.isfile(recon_path):
                        print(f"[{sample}/single/{model}] WARNING: missing final_processed.ply, skipping.")
                        continue
                    output_dir = os.path.join(single_dir, model)
                    row = run_one(
                        recon_path, direct_gt_path, output_dir,
                        get_transform(sample, model, "single"), sample, "single", model,
                        extra={"Orientation": "-"},
                        recon_scale=MODEL_SCALES[model],
                    )
                    model_rows.append(row)

                if model_rows:
                    results["single"].append(merge_rows(model_rows, ["Sample", "Orientation"]))

            else:
                # Orientation subfolders expected, each with its own ground_truth.ply.
                orientations = sorted(
                    d for d in os.listdir(single_dir) if os.path.isdir(os.path.join(single_dir, d))
                )
                for orientation in orientations:
                    orientation_dir = os.path.join(single_dir, orientation)
                    gt_path = os.path.join(orientation_dir, "ground_truth.ply")
                    if not os.path.isfile(gt_path):
                        print(f"[{sample}/single/{orientation}] WARNING: missing ground_truth.ply, skipping.")
                        continue

                    model_rows = []
                    for model in MODELS:
                        recon_path = os.path.join(orientation_dir, model, "final_processed.ply")
                        if not os.path.isfile(recon_path):
                            print(f"[{sample}/single/{orientation}/{model}] WARNING: missing final_processed.ply, skipping.")
                            continue
                        output_dir = os.path.join(orientation_dir, model)
                        row = run_one(
                            recon_path, gt_path, output_dir,
                            get_transform(sample, model, "single", orientation), sample, "single", model,
                            extra={"Orientation": orientation},
                            recon_scale=MODEL_SCALES[model],
                        )
                        model_rows.append(row)

                    if model_rows:
                        results["single"].append(merge_rows(model_rows, ["Sample", "Orientation"]))

    # -----------------------------------------------------------------
    # Write Excel summaries, one file per config type
    # -----------------------------------------------------------------
    os.makedirs(SUMMARY_OUTPUT_DIR, exist_ok=True)

    for config, rows in results.items():
        if not rows:
            print(f"No results for '{config}', skipping Excel file.")
            continue

        df = pd.DataFrame(rows)

        # Add Surface / Size / Shape / Complexity right after Sample.
        attrs = df["Sample"].apply(parse_sample_name).apply(pd.Series)
        for i, col in enumerate(ATTRIBUTE_COLS):
            df.insert(df.columns.get_loc("Sample") + 1 + i, col, attrs[col])

        # Identify columns (Sample, attributes, Orientation) vs metric columns.
        id_cols = [c for c in ["Sample"] + ATTRIBUTE_COLS + ["Orientation"] if c in df.columns]

        metric_base_names = []
        seen = set()
        for col in df.columns:
            if col in id_cols:
                continue
            for model in MODELS:
                suffix = f" ({model})"
                if col.endswith(suffix):
                    base = col[: -len(suffix)]
                    if base not in seen:
                        seen.add(base)
                        metric_base_names.append(base)

        # Leftover columns that don't match the "<metric> (<model>)" pattern
        # (e.g. an ERROR column) get appended as their own single-row-span metric.
        leftover_cols = [
            c for c in df.columns
            if c not in id_cols and not any(c == f"{base} ({m})" for base in metric_base_names for m in MODELS)
        ]

        out_path = os.path.join(SUMMARY_OUTPUT_DIR, f"{config}_results.xlsx")
        write_two_row_header_excel(df, id_cols, metric_base_names, leftover_cols, out_path, config)
        print(f"Wrote {out_path} ({len(df)} rows)")

    print("Batch comparison complete.")


if __name__ == "__main__":
    main()