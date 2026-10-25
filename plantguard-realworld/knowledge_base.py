INFO = {
    'Tomato': {
        'Bacterial Spot': {          # FIX: missing tha
            'symptoms': [
                'Small dark water-soaked spots on leaves.',
                'Spots may have yellow halos around them.',
                'Lesions can turn brown and dry out over time.',
                'Severe infection causes leaf drop.',
                'Fruit may develop raised, scabby spots.'
            ],
            'prevention': 'Avoid overhead irrigation, use disease-free seedlings, sanitize tools, rotate crops, and apply copper-based bactericide if needed.',
            'description': 'Bacterial spot in tomato is caused by Xanthomonas bacteria and spreads rapidly in warm, wet conditions.'
        },
        'Early Blight': {
            'symptoms': [
                'Dark brown spots with concentric rings (target-like pattern).',
                'Yellowing often appears around older infected leaves.',
                'Usually starts on lower leaves and moves upward.',
                'Leaves dry out and may drop early.',
                'Stem lesions can appear in severe infection.'
            ],
            'prevention': 'Use disease-free seedlings, rotate crops, avoid frequent overhead irrigation, remove infected leaves, and apply recommended fungicide when needed.',
            'description': 'Early blight is a fungal disease commonly associated with Alternaria infection and is usually recognized by target-like lesions on older leaves.'
        },
        'Late Blight': {
            'symptoms': [
                'Water-soaked or greasy patches that quickly turn brown-black.',
                'Rapid spread during cool and wet weather.',
                'Whitish fungal growth may appear on leaf undersides in humid conditions.',
                'Leaves collapse quickly when disease becomes severe.',
                'Stem and fruit infection may also occur.'
            ],
            'prevention': 'Improve airflow, avoid leaf wetness, remove infected material quickly, and use preventive fungicide programs where appropriate.',
            'description': 'Late blight is a highly aggressive disease that can spread very fast in cool, humid weather.'
        },
        'Healthy': {
            'symptoms': [
                'Uniform green color across the leaf.',
                'No visible spots, lesions, mold, or yellow halo.',
                'Leaf edges and surface look normal.',
                'Strong and fresh texture is maintained.',
                'No major deformation or drying pattern.'
            ],
            'prevention': 'Continue balanced irrigation, proper nutrition, clean field hygiene, and regular crop monitoring.',
            'description': 'The tomato leaf appears healthy based on the model prediction.'
        }
    },
    'Potato': {
        'Early Blight': {
            'symptoms': [
                'Small dark lesions with concentric circles.',
                'Yellow tissue can surround the lesions.',
                'Older lower leaves are often affected first.',
                'Progressive drying and leaf death may occur.',
                'Severe infection reduces plant vigor.'
            ],
            'prevention': 'Rotate crops, use clean seed material, maintain field sanitation, and apply recommended fungicide if pressure is high.',
            'description': 'Potato early blight often appears as dry target-like spots and usually begins on older foliage.'
        },
        'Late Blight': {
            'symptoms': [
                'Irregular dark lesions that look water-soaked at first.',
                'Rapid blighting under humid and cool conditions.',
                'Leaf underside may show light fungal growth.',
                'Stems can darken and collapse.',
                'Disease can spread very quickly across plants.'
            ],
            'prevention': 'Use resistant material when available, reduce prolonged moisture, scout frequently, and destroy infected crop residue.',
            'description': 'Potato late blight is one of the most destructive potato diseases because of its fast spread.'
        },
        'Healthy': {
            'symptoms': [
                'Leaf color is uniformly green.',
                'No spotting, wilting, or lesion pattern is visible.',
                'Leaf shape and texture appear normal.',
                'No unusual yellowing or browning.',
                'Overall foliage looks vigorous.'
            ],
            'prevention': 'Maintain proper drainage, balanced nutrition, and routine inspection for early detection.',
            'description': 'The potato leaf appears healthy based on the model prediction.'
        }
    },
    'Bell Pepper': {
        'Bacterial Spot': {
            'symptoms': [
                'Small dark or water-soaked spots on leaves.',
                'Spots can appear angular because veins limit lesion expansion.',
                'Yellow halos may form around lesions.',
                'Leaves can tear or drop in severe infection.',
                'Fruit may develop raised scabby lesions.'
            ],
            'prevention': 'Avoid overhead irrigation, use clean seed/transplants, sanitize tools, and follow local bactericide guidance if needed.',
            'description': 'Bacterial spot is a common bell pepper disease and often shows angular leaf spotting with yellow halos.'
        },
        'Healthy': {
            'symptoms': [
                'Leaf surface is clean and evenly colored.',
                'No spot clusters or yellow halos are visible.',
                'Leaf edges look normal and undamaged.',
                'Texture appears fresh and firm.',
                'No major discoloration is present.'
            ],
            'prevention': 'Maintain clean irrigation practices, balanced fertility, and regular scouting.',
            'description': 'The bell pepper leaf appears healthy based on the model prediction.'
        }
    }
}


def get_disease_info(plant, disease):
    plant_info = INFO.get(plant, {})
    disease_info = plant_info.get(disease)
    if disease_info:
        return disease_info
    return {
        'symptoms': ['Detailed symptom mapping is not available for this result.'],
        'prevention': 'Follow good agricultural practices and consult a local extension expert if symptoms persist.',
        'description': 'Prediction completed.'
    }