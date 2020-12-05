class LocalizationDictionaryEnUS:
    @staticmethod
    def get_dictionary():
        return {
            'D0001': 'Unit name may not be blank or whitespace only.',
            'D0002': 'Unit factor may not be zero.',
            'W0001': 'Vehicle has trailer but no articulation point was provided.'
                     'Articulation point assumed to be at back tip of vehicle.',
            'E0001': 'Vehicle model %%0 requested but not found in VehicleModelsCollection.',
            'E0002': 'XML File validation failed. File is not usable: %%0',
            'E0003': 'The archive must contain exactly one file with the following name fragment: %%0',
            'E0004': 'The parameter passed to a distribution must be in the range [0, 1). %%0 was passed.',
            'E0005': 'In distribution %%0, illegal value of %%1 was provided.',
            'E0006': 'In distribution %%0, the total of share occurrences must be greater than zero.',
        }
