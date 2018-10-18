from .HashTable import HashTable

class Course():
    """
    Implements a Course data structure to be used within a Subject.    
    """
    def __init__(self, title, description, creds, reqs):
        self.title = title
        self.description = description
        self.credits = creds
        self.requisites = reqs

    def __repr__(self):
        return f"{{'title': {repr(self.title)}, 'description': {repr(self.description)}, 'credits': {repr(self.credits)}, 'requisites': {repr(self.requisites)}}}"
    
    def to_tuple(self):
        """
        Returns a tuple representation of the stored data.
        """
        return (self.title, self.description, self.credits)
        
# class Subject():
#     """
#     Implements a Subject data structure to be used in a Catalog.
#     """
#     def __init__(self, courses=HashTable(47)):
#         self.courses = courses

#     def __repr__(self):
#         return str(repr(self.courses))

#     def __len__(self):
#         return len(self.courses)


class Catalog():
    """
    Implements a Catalog for storing course data utilizing nested HashTables.
    """
    def __init__(self, subjects=HashTable(79)):        
        self.subjects = subjects

    def __repr__(self):
        return repr(self.subjects)

    def __len__(self):
        return len(self.subjects)

    def get_subject(self, subject):
        """
        Returns the subject data if it exists
        """        
        return self.subjects[subject]

    def get_subjects(self):
        """
        Returns a list of all subjects in the catalog
        """
        return list(self.subjects.keys()) # wrap in list to work dictionary objects

    def get_course(self, course):
        """
        Checks all subjects for the course, and returns the data if it finds it, else None
        """
        for subject in self.subjects.keys():
            if course in self.subjects[subject].keys():
                return self.subjects[subject][course]
        
        return None

    def get_courses(self, subject):
        """
        Returns a list of courses for a given subject
        """
        return list(self.subjects[subject].keys()) #wrap in list to work with dictionary objects
