#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2025-04-08 14:58
Author: calebharada

192310_DataSetup.py

    Description: combines RV datasets for HD 192310
"""

import radvel
import pandas as pd

SYSTEM_HD = 192310
STD_COL_NAMES = ['time', 'mnvel', 'errvel', 'tel']


def data_setup():
    """Main data setup function. 

    Calls other functions to read in RV data and combines each data set
    into a single table. Saves an unbinned and binned RV data file.
    """

    # create new DF and add each data source
    combined_data = pd.DataFrame(columns=STD_COL_NAMES)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # add HIRES (Keck)
    combined_data = pd.concat([combined_data, 
        get_EBPS_HIRES(f'{SYSTEM_HD}_EBPS_HIRES.vels')],
        ignore_index=True)
     # add HAPRS (ESO)
    combined_data = pd.concat([combined_data, 
        get_RVBank_HARPS(f'{SYSTEM_HD}_RVBank_HARPS.csv')],
        ignore_index=True )
    # add UCLES (AAT)
    combined_data = pd.concat([combined_data, 
        get_Laliotis23_UCLES(f'{SYSTEM_HD}_Laliotis23_UCLES.csv')],
        ignore_index=True )
    # add PFS (Magellan)
    combined_data = pd.concat([combined_data, 
        get_Laliotis23_PFS(f'{SYSTEM_HD}_Laliotis23_PFS-Pre.csv')],
        ignore_index=True )
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # save compiled data file
    combined_data.to_csv(f'{SYSTEM_HD}_rv_main_unbinned.txt', sep='\t',
                         index=False, header=True)

    # nightly bin
    time, mnvel, errvel, tel = radvel.utils.bintels(
        combined_data['time'].values,
        combined_data['mnvel'].values,
        combined_data['errvel'].values,
        combined_data['tel'])
    bin_dict = {'time':time, 'mnvel':mnvel, 'errvel':errvel, 'tel':tel}

    # save binned data file
    data_all_bin = pd.DataFrame(data=bin_dict)
    data_all_bin.to_csv(f'{SYSTEM_HD}_rv_main_binned.txt', sep='\t',
                        index=False, header=True)

    return


def get_EBPS_HIRES(data_file):
    """Read in a .vels data file from the EBPS HIRES RV archive

    Args:
        data_file (str): path to .vels file

    Returns:
        pd.DataFrame: RV dataframe
    """

    # load file
    raw = pd.read_csv(data_file, sep='\s+', header=None, 
                      usecols=[0,1,2], names=['time', 'mnvel', 'errvel'])

    # new df
    new = pd.DataFrame()
    
    # separate PRE-upgrade (before Aug 18, 2004 = JD 2453236)
    hires_pre_msk = raw['time'] < 2_453_236
    hires_pre_data = raw.loc[
        hires_pre_msk, ['time', 'mnvel', 'errvel']]
    hires_pre_data['tel'] = 'HIRES-pre'
    new = pd.concat([new, hires_pre_data])
    
    # separate POST-upgrade (after Aug 18, 2004 = JD 2453236)
    hires_post_msk = raw['time'] >= 2_453_236
    hires_post_data = raw.loc[
        hires_post_msk, ['time', 'mnvel', 'errvel']]
    hires_post_data['tel'] = 'HIRES-post'
    new = pd.concat([new, hires_post_data])
    
    # order columns
    new = new[STD_COL_NAMES]

    return new


def get_RVBank_HARPS(data_file):
    """Read in a data file from the HARPS RVBank

    Args:
        data_file (str): path to .csv file

    Returns:
        pd.DataFrame: RV dataframe
    """

    # load file
    raw = pd.read_csv(data_file, index_col=0)
    
    # new df
    new = pd.DataFrame()
    
    # separate pre-upgrade (Trifonov et al. 2020)
    harps_pre_msk = raw['BJD'] <= 2_457_163 
    harps_pre_data = raw.loc[harps_pre_msk, 
                            ['BJD', 'RV_mlc_nzp', 'e_RV_mlc_nzp']]
    harps_pre_data['tel'] = 'HARPS-pre'
    harps_pre_data = harps_pre_data.rename(
        columns={'BJD':'time', 'RV_mlc_nzp':'mnvel', 'e_RV_mlc_nzp':'errvel'})
    new = pd.concat([new, harps_pre_data])
    
    # separate post-upgrade (Trifonov et al. 2020)
    harps_post_msk = raw['BJD'] >= 2_457_173 
    harps_post_data = raw.loc[harps_post_msk, 
                            ['BJD', 'RV_mlc_nzp', 'e_RV_mlc_nzp']]
    harps_post_data['tel'] = 'HARPS-post'
    harps_post_data = harps_post_data.rename(
        columns={'BJD':'time', 'RV_mlc_nzp':'mnvel', 'e_RV_mlc_nzp':'errvel'})
    new = pd.concat([new, harps_post_data])

    # order columns
    new = new[STD_COL_NAMES]
    
    return new


def get_Laliotis23_UCLES(data_file):
    """Read in UCLES data file from the Laliotis et al (2023)

    Args:
        data_file (str): path to .csv file

    Returns:
        pd.DataFrame: RV dataframe
    """    
     # load file
    raw = pd.read_csv(data_file, usecols=[1,2,3],
                      skiprows=1, names=['time', 'mnvel', 'errvel'])
    
    # new df
    new = raw.copy()
    
    # add tel
    new['tel'] = 'UCLES'
    
    # reorder columns
    new = new[STD_COL_NAMES]

    return new


def get_Laliotis23_PFS(data_file):
    """Read in PFS data file from the Laliotis et al (2023)

    Args:
        data_file (str): path to .csv file

    Returns:
        pd.DataFrame: RV dataframe
    """    
     # load file
    raw = pd.read_csv(data_file, usecols=[1,2,3],
                      skiprows=1, names=['time', 'mnvel', 'errvel'])
    
    # new df
    new = raw.copy()
    
    # add tel
    new['tel'] = 'PFS-Pre'
    
    # reorder columns
    new = new[STD_COL_NAMES]

    return new




########################################################################
########################################################################
# execute script

if __name__ == '__main__':
    data_setup()

########################################################################
########################################################################


