# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 12:03:40 2019

@author: firo
"""


# samples with no processing errors


very_good_samples = ['T3_100_7_III',
                'T3_100_100_III',
                'T3_300_5',
                'T3_025_9',
                'T3_100_6',
                'T3_100_7',
                'T3_025_3_III',
                'T3_025_7_II',
                'T3_100_10',
                'T3_300_4',
                'T3_300_5',
                'T3_300_5_III',
                'T3_300_8_III',
                'T3_300_15'
                ]
	

# similar behavior can be observed also in definetly dry samples --> no influence of little and local acetone films?!	
questionable_sample = ['T3_300_9_III',       #wet with acetone
						'T3_100_4_III']     #wet with acetone

samples_to_repeat = ['T3_300_3',
                     'T3_025_1',
                     'T3_025_4',
                     'T3_025_9_III',
                     'T3_300_3']


good_samples = very_good_samples + questionable_sample


# last time step before registration fails
time_limit = {'T3_100_10_III': 344,
              'T3_300_5': 229,
              'T3_100_7': 206,
              'T3_100_10': 232}