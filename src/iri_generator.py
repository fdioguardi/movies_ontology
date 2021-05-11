class IRIGenerator(object):
    indexes = {}

    @classmethod
    def get_iri(cls, a_type):
        if a_type in cls.indexes.keys():
            cls.indexes[a_type] += 1
        else:
            cls.indexes[a_type] = 0

        return cls.indexes[a_type]
