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
```

## Approach

I've used ResNet-18 for my detection. First I've made weighted dataset to fix the problem of 
the unbalanced dataset. Than created augmentation of the dataset Rescal and RandomCrop. 
There more augmentation can be provided like Gaussian Noise and RandomFlip. 
After this I've grayscaled the image and trained the network. 

## Future Work

Can be used and ensemble of the networks, like I've tried with DensNet and ResNet. 
In parallel they will do prediction and will give geometric mean for the prediction. Also 
another approach is to create a base model for the feature extraction and than 
train model on meta features. Another approach is to add Blending and KFold Split in the dataset.
All of these features may give boost to accuracy. 







### Upload functionality (videos) to EC2 (update all code the RPIS)   - fast
### Need to check bugs with starting the videos after detection (master is not stable)  - slow 
### Set min recodr thresohold to 5 mins for all RPIS      -  fast 
### Configuration need to be catched when we setup from the UI  - medium 
### Blinking leds and download and uploading  - medium 
### Make popup on the setting rpi config 
### Check the routes for logs and the buttons actions 