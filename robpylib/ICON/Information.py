# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 09:39:25 2019

@author: firo
"""

special_folders=['000_empty_frame',
                 '000_REF',
                 'bl1adjust',
                 'blackbody1',
                 'blackbody2',
                 'focus',
                 'test']

fabric_Folders=['009_50W_inline',
                '010_ref_inline',
                '011_30W_inline',
                '012_35W_inline',
                '013_40W_inline',
                '014_30W_ofline',
                '015_ref_offline',
                '016_40W_offline',
                '017_35W_offline',
                '036_40W_offline2',
                '037_30W_inline2']

yarn_Folders=['000_Sample_32_050_100_H',
              '002_32_200_100_H',
              '003_32_200_300_H',
              '004_32_200_025_H',
              '005_32_050_025_H',
              '006_32_500_025_H',
              '007_32_200_100_H2',
              '008_32_500_100_H',
              '038_32_500_300_H',
              '039_32_200_300_H2']

empty_strip={}
empty_strip['009_50W_inline']=[370,670]
empty_strip['010_ref_inline']=[348,348+344]
empty_strip['011_30W_inline']=[1440,1440+336]
empty_strip['012_35W_inline']=[1328,1328+448]
empty_strip['013_40W_inline']=[324,324+384]
empty_strip['014_30W_ofline']=[324,324+384]
empty_strip['015_ref_offline']=[1316,1316+424]
empty_strip['016_40W_offline']=[1326,1316+424]
empty_strip['017_35W_offline']=[1326,1316+424]
empty_strip['036_40W_offline2']=[1316,1316+472]
empty_strip['037_30W_inline2']=[1320,1316+472]

empty_strip['001_500_offline_II']=[1492,1492+268]
empty_strip['018_rand_I']=[336,336+304]
empty_strip['019_2000_inline_i']=[336,336+492]
empty_strip['020_1000_inline_i']=[1432,1432+340]
empty_strip['021_2000_offline']=[1432,1432+340]
empty_strip['022_1500_inline_i']=[1432,1432+340]
empty_strip['023_500_inline_i']=[332,332+348]
empty_strip['024_2000_inline_ii']=[1484,1484+288]
empty_strip['025_1500_offline_I']=[1484,1484+288]
empty_strip['026_1000_offline_i']=[1484,1484+288]
empty_strip['027_500_offline_i']=[1484,1484+288]
empty_strip['028_500_inline_ii']=[1489,1484+288]
empty_strip['029_1500_inline_ii']=[356,356+328]
empty_strip['030_rand_ii']=[356,356+288]
empty_strip['031_1000_inline_ii']=[1428,1428+352]
empty_strip['032_rand_iii']=[320,320+288]
empty_strip['033_1000_offline_ii']=[1536,1536+264]
empty_strip['034_1500_offline_ii']=[1416,1416+356]
empty_strip['035_1500_inline_iii']=[256,256+288]



espun_transition={
        '001': 44,
        '018': 1,#48,
        '019': 19,
        '020': 44,
        '021': 1, #49,
        '022': 22,
        '023': 32,
        '024': 1,#16,
        '025': 34,
        '026': 33,
        '027': 24,
        '028': 36,
        '029': 25,
        '030': 1, #26,
        '031': 1, #32,
        '032': 36,
        '033': 48,
        '034': 26,
        '035': 26
        }

espun_threshold={
        '001': 0.01,
        '018': 0,
        '019': 0.01,
        '020': 0.01,
        '021': 0,
        '022': 0.01,
        '023': 0.008,
        '024': 0,
        '025': 0.01,
        '026': 0.01,
        '027': 0.01,
        '028': 0.01,
        '029': 0.01,
        '030': 0,
        '031': 0.0125,
        '032': 0.0075,    
        '033': 0.01,
        '034': 0.01,
        '035': 0.01
        }


def espun_props(sample):
    if not sample[4]=='5':
        if not sample[4] == 'r':
            rpm=int(sample[4:8])
            orient=sample[9:12]
    if sample[4]=='5':
        rpm=500
        orient=sample[8:11]
    if sample[4]=='r':
        rpm=0
        orient='none'
    return rpm, orient


def get_flags(sample, special_folders=special_folders, fabric_Folders=fabric_Folders, yarn_Folders=yarn_Folders):
    breakflag=False
    fabricflag=False
    yarnflag=False
    for test in special_folders:
        if sample == test: breakflag=True
    for test in fabric_Folders:   #check if fast scan
        if sample == test: fabricflag=True
    for test in yarn_Folders:
        if sample == test: yarnflag=True
    return breakflag, fabricflag, yarnflag
    