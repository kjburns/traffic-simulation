class LocalizationDictionaryEnUS:
    @staticmethod
    def get_dictionary():
        return {
            'D0001': 'Unit name may not be blank or whitespace only.',
            'D0002': 'Unit factor may not be zero.',
            'W0001': 'Vehicle has trailer but no articulation point was provided.'
                     'Articulation point assumed to be at back tip of vehicle.',
            'W0002': 'One-sided truncation of normal distribution with mean of %%0 and standard deviation of %%1'
                     ' eliminates more than one quarter of the distribution.',
            'W0003': 'Two-sided truncation of normal distribution with mean of %%0 and standard deviation of %%1'
                     ' eliminates more than one half of the distribution.',
            'W0004': 'Acceleration function %%0 is not monotonic decreasing as a function of speed.',
            'W0005': 'Probability of max deceleration < 1 m/s^2 is greater than 0.01. (%%0)',
            'W0006': 'Desired acceleration/deceleration fraction %%0 should be monotonic increasing.',
            'W0007': 'Speed distribution %%0 should be monotonic increasing.',
            'E0001': 'Vehicle model %%0 requested but not found in VehicleModelsCollection.',
            'E0002': 'XML File validation failed. File is not usable: %%0',
            'E0003': 'The archive must contain exactly one file with the following name fragment: %%0',
            'E0004': 'The parameter passed to a distribution must be in the range [0, 1). %%0 was passed.',
            'E0005': 'In distribution %%0, illegal value of %%1 was provided.',
            'E0006': 'In distribution %%0, the total of share occurrences must be greater than zero.',
            'E0007': 'Max and min values of normal distribution %%0 are not simultaneously possible.',
            'E0008': 'In binned distribution %%0, there is an illegal discontinuity from %%1 to %%2.',
        }
