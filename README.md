# ProjectMUSEEG
✽ Welcome to Project MUSEEG! (Pronounced Muse-EGG) ✽ </br></br>
***Project A*** </br> 
*Music is already known to help with anxiety, focus, and relaxation—but what if it could be tailored to an individual’s brain activity? Brainwaves provide measurable indicators of emotional states like stress, restlessness, and calm. By collecting EEG data and training a neural network, I aim to create a system that detects these emotional states and generates personalized music designed to counteract them. The long-term goal is to explore applications in mental health, where this system could be used in hospitals, therapy settings, or for personal well-being. Since neurotechnology isn’t one-size-fits-all, this research is a step toward more personalized solutions in brain-music interaction.* </br></br>
***Project B***
*Ever wondered if someone could hear your thoughts? While we’re not at the point of translating thoughts into words, we can start by turning brain activity into music. Since music is a universal language, this research will explore how EEG data can be converted into sound patterns. By mapping electrical brain signals to musical structures, we lay the groundwork for future nonverbal communication systems. This could eventually evolve into a tool for individuals who struggle with verbal communication, but for now, the focus is on understanding the underlying brain-music relationship.* </br></br>
## Phase 1: Initial Research
*[Bibliography](https://docs.google.com/document/d/126_Q5-wPVYQXYX758TkZR0ndfYQ_7DFlI9uJoeaBVlY/edit?usp=sharing) of useful resources.*
## Phase 2: Hardware 
<div align="center">
<img src="README_IMGS/assembly.gif"/></div>

*Materials unboxing*
|------|

|Material Link                       | What's Included                                                                   | Cost                        |
| --------                           | -------                                                                           | -------                     |
| [Ultracortex "Mark IV" EEG Headset](https://shop.openbci.com/products/ultracortex-mark-iv?variant=23280741699)  | <ul><li> EEG nodes</li><li>Ear clips</li><li>Screws</li><li>Ribbon Cables</li></ul> |$900                         |
| [Daisy + Cyton BioSensing Board](https://shop.openbci.com/products/cyton-daisy-biosensing-boards-16-channel?variant=38959256526)    | <ul><li>Cyton+Daisy board (able to receive data from 16 different channels/points on brain)</li><li>Rechargeable Lithium Battery</li><li>Charging pack (for battery)</li><li>Programmable Dongle (Bluetooth communication)</li><li>Y-splitter cable</li><li>Board cover</li></ul> | $2100|
|[USB-A to USB-C Converter](https://www.bestbuy.com/site/insignia-usb-c-to-usb-adapter-black/6473492.p?skuId=6473492&extStoreId=46&utm_source=feed&ref=212&loc=18670532085&gad_source=1&gad_campaignid=18673989082&gbraid=0AAAAAD-ORIiROXi48bwZ1xsDqw0y9IgxL&gclid=Cj0KCQjwjo7DBhCrARIsACWauSmR3vUUhmtopa0tZ__U4yZM3AUu9UiuOb3mSAOf0FKv1AXDpcI0BTkaAo3EEALw_wcB&gclsrc=aw.ds) | <ul><li>USB-A to USB-C Converter</li></ul> | $10 |
|[Gorilla Glue](https://g.co/kgs/9oacW73) | <ul><li>Super Glue</li></ul>| $7 |

***Assembly of the headset is relatively simple, there are a few things to keep in mind:***
<ul><li>Assembly will take 24hrs+ because you will need to superglue in the inserts and wait for them to set overnight</li>
<li>ALWAYS make sure to check the polarity, ada fruit batteries only have one way to insert them so make sure the *red wire* aligns with the positive port and the the *black wire* aligns with the negative port when plugging into the Cyton board</li>
<li>The new design of the board covers/mounts does NOT have the three holes on either side, instead they are long oval shaped opening. They are helpful for custom positioning on to the EEG frame but a bit tricky to level. If you would like the original case, you can always 3D print it by using the <a href="https://github.com/openbci-archive/Docs/blob/master/assets/MarkIV/STL_Directory/M4%20Board_Mount.stl">STL provided on the OpenBCI website</a>.</li>
<li><a href="https://www.youtube.com/watch?v=S87FV-Q59F8">This assembly video</a> does not entirely follow the OpenBCI documentation, it has some inconsistencies with node placement and wire color cooridination. It also does not show how to connect the wires to the Cyton+Daisy boards. When I went through the assembly process the video was helpful for me to have a step by step, narrated assembly, but I did find myself using the <a href="https://docs.openbci.com/AddOns/Headwear/MarkIV/">documentation</a> and the <a href="https://docs.openbci.com/assets/images/1020-8a20d1014a755a8d1d968751ddc3b908.jpg">node placement 10-20 system diagram the most</a>.</li>
<li>I also have a mac with ONLY USB-C ports, and I could not find a source that explained what converter I needed for the bluetooth dongle. WIth some help from BestBuy, it is a USB-A without the protective casing. </li></ul>

***

![](README_IMGS/final.png)
*Finalized assembly of EEG Ultracortex Headset*
|------|

***

## Phase 3: Implementing Software
*connecting with the free OpenBCI Software*
*retrieving, and storing data*
# Project A: Musical Therapy
## Phase 4: Collecting Data (relevant to project)
*Note: I had trouble with loss of data packets when streaming via LSL, thank you William for helping me troubleshoot! Here is the forum post for reference: https://openbci.com/forum/index.php?p=/discussion/4075/confusion-on-lost-packets-could-be-a-software-issue#:~:text=connect%20to%20stream,proceed%20with%20the%20next%20stimuli.*
|------|

The first part is to detect a user's emotional state. For this project's phase I have decided to utilise the EmoEEG-MC dataset (completely open sourced) EEG data from 60 participants regarding their emotional state (eg. sadness, disgust, joy, fear, neutral, inpiration, and tenderness) when exposed to multimedia stimuli. There are a few missing entries and one missing EDF file, but for the most part the data is complete, the derivative files are completely intact. 

The files are large and take up quite a bit of processing power and GB, I downloaded 18 participants data to play around with different EEG preprocessing techniques. (I will soon add those files) *expand*

For the sake of having more data to train my model to detect emotions (which is very nuanced, and rely on purest form of emotion eg. data cannot be faked or duplicated with some data augmentation for fear of overfitting and incorrect detection) properly I will utilise the derivatives but process them so they match the settings of my headset and number of nodes. 

There are additional and extensive data sets from EEGs regarding emotion recognition the most prominent of which are housed at the Queen Mary University of London, however they are reserved for other Universities and research groups.

In my search of more data to properly train my model to detect emotions accurately I have two opetions, to collect more data from my headset and/or potentially combine with a different medium of detection. I have decided that I will be attemting to do both. I have collected data from subjects from stimulus videos from EmoStim Library. I have cleaned and determined my videos in the 1_exploring-emoStim.ipynb file and have created a full a experiment setup in 2_brainflow-collectingEEG.ipynb utilizing brainflow python library to collect EEG data during the segments when the stimulus videos are played and then save them as numpyArray files grouped under negative or positive EEG folders. After testing I also have participants rate their experiences with the following google form to better understand their emotional state through valence and arousal: https://forms.gle/pFkcQGueHi17YKBE8. I am now cleaning the data by applying bandpass filtering, normalizing, and cutting in segments for model training and will update once I have everything complete.

Additionaly, I will combine my model that detects emotion from EEG output with a model that can for the most part accurately detect emotions via live camera feed. 

I wanted to first learn about the principles of building a model for facial emotion recognition from scratch *expand* I will soon include my model which I trained on a Kaggle dataset and had about 60-70% accuracy in detection of emotions via photos. But to get optimal results I ended up using the DeepFace model and OpenCV library to access my webcam for live detection. 

End goal is to have a fusion neural network which is able to stack both models (emotion detection from EEG will have more weight since that is a purer form of emotion and cannot be faked, while the facial emotion recognition will supplement this). Hopefully this will result in overall more accurate model for emotion recognition. 
___

## Phase 5: Analyzing Data (relevant to project)
# Project B: Brain Wave to Music Interpretation
## Phase 4: Building a Simple Interpreter
While I will expand on the specifics later the workflow of the files under Project B are as follows, through the power of LSL we are able to transefer the processed live data from the OpenBCI GUI to VSCode/code editor of choice and then calling upon Garage Band/Music creation workflow of choice to play the sound. Brain waves have different frequencies and amplitudes just like music, so the way the program work is it takes a voltage and clips it to stay in the +100 to -100 micro-volt range and then scales it to play a note in the MiDi range. There are two different files--one for a single node, the otehr that plays all 16 nodes at once.  
## Phase 5: Expanding 
I found that Transformer models are best in music generation due to their ability of understanding context which is very crucial in creating fluid musical pieces. After doing a deep dive with videos from Velario Valrdo from the SOund of AI (here are my notes) I am playing around with filtering brainwaves and using them as inputs to RAVE to create complete musical compositions from snippets of EEG data. 


