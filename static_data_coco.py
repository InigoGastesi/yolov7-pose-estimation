def generation_info():
   return  {
        "description": "COCO 2017 Dataset",
        "url": "http:\/\/cocodataset.org",
        "version": "1.0",
        "year": 2017,
        "contributor": "COCO Consortium",
        "date_created": "2017\/09\/01"
    }
def generate_license():
   return  [
        {
            "url": "http:\/\/creativecommons.org\/licenses\/by-nc-sa\/2.0\/",
            "id": 1,
            "name": "Attribution-NonCommercial-ShareAlike License"
        },
        {
            "url": "http:\/\/creativecommons.org\/licenses\/by-nc\/2.0\/",
            "id": 2,
            "name": "Attribution-NonCommercial License"
        },
        {
            "url": "http:\/\/creativecommons.org\/licenses\/by-nc-nd\/2.0\/",
            "id": 3,
            "name": "Attribution-NonCommercial-NoDerivs License"
        },
        {
            "url": "http:\/\/creativecommons.org\/licenses\/by\/2.0\/",
            "id": 4,
            "name": "Attribution License"
        },
        {
            "url": "http:\/\/creativecommons.org\/licenses\/by-sa\/2.0\/",
            "id": 5,
            "name": "Attribution-ShareAlike License"
        },
        {
            "url": "http:\/\/creativecommons.org\/licenses\/by-nd\/2.0\/",
            "id": 6,
            "name": "Attribution-NoDerivs License"
        },
        {
            "url": "http:\/\/flickr.com\/commons\/usage\/",
            "id": 7,
            "name": "No known copyright restrictions"
        },
        {
            "url": "http:\/\/www.usa.gov\/copyright.shtml",
            "id": 8,
            "name": "United States Government Work"
        }
    ]
def generate_static_categories():
   return  [ 
            {       
                "supercategory": "person",
                "id": 1,
                "name": "person",
                "keypoints": [
                    "nose","left_eye","right_eye","left_ear","right_ear",
                    "left_shoulder","right_shoulder","left_elbow","right_elbow",
                    "left_wrist","right_wrist","left_hip","right_hip",
                    "left_knee","right_knee","left_ankle","right_ankle"
                ],
                "skeleton": [
                    [16,14],[14,12],[17,15],[15,13],[12,13],[6,12],[7,13],[6,7],
                    [6,8],[7,9],[8,10],[9,11],[2,3],[1,2],[1,3],[2,4],[3,5],[4,6],[5,7]
                ]
            }]