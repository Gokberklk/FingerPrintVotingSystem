"""
Constants
"""

database_name = "Government"
path_of_image = "Real"
path_of_face = "Face"

#------------------------------TEST CASES FOR DATABASE--------------------------------------------#

citizen = [(11111111111, "Gökberk", "Lük", "1900-06-06", "Adana"),
           (22222222222, "Adem", "Garip", "1900-06-06", "Bursa"),
           (33333333333, "Canberk", "Sefa", "1900-06-06", "Bursa"),
           (44444444444, "Osman Eren", "Gündogdu", "1900-06-06", "Konya"),
           (55555555555, "Ata", "Öztaş", "1900-06-06", "Eskişehir")]

candidate = [(citizen[1][0],), (citizen[2][0],), (citizen[3][0],), (citizen[4][0],)]
candidate_election = [(0, citizen[1][0], 20241), (0, citizen[2][0], 20241), (0, citizen[3][0], 20242), (0, citizen[4][0], 20242)]
election = [(20241, "Null", "2024-06-07", "09:00:00","2024-06-08","10:00:00"), (20242, "Null", "2024-06-07", "09:00:00","2024-06-08","10:00:00")]


#------------------------------Finger Print Voting System--------------------------------------------#
