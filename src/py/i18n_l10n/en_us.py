class LocalizationDictionaryEnUS:
    @staticmethod
    def get_dictionary():
        return {
            'D0001': 'Unit name may not be blank or whitespace only.',
            'D0002': 'Unit factor may not be zero.',
            'W0001': 'Vehicle has trailer but no articulation point was provided.'
                     'Articulation point assumed to be at back tip of vehicle.',
            'E0001': 'Vehicle model %%0 requested but not found in VehicleModelsCollection.',
            'E0002': 'XML File validation failed. File is not usable: %%0'
        }
