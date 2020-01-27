***


# Classifying the visibility of ID cards in photos

The folder images inside data contains several different types of ID documents taken in different conditions and backgrounds. The goal is to use the images stored in this folder and to design an algorithm that identifies the visibility of the card on the photo (FULL_VISIBILITY, PARTIAL_VISIBILITY, NO_VISIBILITY).

## Data

Inside the data folder you can find the following:

### 1) Folder images
A folder containing the challenge images.

### 2) gicsd_labels.csv
A CSV file mapping each challenge image with its correct label.
	- **IMAGE_FILENAME**: The filename of each image.
	- **LABEL**: The label of each image, which can be one of these values: FULL_VISIBILITY, PARTIAL_VISIBILITY or NO_VISIBILITY. 


## Dependencies

Create environment

```
./env_create.sh
```


Dwonload dependencies
```
./env_update.sh
```

## Run Instructions


Train Model
```
python main.py train model_v1
```

Predict on one image
```
python main.py predict image --model_path=/path/to/model    --image_path=/path/to/image
/GICSD_1_0_3.png
```

## Approach

[TODO: Complete this section with a brief summary of the approach]

## Future Work

[TODO: Complete this section with a set of ideas for future work]
