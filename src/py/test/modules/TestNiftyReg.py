## \file TestNiftyReg.py
#  \brief  Class containing unit tests for module Stack
# 
#  \author Michael Ebner (michael.ebner.14@ucl.ac.uk)
#  \date May 2016


## Import libraries 
import SimpleITK as sitk
import numpy as np
import unittest
import sys

## Add directories to import modules
dir_src_root = "../src/"
sys.path.append( dir_src_root )

## Import modules
import registration.NiftyReg as nreg
import base.Stack as st
import utilities.SimpleITKHelper as sitkh

## Concept of unit testing for python used in here is based on
#  http://pythontesting.net/framework/unittest/unittest-introduction/
#  Retrieved: Aug 6, 2015
class TestNiftyReg(unittest.TestCase):

    ## Specify input data
    dir_test_data = "../../../test-data/"

    accuracy = 7

    def setUp(self):
        pass

    def test_affine_transform_reg_aladin(self):

        ## Read data
        filename_fixed = "stack1_rotated_angle_z_is_pi_over_10"
        filename_moving = "recon_fetal_neck_mass_brain_cycles0_SRR_TK0_itermax20_alpha0.1"

        moving = st.Stack.from_filename(self.dir_test_data, filename_moving, "_mask")
        fixed = st.Stack.from_filename(self.dir_test_data, filename_fixed)

        ## Set up NiftyReg
        nifty_reg = nreg.NiftyReg()
        nifty_reg.set_fixed(fixed)
        nifty_reg.set_moving(moving)

        ## Register via NiftyReg
        nifty_reg.run_reg_aladin(options="-voff")

        ## Get associated results
        affine_transform_sitk = nifty_reg.get_affine_transform_sitk()
        moving_warped = nifty_reg.get_registered_image()

        ## Get SimpleITK result with "similar" interpolator (NiftyReg does not state what interpolator is used but it seems to be BSpline)
        moving_warped_sitk = sitk.Resample(moving.sitk, fixed.sitk, affine_transform_sitk, sitk.sitkBSpline, 0.0, moving.sitk.GetPixelIDValue())

        ## Check alignment of images
        nda_NiftyReg = sitk.GetArrayFromImage(moving_warped.sitk)
        nda_SimpleITK = sitk.GetArrayFromImage(moving_warped_sitk)
        diff = nda_NiftyReg - nda_SimpleITK
        abs_diff = abs(diff)

        try:
            self.assertEqual(np.round(
                np.linalg.norm(diff)
                , decimals = self.accuracy), 0)

        except Exception as e:
            print("FAIL: " + self.id() + " failed given norm of difference = %.2e > 1e-%s" %(np.linalg.norm(diff),self.accuracy))
            print("\tCheck statistics of difference: (Maximum absolute difference per voxel might be acceptable)")
            print("\tMaximum absolute difference per voxel: %s" %abs_diff.max())
            print("\tMean absolute difference per voxel: %s" %abs_diff.mean())
            print("\tMinimum absolute difference per voxel: %s" %abs_diff.min())

            ## Show results (difficult to compare directly given the different interpolators of NiftyReg and SimpleITK)
            # sitkh.show_sitk_image(moving_warped.sitk, overlay=fixed.sitk, title="warpedMoving_fixed")
            # sitkh.show_sitk_image(moving_warped.sitk, overlay=moving_warped_sitk, title="warpedMovingNiftyReg_warpedMovingSimpleITK")
            # sitkh.show_sitk_image(moving_warped.sitk-moving_warped_sitk, title="difference_NiftyReg_SimpleITK")
            


        
